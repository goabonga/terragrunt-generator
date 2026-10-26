#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Trusted GitHub automation; checked-out PR files are data, never executed.

Commands, by workflow:

- resign-signal / resign: ``validate-resign``, ``configure-signing``,
  ``rebase --mode resign``, ``push --mode resign``, ``cleanup``.
- auto-merge-signed: ``validate-merge``, ``queue``, ``wait``,
  ``configure-signing``, ``rebase --mode merge``, ``push --mode merge``,
  ``wait --signed``, ``merge``, ``cleanup``.
- dependabot-auto-merge: ``label-dependabot``.
- every workflow: ``summary``.
"""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote

RELEASE_BRANCH = "main"
# A pull request may target main, or the branch collecting the work of an
# issue, whose sub-issue branches merge into it before it reaches main.
ISSUE_BRANCH_PREFIX = "issue-"
MERGE_JOB_PREFIX = "merge into "
SIGNING_HOME_PREFIX = "ci-signing-"
MAJOR_UPDATE = "update-type: version-update:semver-major"
MAJOR_NOTICE = "<!-- dependabot-major-update -->"
ANNOUNCED_UPDATE = re.compile(
    r"^(?:Updates `([^`\s]+)`|Bumps \[([^\]\s]+)\]\([^)]*\)) from v?(\S+?) to v?(\S+?)\.?$",
    re.M,
)
MERGE_COMMANDS = {"validate-merge", "queue", "wait", "rebase", "push", "merge"}


def run(*args, **kwargs):
    return subprocess.check_output(args, **kwargs).decode().strip()


def git(*args):
    return run("git", *args)


def api(endpoint, method="GET", payload=None, paginate=False, token=None):
    command = ["gh", "api", endpoint, "--method", method]
    if paginate:
        command += ["--paginate"]
    options = {}
    if token is not None:
        if not token:
            raise ValueError("An explicit GitHub token must not be empty")
        options["env"] = {**os.environ, "GH_TOKEN": token}
    if payload is not None:
        command += ["--input", "-"]
        options["input"] = json.dumps(payload).encode()
    response = run(*command, **options)
    if paginate:
        # gh --paginate prints consecutive JSON documents. Decode each
        # complete page without depending on newer gh's --slurp flag.
        decoder = json.JSONDecoder()
        pages = []
        while response.strip():
            response = response.lstrip()
            page, offset = decoder.raw_decode(response)
            pages.append(page)
            response = response[offset:]
        return pages
    return json.loads(response) if response else None


def repository():
    value = os.environ["GH_REPO"]
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", value):
        raise ValueError("Invalid repository")
    return value


def pr_number():
    return int(os.environ.get("PR_NUMBER") or os.environ["PR"])


def pull_request():
    return api(f"repos/{repository()}/pulls/{pr_number()}")


def validate_head(sha, branch):
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("Invalid commit SHA")
    subprocess.run(["git", "check-ref-format", f"refs/heads/{branch}"], check=True)


def output(name, value):
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as stream:
        print(f"{name}={value}", file=stream)


def annotation(kind, message):
    """A GitHub Actions annotation; newlines are encoded so it stays one entry."""
    text = str(message).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::{kind}::{text}")


def pr_write_token():
    """The token pull request comments and label removals are written with."""
    token = os.environ.get("PR_WRITE_TOKEN")
    if not token:
        raise ValueError(
            "PR_WRITE_TOKEN is required to comment on or relabel the pull request"
        )
    return token


def mergeable_base(branch):
    """True for a branch pull requests may be merged into: main or an issue branch."""
    return branch == RELEASE_BRANCH or branch.startswith(ISSUE_BRANCH_PREFIX)


def base_branch():
    """The branch this run merges into, as recorded when the label was added."""
    base = os.environ.get("BASE_REF") or RELEASE_BRANCH
    if not mergeable_base(base):
        raise ValueError(f"The merge queue does not merge into {base}")
    return base


def open_pulls(branch):
    """The open pull requests whose head is ``branch`` of this repository."""
    owner = repository().split("/")[0]
    head = quote(f"{owner}:{branch}", safe="")
    pages = api(
        f"repos/{repository()}/pulls?state=open&head={head}&per_page=100",
        paginate=True,
    )
    return [
        pull
        for page in pages
        for pull in page
        if (pull["head"]["repo"] or {}).get("full_name") == repository()
        and pull["head"]["ref"] == branch
    ]


def commits_of(number):
    pages = api(
        f"repos/{repository()}/pulls/{number}/commits?per_page=100", paginate=True
    )
    return [commit for page in pages for commit in page]


def verified(commit):
    return bool((commit["commit"].get("verification") or {}).get("verified"))


def major_updates(text):
    """Dependencies whose leading version number changes in a Dependabot announcement."""
    majors = []
    for current, single, old, new in ANNOUNCED_UPDATE.findall(text):
        before, after = (re.match(r"\d+", version) for version in (old, new))
        if before and after and before.group() != after.group():
            majors.append(current or single)
    return majors


def dependabot_pull(pr):
    """A Dependabot pull request from this repository, opened against main."""
    return (
        pr["state"] == "open"
        and pr["user"]["login"] == "dependabot[bot]"
        and (pr["head"]["repo"] or {}).get("full_name") == repository()
        and pr["head"]["ref"].startswith("dependabot/")
        and pr["base"]["ref"] == RELEASE_BRANCH
    )


def add_merge_label(number):
    """Label with the merge PAT: a label added by the workflow token would not
    start auto-merge-signed, because GitHub does not chain its events."""
    api(
        f"repos/{repository()}/issues/{number}/labels",
        "POST",
        {"labels": [os.environ["MERGE_LABEL"]]},
    )


def token_owner():
    """The account behind GH_TOKEN, the maintainer's PAT, or ``None`` when it
    cannot tell (the workflow token cannot read /user)."""
    try:
        return api("user")["login"]
    except (subprocess.CalledProcessError, KeyError, TypeError):
        return None


def assign(number, login):
    if login:
        api(
            f"repos/{repository()}/issues/{number}/assignees",
            "POST",
            {"assignees": [login]},
        )


def label_dependabot():
    """Queue a Dependabot pull request for merging once CI passed on its signed head.

    Major updates are left for a maintainer, who approves one by adding the
    merge label; the pull request gets a notice saying so.
    """
    sha, branch = os.environ["RUN_HEAD_SHA"], os.environ["RUN_HEAD_BRANCH"]
    validate_head(sha, branch)
    pulls = [pull for pull in open_pulls(branch) if dependabot_pull(pull)]
    if len(pulls) != 1 or pulls[0]["head"]["sha"] != sha:
        print(
            "CI ran on a commit that is no longer the head of an open Dependabot pull request"
        )
        return
    pr = pulls[0]
    if any(label["name"] == os.environ["MERGE_LABEL"] for label in pr["labels"]):
        print(f"#{pr['number']} is already queued for merging")
        return
    commits = commits_of(pr["number"])
    if not commits or not all(verified(commit) for commit in commits):
        print(f"#{pr['number']} still has commits that are not rewritten and signed")
        return
    # The rewritten commits carry no body, so the pull request description,
    # which Dependabot writes and the rewrite leaves alone, tells majors apart.
    if major_updates(pr.get("body") or "") or any(
        MAJOR_UPDATE in commit["commit"]["message"] for commit in commits
    ):
        pages = api(
            f"repos/{repository()}/issues/{pr['number']}/comments?per_page=100",
            paginate=True,
        )
        if not any(
            MAJOR_NOTICE in comment["body"] for page in pages for comment in page
        ):
            api(
                f"repos/{repository()}/issues/{pr['number']}/comments",
                "POST",
                {
                    "body": f"{MAJOR_NOTICE}\nThis pull request contains a major update, so it is not merged "
                    f"automatically. Review it, then add the `{os.environ['MERGE_LABEL']}` label to merge "
                    "it through the signed merge queue."
                },
                token=pr_write_token(),
            )
            assign(pr["number"], token_owner())
        print(
            f"#{pr['number']} is a major update and waits for a maintainer's label"
        )
        return
    add_merge_label(pr["number"])
    print(f"#{pr['number']} queued for merging")


def merge_authorized(pr, sha):
    head = pr["head"]["ref"]
    return (
        pr["state"] == "open"
        and not pr["draft"]
        and (pr["head"]["repo"] or {}).get("full_name") == repository()
        and pr["head"]["sha"] == sha
        and head == os.environ["HEAD_REF"]
        and pr["base"]["ref"] == base_branch()
        # main only ever moves forward.
        and head != RELEASE_BRANCH
        and any(label["name"] == os.environ["MERGE_LABEL"] for label in pr["labels"])
    )


def check_labeller():
    login = quote(os.environ["LABELLER"], safe="")
    permission = api(f"repos/{repository()}/collaborators/{login}/permission")[
        "permission"
    ]
    if permission not in {"admin", "maintain", "write"}:
        raise ValueError("The labeller no longer has write access")


def validate_merge():
    validate_head(os.environ["HEAD_SHA"], os.environ["HEAD_REF"])
    if not os.environ.get("GH_TOKEN") or not os.environ.get("GPG_PRIVATE_KEY"):
        raise ValueError("Merge token and signing key are required")
    if not merge_authorized(pull_request(), os.environ["HEAD_SHA"]):
        raise ValueError("Pull request changed or merge authorization was removed")
    check_labeller()


def configure_signing():
    for name in (
        "GPG_PRIVATE_KEY",
        "PUSH_TOKEN",
        "GIT_USER_NAME",
        "GIT_USER_EMAIL",
        "GIT_SIGNING_KEY",
    ):
        if not os.environ.get(name):
            raise ValueError(f"Missing {name}")
    home = Path(
        tempfile.mkdtemp(prefix=SIGNING_HOME_PREFIX, dir=os.environ["RUNNER_TEMP"])
    )
    home.chmod(0o700)
    os.environ["GNUPGHOME"] = str(home)
    # Register cleanup before any import or key validation can fail.
    with Path(os.environ["GITHUB_ENV"]).open("a") as stream:
        print(f"GNUPGHOME={home}", file=stream)
    subprocess.run(
        ["gpg", "--batch", "--import"],
        input=os.environ["GPG_PRIVATE_KEY"].encode(),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "gpg",
            "--batch",
            "--list-secret-keys",
            os.environ["GIT_SIGNING_KEY"].rstrip("!"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    passphrase = home / "passphrase"
    passphrase.write_text(os.environ.get("GPG_PASSPHRASE", ""))
    passphrase.chmod(0o600)
    wrapper = home / "git-gpg"
    wrapper.write_text(
        "#!/usr/bin/env python3\nimport os, sys\n"
        "os.execvp('gpg', ['gpg', '--batch', '--pinentry-mode', 'loopback', "
        "'--passphrase-file', os.path.join(os.environ['GNUPGHOME'], 'passphrase'), *sys.argv[1:]])\n"
    )
    wrapper.chmod(0o700)
    for key, value in (
        ("user.name", os.environ["GIT_USER_NAME"]),
        ("user.email", os.environ["GIT_USER_EMAIL"]),
        ("user.signingkey", os.environ["GIT_SIGNING_KEY"]),
        ("gpg.program", str(wrapper)),
        ("commit.gpgsign", "true"),
        ("core.hooksPath", "/dev/null"),
    ):
        git("config", key, value)


def cleanup():
    home = Path(os.environ.get("GNUPGHOME", "/nonexistent"))
    root = Path(os.environ["RUNNER_TEMP"]).resolve()
    if (
        home.parent.resolve() == root
        and home.name.startswith(SIGNING_HOME_PREFIX)
        and not home.is_symlink()
    ):
        subprocess.run(["gpgconf", "--kill", "gpg-agent"], check=False)
        shutil.rmtree(home, ignore_errors=True)


def rebase(mode):
    git("config", "core.hooksPath", "/dev/null")
    if mode == "merge":
        git("fetch", "origin", base_branch())
        base = git("rev-parse", f"origin/{base_branch()}")
        Path(os.environ["RUNNER_TEMP"], "merge-base-sha").write_text(base)
    else:
        # Same base, same order: only the signatures and identity change.
        base = git("merge-base", f"origin/{resign_base()}", "HEAD")
    if git("rev-list", "--merges", f"{base}..HEAD"):
        raise ValueError("Merge commits cannot be automatically replayed")
    script = Path(__file__).with_name("sign_commit.py")
    subprocess.run(
        [
            "git",
            "rebase",
            "--force-rebase",
            "--empty=keep",
            base,
            "--exec",
            shlex.join(["python3", str(script)]),
        ],
        check=True,
    )


def authenticated_git(*args):
    subprocess.run(
        [
            "git",
            "-c",
            "credential.helper=",
            "-c",
            "credential.helper=!gh auth git-credential",
            *args,
        ],
        check=True,
    )


def push_signed(mode):
    sha = os.environ.get("EXPECTED_SHA") or os.environ["HEAD_SHA"]
    pr = pull_request()
    branch = os.environ["HEAD_REF"]
    validate_head(sha, branch)
    if mode == "merge":
        if not merge_authorized(pr, sha):
            raise ValueError("Pull request changed or merge authorization was removed")
    elif not (
        pr["state"] == "open"
        and (pr["head"]["repo"] or {}).get("full_name") == repository()
        and pr["head"]["sha"] == sha
        and pr["head"]["ref"] == branch
        and pr["base"]["ref"] == resign_base()
    ):
        raise ValueError("Pull request changed while its commits were re-signed")
    check_labeller()
    authenticated_git(
        "push",
        f"--force-with-lease=refs/heads/{branch}:{sha}",
        "origin",
        f"HEAD:refs/heads/{branch}",
    )
    if mode == "resign":
        api(
            f"repos/{repository()}/issues/{pr['number']}/comments",
            "POST",
            {
                "body": f"Re-signed the commits of `{branch}` with the maintainer key after an unsigned push "
                f"by `{os.environ['LABELLER']}`; checks run again on `{git('rev-parse', '--short', 'HEAD')}`."
            },
            token=pr_write_token(),
        )


def resign_base():
    """The base of the pull request being re-signed, decided by validate-resign."""
    base = os.environ["BASE_BRANCH"]
    if not mergeable_base(base):
        raise ValueError(f"Pull requests into {base} are not re-signed")
    return base


def validate_resign():
    """Decide whether a push to a pull request branch needs its commits re-signed.

    Only an open pull request from this repository, still at the pushed head,
    qualifies, and only when one of its commits is not verified: the signed
    push this workflow makes then triggers it again with nothing left to do.
    The pusher must have write access, the trust the merge label also asks for.
    """
    sha, branch = os.environ["SIGNAL_SHA"], os.environ["SIGNAL_BRANCH"]
    validate_head(sha, branch)
    pulls = [
        pull
        for pull in open_pulls(branch)
        if branch != RELEASE_BRANCH and mergeable_base(pull["base"]["ref"])
    ]
    if len(pulls) != 1 or pulls[0]["head"]["sha"] != sha:
        print("The pushed commit is no longer the head of an open pull request")
        output("needed", "false")
        return
    number = pulls[0]["number"]
    output("number", number)
    output("base", pulls[0]["base"]["ref"])
    unsigned = [
        commit["sha"][:7] for commit in commits_of(number) if not verified(commit)
    ]
    if not unsigned:
        print(f"Every commit of #{number} is signed")
        output("needed", "false")
        return
    check_labeller()
    print(f"#{number}: re-signing after unsigned commits " + ", ".join(unsigned))
    output("needed", "true")


def required_checks(base=None):
    """The status checks the active rulesets require before merging into ``base``.

    An issue branch has no ruleset of its own, so it requires what main does:
    the checks that would have to pass when the issue reaches main.
    """
    for branch in dict.fromkeys([base or base_branch(), RELEASE_BRANCH]):
        rules = api(f"repos/{repository()}/rules/branches/{quote(branch, safe='')}")
        checks = {
            check["context"]
            for rule in rules or []
            if rule["type"] == "required_status_checks"
            for check in rule["parameters"]["required_status_checks"]
        }
        if checks:
            return checks
    return set()


def checks_ready(runs, statuses, required):
    required = set(required)
    # A rerun supersedes older attempts with the same app and check name.
    latest = {}
    for check in runs:
        key = (check.get("app", {}).get("id"), check["name"])
        if key not in latest or check["id"] > latest[key]["id"]:
            latest[key] = check
    checks = [c for c in latest.values() if not c["name"].startswith(MERGE_JOB_PREFIX)]
    if any(
        c["status"] == "completed"
        and c["conclusion"] not in {"success", "neutral", "skipped"}
        for c in checks
    ):
        raise ValueError("A check failed")
    if statuses.get("statuses") and statuses["state"] in {"failure", "error"}:
        raise ValueError("A commit status failed")
    # Every required check must be reported, as the ruleset demands, and at
    # least one must have succeeded so a fully skipped run cannot merge.
    names = {c["name"]: c for c in checks}
    return (
        bool(required)
        and required <= names.keys()
        and any(names[name]["conclusion"] == "success" for name in required)
        and all(c["status"] == "completed" for c in checks)
        and (not statuses.get("statuses") or statuses["state"] == "success")
    )


def wait_checks(signed=False):
    token = os.environ.get("CHECKS_TOKEN")
    if not token:
        raise ValueError("CHECKS_TOKEN is required to read CI with the workflow token")
    sha = git("rev-parse", "HEAD") if signed else os.environ["HEAD_SHA"]
    required = required_checks()
    deadline = time.monotonic() + 25 * 60
    while time.monotonic() < deadline:
        pr = pull_request()
        if (
            signed
            and sha != os.environ["HEAD_SHA"]
            and pr["head"]["sha"] == os.environ["HEAD_SHA"]
        ):
            # GitHub updates the pull request head shortly after the signed push.
            time.sleep(5)
            continue
        if not merge_authorized(pr, sha):
            raise ValueError("Pull request changed while waiting for checks")
        pages = api(
            f"repos/{repository()}/commits/{sha}/check-runs?per_page=100&filter=latest",
            paginate=True,
            token=token,
        )
        runs = [c for page in pages for c in page["check_runs"]]
        statuses = api(f"repos/{repository()}/commits/{sha}/status", token=token)
        if checks_ready(runs, statuses, required):
            return
        time.sleep(30)
    raise TimeoutError("Timed out waiting for CI; re-apply the auto-merge label")


def queue_ahead(number, base=None):
    """Return the labelled pull requests queued before ``number``, oldest first.

    Only pull requests into the same base compete: each base moves on its own.
    The queue order is the time of each pull request's latest auto-merge label,
    so removing and re-applying the label moves a pull request to the back.
    """
    label = os.environ["MERGE_LABEL"]
    branch = quote(base or base_branch(), safe="")
    pages = api(
        f"repos/{repository()}/pulls?state=open&base={branch}&per_page=100",
        paginate=True,
    )
    queued = []
    for pull in (pull for page in pages for pull in page):
        if not any(item["name"] == label for item in pull["labels"]):
            continue
        events = api(
            f"repos/{repository()}/issues/{pull['number']}/events?per_page=100",
            paginate=True,
        )
        labelled = [
            event["created_at"]
            for page in events
            for event in page
            if event["event"] == "labeled"
            and (event.get("label") or {}).get("name") == label
        ]
        if labelled:
            queued.append((max(labelled), pull["number"]))
    order = [entry for _, entry in sorted(queued)]
    return order[: order.index(number)] if number in order else order


def pending_release(directory):
    """Return the components ``multicz plan`` would still bump on the latest main."""
    authenticated_git(
        "-C", str(directory), "fetch", "--quiet", "--tags", "--force", "origin", RELEASE_BRANCH
    )
    git("-C", str(directory), "checkout", "--quiet", "--detach", "FETCH_HEAD")
    plan = run("multicz", "plan", "--output", "json", cwd=directory)
    return sorted(json.loads(plan)["bumps"])


def wait_turn(poll=30, limit=5 * 60 * 60):
    """Wait until this pull request heads the queue and main has no pending release."""
    number, directory = pr_number(), Path(os.environ["QUEUE_DIR"])
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        if not merge_authorized(pull_request(), os.environ["HEAD_SHA"]):
            raise ValueError("Pull request changed or merge authorization was removed")
        ahead = queue_ahead(number)
        if ahead:
            print(
                "Waiting for "
                + ", ".join(f"#{entry}" for entry in ahead)
                + " ahead in the merge queue"
            )
        else:
            # Releases are cut from main only; an issue branch has none.
            pending = pending_release(directory) if base_branch() == RELEASE_BRANCH else []
            if not pending:
                print(f"First in the merge queue and {base_branch()} can move")
                return
            print(f"Waiting for the release of {', '.join(pending)} on {RELEASE_BRANCH}")
        time.sleep(poll)
    raise TimeoutError("Timed out waiting in the merge queue")


def delete_merged_branch(head, base):
    """Delete the merged head branch; a failure never fails the merge."""
    if head in {base, RELEASE_BRANCH}:
        return
    try:
        authenticated_git("push", "origin", "--delete", head)
    except subprocess.CalledProcessError:
        print(f"::warning::Could not delete the merged branch {head}")


def merge():
    sha = git("rev-parse", "HEAD")
    if not merge_authorized(pull_request(), sha):
        raise ValueError("Pull request changed or merge authorization was removed")
    check_labeller()
    base = base_branch()
    git("fetch", "origin", base)
    recorded = Path(os.environ["RUNNER_TEMP"], "merge-base-sha").read_text()
    if git("rev-parse", f"origin/{base}") != recorded:
        raise ValueError(f"{base} advanced; re-apply the auto-merge label")
    authenticated_git("push", "origin", f"HEAD:refs/heads/{base}")
    api(
        f"repos/{repository()}/issues/{pr_number()}/comments",
        "POST",
        {
            "body": f"Merged into `{base}` as `{sha}`, GPG-signed with the maintainer key. "
            "History stays linear."
        },
        token=pr_write_token(),
    )
    delete_merged_branch(os.environ["HEAD_REF"], base)


def summary(title, body=""):
    text = f"## {title}\n\n**Result:** {os.environ.get('JOB_STATUS', 'unknown')}\n"
    if "PR_NUMBER" in os.environ or "PR" in os.environ:
        number = os.environ.get("PR_NUMBER") or os.environ.get("PR") or "not validated"
        text += f"\nPull request: {number}\n"
    if os.environ.get("GIT_USER_NAME") or os.environ.get("GIT_USER_EMAIL"):
        name = os.environ.get("GIT_USER_NAME", "")
        email = os.environ.get("GIT_USER_EMAIL", "")
        text += f"\nIdentity: {name} <{email}>\n"
    if body:
        text += f"\n{body}\n"
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as stream:
        stream.write(text)


def command_actions(args):
    """Every command, by name; ``args`` is read only when one runs."""
    return {
        "validate-resign": validate_resign,
        "label-dependabot": label_dependabot,
        "validate-merge": validate_merge,
        "configure-signing": configure_signing,
        "cleanup": cleanup,
        "rebase": lambda: rebase(args.mode),
        "push": lambda: push_signed(args.mode),
        "wait": lambda: wait_checks(args.signed),
        "merge": merge,
        "queue": wait_turn,
        "summary": lambda: summary(args.title, args.body),
    }


def report_merge_failure(error):
    """Retrying is explicit: fix the problem, then re-apply the label.

    No PR code runs here, including when a rebase fails.
    """
    label = os.environ["MERGE_LABEL"]
    try:
        api(
            f"repos/{repository()}/issues/{pr_number()}/comments",
            "POST",
            {
                "body": f"auto-merge-signed: {error}. Fix the problem and re-apply the `{label}` label."
            },
            token=pr_write_token(),
        )
        api(
            f"repos/{repository()}/issues/{pr_number()}/labels/{quote(label, safe='')}",
            "DELETE",
            token=pr_write_token(),
        )
    except subprocess.CalledProcessError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=sorted(command_actions(None)))
    parser.add_argument("--mode", choices=["merge", "resign"], default="merge")
    parser.add_argument("--signed", action="store_true")
    parser.add_argument("--title", default="GitHub automation")
    parser.add_argument("--body", default="", help="Additional job summary text")
    args = parser.parse_args()
    try:
        command_actions(args)[args.command]()
    except (ValueError, TimeoutError, subprocess.CalledProcessError) as error:
        if args.mode == "merge" and args.command in MERGE_COMMANDS:
            report_merge_failure(error)
        # An expected failure is a clear annotation, never a traceback, and
        # never the output of a command, which may hold a token.
        if isinstance(error, subprocess.CalledProcessError):
            error = f"`{error.cmd[0]}` failed with exit status {error.returncode}"
        annotation("error", error)
        raise SystemExit(1) from None


if __name__ == "__main__":
    sys.exit(main())

# Stability and deprecation policy

This page is the contract between terragrunt-generator and its users about
what is part of the **public interface**, how it is versioned, and how long
it takes between announcing a deprecation and removing the deprecated
behavior.

## Public interface

terragrunt-generator is primarily a **command-line tool**. Its public
interface is:

- the `terragrunt-generator` CLI: its option names, defaults and the shape
  of the generated `terragrunt.hcl` / YAML output; and
- documented behavior described on this site.

The Python modules under `terragrunt_generator` are **implementation
details**. They may change at any time without notice; do not import them as
a library and rely on their signatures.

## Versioning

terragrunt-generator follows [Semantic Versioning](https://semver.org/).
Releases are automated from
[Conventional Commits](https://www.conventionalcommits.org/) by
[multicz](https://github.com/goabonga/multicz) — see
[CONTRIBUTING.md](https://github.com/goabonga/terragrunt-generator/blob/main/CONTRIBUTING.md#commit-messages)
for the commit-type → bump-level mapping.

## Deprecation lifecycle (n + 2 minors)

Removals of public CLI behavior are governed by the cycle below. It is
counted in **minor** versions. Letting `M` be the current major and `m` the
current minor:

| Version | What changes |
| --- | --- |
| **`M.m.*`** | The behavior exists. No warning. |
| **`M.(m+1).0`** | The behavior is **deprecated**. The announcement is a `deprecate: ...` commit (a custom Conventional Commits type registered in `multicz.toml` that bumps the minor and routes the entry into `### Deprecated` of `CHANGELOG.md`). The CLI emits a `DeprecationWarning`, the migration path is documented, and the behavior still works. |
| **`M.(m+2).0`** | The behavior is **removed**. The commit type is `remove: ...` (another custom multicz type that bumps the minor and routes to `### Removed`). Under the n+2 contract, a removal that respected the warning window is not a breaking change, so the major `M` does not change. |

- "n + 2" means **two minor releases between announcement and removal**.
  Patches (`M.m.z`) never deprecate or remove.
- The announcement and warning land in the release that introduces them.
- `feat!:` / `BREAKING CHANGE:` (a major bump) is reserved for changes that
  **bypass** the n+2 window — security fixes, or design errors that cannot
  wait two minor cycles.

### Exceptions

- **Security fixes** may change or remove behavior without the deprecation
  window. The release notes explain why and link to the advisory.
- **0.x releases** follow a relaxed cycle: semver allows breaking changes
  during the 0.x phase. The n+2 promise becomes binding at **v1.0**.

## Riding deprecations safely

Pin to the **minor**:

```toml
dependencies = [
    "terragrunt-generator ~= 1.3",   # accepts 1.3.x, rejects 1.4.x
]
```

Read `CHANGELOG.md` before every bump — every removal is listed under a
`Removed` section and back-references the original `Deprecated` entry.

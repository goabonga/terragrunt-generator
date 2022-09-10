from os.path import exists
from urllib.parse import urlparse


def is_local(url):
    url_parsed = urlparse(url)
    if url_parsed.scheme in ('file', ''):
        return exists(url_parsed.path)
    return False

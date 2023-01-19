import os

from urllib.parse import urlparse
from urllib.parse import unquote


def get_file_extension_from_url(url):
    filename = unquote(urlparse(url).path.split("/")[-1])
    return os.path.splitext(filename)[-1]
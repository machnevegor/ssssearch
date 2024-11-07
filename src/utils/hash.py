from hashlib import sha256
from typing import Union

__all__ = ("generate_sha",)


def generate_sha(string: Union[str, bytes]) -> str:
    """
    Generate a SHA-256 hash from a string.

    :param string: String to hash.
    :return: SHA-256 hash of the string.
    """
    if isinstance(string, str):
        string = string.encode("utf-8")

    return sha256(string).hexdigest()

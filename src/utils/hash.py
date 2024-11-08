from hashlib import sha256

__all__ = ("generate_sha",)


def generate_sha(string: str) -> str:
    """
    Generate a SHA-256 hash from a string.

    :param string: String to hash.
    :return: SHA-256 hash of the string.
    """
    return sha256(string.encode()).hexdigest()

"""
All hashing originates in this file for easier auditing.
"""
import hashlib


SECURE_HASH_ALGORITHM = hashlib.sha384
INSECURE_HASH_ALGORITHM = hashlib.md5


def secure_hash(string, algorithm) -> str:
    if isinstance(string, str):
        string = string.encode("utf-8")
    return SECURE_HASH_ALGORITHM(string).hexdigest()


def insecure_hash(string) -> str:
    if isinstance(string, str):
        string = string.encode("utf-8")
    return INSECURE_HASH_ALGORITHM(string).hexdigest()

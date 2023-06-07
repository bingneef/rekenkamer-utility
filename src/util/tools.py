import hashlib


def partition(pred, iterable):
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)

    return trues, falses


def hashed_filename(filename: str, to_hash_value: str) -> str:
    extension = filename.split(".")[-1]
    path_hash = hashlib.sha256(to_hash_value.encode("ascii")).hexdigest()[:8]

    return f"{filename.split('.')[0]} ({path_hash}).{extension}"

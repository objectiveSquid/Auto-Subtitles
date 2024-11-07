import zipfile


def unzip(zip_file: str, target: str) -> None:
    with zipfile.ZipFile(zip_file, "r") as zip_reference:
        zip_reference.extractall(target)

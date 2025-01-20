import json
from logging import getLogger
from tkinter import E
from typing import Any

logger = getLogger("FileHandler")


def write_to_file(data: object, filename: str) -> None:
    with open(filename, "w") as file:
        file.write(json.dumps(obj=data, indent=4))


def read_file(filename: str) -> Any:
    try:
        with open(filename, "r") as file:
            data: object = json.load(file)
        return data
    except Exception as e:
        logger.log(f"Error reading file: {e}")

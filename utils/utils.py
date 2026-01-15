"""
PRINTERS
"""

from enum import Enum

class PrintType(Enum):
    NONE = 0
    MESSAGE = 1
    INPUT = 2
    NOTICE = 3
    ERROR = 4

def print_log(*message: object, print_type: PrintType = PrintType.MESSAGE, end: str = "\n") -> None:
    if print_type == PrintType.MESSAGE:
        print("[ ]", end=": ")
    elif print_type == PrintType.INPUT:
        print("[?]", end=": ")
    elif print_type == PrintType.NOTICE:
        print("[!]", end=": ")
    elif print_type == PrintType.ERROR:
        print("ERR", end=": ")
    else:
        print("   ", end="  ")
    print(*message, end=end)

def print_line() -> None:
    print("=" * 50)
    return

"""
HELPER FUNCTIONS
"""

import hashlib, os, re
from pathlib import Path

def is_hex(string: str) -> bool:
    return bool(re.fullmatch(r"^[0-9a-fA-F]+$", string))

def is_sha256(string: str) -> bool:
    return is_hex(string) and len(string) == 64

def calculate_sha256(file_path: Path, chunk_size: int = 65536) -> str:
    file_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                data_chunk = f.read(chunk_size)
                if (not data_chunk):
                    break
                file_hash.update(data_chunk)
        return file_hash.hexdigest()
    except Exception as e:
        print_log(f"Error reading {file_path}: {e}", print_type=PrintType.ERROR)
        return ""

class FileInfo:
    def __init__(self, full_path: str, date: float, size: int, checksum: str) -> None:
        self.full_path = full_path
        self.date = date
        self.size = size
        self.checksum = checksum
    def __str__(self) -> str:
        return f"{self.full_path}, {self.date}, {self.size}, {self.checksum}"

def get_dir_info(directory: Path, is_verbose: bool = False, no_checksum: bool = False) -> tuple[dict[str, FileInfo], list[str]]:
    checksums: dict[str, FileInfo] = {}
    failed: list[str] = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = Path(root) / filename
            checksum = "0" if no_checksum else calculate_sha256(file_path)
            
            relative_path = file_path.relative_to(directory)
            full_path = file_path.resolve()
            
            if is_verbose:
                print_log(f"- {relative_path}... ", print_type=PrintType.NONE, end="")

            if checksum:
                if is_verbose:
                    print("DONE")
                checksums[str(relative_path)] = FileInfo(str(full_path), os.path.getmtime(full_path), os.path.getsize(full_path), checksum)
                continue
            else:
                if is_verbose:
                    print("FAILED")
                failed.append(str(full_path))
                
    return (checksums, failed)

def parse_dir_info_file(dir_info_file_path: Path | str) -> dict[str, FileInfo]:
    checksums: dict[str, FileInfo] = {}
    with open(dir_info_file_path, "r", encoding="utf-8") as fp:
        fp.readline()[len("FULL PATH: "):]
        for line in fp:
            full_path_str = fp.readline()[6:].rstrip()
            relative_path_str = fp.readline()[6:].rstrip()
            checksum = fp.readline()[6:].rstrip()
            date_modified_str = fp.readline()[6:].rstrip()
            size_str = fp.readline()[6:].rstrip()
            if not (
                full_path_str 
                and relative_path_str 
                and checksum
                and date_modified_str
                and size_str
            ):
                break
            
            if (not is_sha256(checksum)):
                print_log(f"Checksums file ({dir_info_file_path}) is malformed: '{checksum}' is not a valid SHA256 checksum string.", print_type=PrintType.ERROR)
                break
            
            try:
                date_modified = float(date_modified_str)
            except Exception:
                print_log(f"Checksums file ({dir_info_file_path}) is malformed: '{date_modified_str}' is not a valid float.", print_type=PrintType.ERROR)
                break
            
            try:
                size = int(size_str)
            except Exception:
                print_log(f"Checksums file ({dir_info_file_path}) is malformed: '{size_str}' is not a valid integer.", print_type=PrintType.ERROR)
                break
            
            try:
                curr_file_path = Path(relative_path_str)
                # full_file_path = Path (full_path_str)
                checksums[str(curr_file_path)] = FileInfo(full_path_str, date_modified, size, checksum)
            except Exception as e:
                print_log(f"Checksums file ({dir_info_file_path}) is malformed: {e}", print_type=PrintType.ERROR)
                break
    return checksums
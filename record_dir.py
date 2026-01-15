import sys, os
from pathlib import Path
import uuid
import argparse

from utils.utils import print_line, print_log, PrintType, calculate_sha256, get_dir_info

def main(source_dir: str, is_verbose: bool, output_dir: str) -> int:
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    if (not os.path.isdir(source_path)): 
        print_log("Invalid SOURCE path provided: Directory does not exist or is not a directory.", print_type=PrintType.ERROR)
        return 1
    if (not os.path.isdir(output_path)): 
        print_log("Invalid LOG OUTPUT path provided: Directory does not exist or is not a directory.", print_type=PrintType.ERROR)
        return 1

    print_log(f"Checksums of files inside \"{source_path.name}\" will be checked.", print_type=PrintType.NOTICE)
    
    print_log(f"Calculating checksums in source directory...")
    source_checksums, failed_checksums = get_dir_info(source_path, is_verbose)
    print_log("Done!", print_type=PrintType.NOTICE)
    
    output_filename = f"{source_path.name} - {uuid.uuid4().hex[:10]}.txt"
    print_log(f"Saving checksums to \"{output_filename}\"...")
    with open(f"{output_path / output_filename}", "a", encoding="utf-8") as fp:
        fp.write(f"FULL PATH: {source_path.resolve()}\n")
        idx = 0
        for relative_path, file_info in source_checksums.items():
            idx += 1
            fp.write(f"----- FILE #{idx} -----\n")
            fp.write(f"FULL: {file_info.full_path}\nPART: {relative_path}\nS256: {file_info.checksum}\nDATE: {file_info.date}\nSIZE: {file_info.size}\n")
    print_log("Done!", print_type=PrintType.NOTICE)
    print()

    print_line()
    print("SUMMARY:")
    print(f"   - Total files processed:    {len(source_checksums)}")
    if failed_checksums:
        print()
        print(f"AN ERROR OCCURED WHILE EVALUATING CHECKSUMS FOR THE FOLLOWING FILES:")
        for failed in failed_checksums:
            print(f"   - {failed}")
    print_line()
    
    print()
    print_log("All Done!", print_type=PrintType.NOTICE)
    print()
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="record_dir.py",
        description="Records all identifying information about a specified directory and its contents to a local text file.",
        allow_abbrev=False,
    )
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("-d", "--debug", help="output all arguments (does nothing)", action="store_true")
    parser.add_argument("-o", "--output", help="path to the directory where the output log will be saved", nargs="?", default=".")
    # parser.add_argument("-o", dest="output", help="path to the directory where the output will be saved", nargs="?", default=".")
    parser.add_argument("path", help="path to the target directory")
    
    args = parser.parse_args()
        
    source_dir: str = args.path
    is_verbose: bool = args.verbose
    output_dir: str = args.output
    
    if args.debug:
        for key, value in args.__dict__.items():
            print_log(f"{key.upper()}: {value}")
        sys.exit(0)
    
    sys.exit(main(source_dir, is_verbose, output_dir))
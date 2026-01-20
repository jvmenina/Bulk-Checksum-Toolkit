import sys, os, time, argparse
from pathlib import Path
# from tqdm import tqdm

from utils.utils import print_line, print_log, PrintType, calculate_sha256, parse_dir_info_file, get_dir_info

def main(source: str, external_dir: str, no_checksum: bool) -> int:
    source_path = Path(source)
    source_is_a_file = os.path.isfile(source_path)
    external_path = Path(external_dir)
    if (not source_is_a_file and not os.path.isdir(source_path)): 
        print_log("Invalid SOURCE path provided: Directory/File does not exist or is not a directory/file.", print_type=PrintType.ERROR)
        return 1
    if (not os.path.isdir(external_path)):
        print_log("Invalid EXTERNAL path provided: Directory does not exist or is not a directory.", print_type=PrintType.ERROR)
        return 1

    print_log("Relevant file info inside the following will be checked:", print_type=PrintType.NOTICE)
    if (source_is_a_file):
        print_log(f"- Source (FILE):   {source_path}", print_type=PrintType.NONE)
    else:
        print_log(f"- Source:          {source_path}", print_type=PrintType.NONE)
    print_log(f"- External:        {external_path}", print_type=PrintType.NONE)
    
    print_log(f"Processing files in source directory...")
    if (source_is_a_file):
        source_info = parse_dir_info_file(source_path)
        source_failed: list[str] = []
    else:
        source_info, source_failed = get_dir_info(source_path, no_checksum=no_checksum)
    print_log("Done!", print_type=PrintType.NOTICE)
    
    print_log(f"Processing files in external directory...")
    external_info, external_failed = get_dir_info(external_path, no_checksum=no_checksum)
    print_log("Done!", print_type=PrintType.NOTICE)

    print_log("Comparing file information...")
    all_files = set(source_info.keys()) | set(external_info.keys())
    
    matching: list[str] = []
    mismatches: list[str] = []
    only_in_source: list[str] = []
    only_in_external: list[str] = []
    
    for file_path in all_files:
        source_file_info = source_info.get(file_path)
        external_file_info = external_info.get(file_path)
        
        if source_file_info and external_file_info:
            if (
                no_checksum
                and (
                    source_file_info.size != external_file_info.size
                    or source_file_info.date != external_file_info.date
                )
            ):
                mismatches.append(file_path)
            elif (
                not no_checksum
                and source_file_info.checksum != external_file_info.checksum
            ):
                mismatches.append(file_path)
            else:
                matching.append(file_path)
        elif source_file_info and not external_file_info:
            only_in_source.append(file_path)
        elif external_file_info and not source_file_info:
            only_in_external.append(file_path)
        else:
            print_log(f"Unknown error: File path ({file_path}) cannot be found in generated list of files:", print_type=PrintType.ERROR)
    print_log("Done!", print_type=PrintType.NOTICE)
    print()

    print_line()
    print("RESULTS ")
    print_line()
    print("MISMATCHING FILES:")
    if mismatches:
        for file in mismatches:
            source_diff_info = f"'{time.ctime(source_info[file].date)}', '{source_info[file].size} B'" if no_checksum else source_info[file].checksum
            external_diff_info = f"'{time.ctime(external_info[file].date)}', '{external_info[file].size} B'" if no_checksum else external_info[file].checksum
            print(f"    |--> {file}")
            print(f"    |    Source:   {source_diff_info}")
            print(f"    |    External: {external_diff_info}")
    else:
        print("    (none)")
        
    print()
    
    print(f"FILES ONLY IN SOURCE:")
    if only_in_source:
        for file in only_in_source:
            print(f"    |--> {file}")
    else:
        print("    (none)")
        
    print()
    
    print(f"FILES ONLY IN EXTERNAL:")
    if only_in_external:
        for file in only_in_external:
            print(f"    |--> {file}")
    else:
        print("    (none)")
        
    if source_failed or external_failed:
        print("AN ERROR OCCURED WHILE EVALUATING CHECKSUMS FOR THE FOLLOWING FILES:")
    
    if source_failed:
        for file in source_failed:
            print(f"    |--> [SOURCE] {file}")
    if external_failed:
        for file in external_failed:
            print(f"    |--> [EXTERNAL] {file}")
            

    print_line()
    print("SUMMARY:")
    print(f"   - Total files in source:   {len(source_info)}")
    print(f"   - Total files in external: {len(external_info)}")
    print(f"   - Matching files:          {len(matching)}")
    print(f"   - Mismatched files:        {len(mismatches)}")
    print(f"   - Only in source:          {len(only_in_source)}")
    print(f"   - Only in external:        {len(only_in_external)}")
    if source_failed or external_failed:
        print(f"   - Failed checks:           {len(source_failed)+len(external_failed)}")
    print_line()
    print()
    
    if mismatches or only_in_source or only_in_external:
        print_log("(WARNING) Source and external directories are NOT identical!", print_type=PrintType.NOTICE)
        print_log("All Done!", print_type=PrintType.NOTICE)
        return 1
    else:
        print_log("Source and external directories are identical.", print_type=PrintType.NOTICE)
        print_log("All Done!", print_type=PrintType.NOTICE)
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="compare_dirs.py",
        description="Calculates checksums of all files between two directories and compares the directories for any differences.",
        allow_abbrev=False,
    )
    parser.add_argument("-x", "--no-checksum", help="use date modified and size instead of checksums", action="store_true")
    parser.add_argument("source", help="path to the source directory or a file containing checksums")
    parser.add_argument("external_dir", help="path to the external directory")
    args = parser.parse_args()
        
    source: str = args.source
    external_dir: str = args.external_dir
    no_checksum: bool = args.no_checksum
    
    sys.exit(main(source, external_dir, no_checksum))
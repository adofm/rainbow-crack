#!/usr/bin/env python3

import sys
import os
import argparse
import logging
import time
from datetime import datetime
from rainbowtable import RainbowTable

def format_time(seconds):
    """Format time in a human-readable foramat"""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("hash_string", help="hash to crack")
        parser.add_argument("rainbow_table_file", 
                          help="name of file containing a valid rainbow table (generated from rainbowgen.py)")
        args = parser.parse_args()

        # Display input parameters
        print("\n[+] Cracking Parameters:")
        print(f"    Hash to crack: {args.hash_string}")
        print(f"    Rainbow table: {args.rainbow_table_file}")

        # Verify hash format
        try:
            int(args.hash_string, 16)
        except ValueError:
            print("\n[-] Error: Invalid hash format. Hash must be in hexadecimal format.")
            sys.exit(1)

        # Check if rainbow table file exists
        if not os.path.exists(args.rainbow_table_file):
            print(f"\n[-] Error: Rainbow table file '{args.rainbow_table_file}' not found.")
            sys.exit(1)

        print("\n[+] Loading rainbow table...")
        start_time = time.time()
        try:
            rt = RainbowTable.load_from_file(args.rainbow_table_file)
            load_time = time.time() - start_time
            print(f"    Table loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            print(f"\n[-] Error loading rainbow table: {str(e)}")
            sys.exit(1)

        # Display table information
        print("\n[+] Rainbow Table Information:")
        print(f"    Algorithm: {rt.algorithm}")
        print(f"    Chain Length: {rt.chain_length}")
        print(f"    Number of Chains: {rt.number_of_chains}")
        print(f"    Password Length Range: {rt.min_length} - {rt.max_length}")

        print("\n[+] Starting crack attempt...")
        crack_start_time = time.time()
        
        psw = rt.lookup(args.hash_string)
        
        crack_time = time.time() - crack_start_time

        if psw is not None:
            print("\n[+] Success! Password found:")
            print(f"    Hash: {args.hash_string}")
            print(f"    Password: {psw}")
            print(f"    Time taken: {format_time(crack_time)}")
        else:
            print("\n[-] No match found")
            print(f"    Time taken: {format_time(crack_time)}")
            print("\nPossible reasons for no match:")
            print("  • Password not in the rainbow table's charset")
            print("  • Password length outside the table's range")
            print("  • Hash collision occurred")
            print("  • Rainbow table coverage insufficient")

        total_time = time.time() - start_time
        print(f"\n[+] Total execution time: {format_time(total_time)}")

    except KeyboardInterrupt:
        print("\n[-] Cracking interrupted by user")
        sys.exit(1)
    except Exception as e:
        print (f"\n[-] Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
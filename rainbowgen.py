#!/usr/bin/env python3

import sys
import os
import argparse
import logging
import time
from datetime import datetime
from rainbowtable import RainbowTable

#prasanth
def setup_logging():
    """Configure logging settings"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'{log_dir}/rainbow_generator_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_file

def validate_arguments(args):
    """Validate command line arguments"""
    if args.min_length > args.max_length:
        raise ValueError("Minimum length cannot be greater than maximum length")
    
    if args.min_length < 1:
        raise ValueError("Minimum length must be at least 1")
    
    if args.chain_length < 1:
        raise ValueError("Chain length must be at least 1")
    
    if args.number_of_chains < 1:
        raise ValueError("Number of chains must be at least 1")
    
    if args.algorithm.lower() not in ['sha1', 'md5']:
        raise ValueError("Algorithm must be either 'sha1' or 'md5'")
#jeevan
def estimate_memory_usage(args):
    """Estimate memory usage based on input parameters"""
    avg_length = (args.min_length + args.max_length) / 2
    estimated_bytes = args.number_of_chains * (avg_length + 20)  # 20 bytes for hash
    return estimated_bytes

def print_configuration(args):
    """Print configuration details"""
    logging.info("Rainbow Table Generator Configuration:")
    logging.info("-" * 40)
    logging.info(f"Algorithm: {args.algorithm}")
    logging.info(f"Charset: {args.charset}")
    logging.info(f"Password Length Range: {args.min_length} - {args.max_length}")
    logging.info(f"Chain Length: {args.chain_length}")
    logging.info(f"Number of Chains: {args.number_of_chains}")
    logging.info(f"Output File: {args.output_file}")
    logging.info("-" * 40)

def check_output_file(filename):
    """Check if output file already exists and handle accordingly"""
    if os.path.exists(filename):
        response = input(f"File {filename} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            logging.info("Operation cancelled by user")
            sys.exit(0)
#karthik
def main():
    try:
        # Set up argument parser with more detailed help messages
        parser = argparse.ArgumentParser(
            description="Rainbow Table Generator Tool",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
            "algorithm",
            help="Hash algorithm to use (sha1 or md5)",
            type=str
        )
        parser.add_argument(
            "charset",
            help="Character set name (must be defined in config.ini)",
            type=str
        )
        parser.add_argument(
            "min_length",
            help="Minimum length of passwords to generate",
            type=int
        )
        parser.add_argument(
            "max_length",
            help="Maximum length of passwords to generate",
            type=int
        )
        parser.add_argument(
            "chain_length",
            help="Length of each chain in the rainbow table",
            type=int
        )
        parser.add_argument(
            "number_of_chains",
            help="Number of chains to generate",
            type=int
        )
        parser.add_argument( # Add a new argument for specifying the output file
            "output_file",
            help="Name of the output file",
            type=str
        )
        
        args = parser.parse_args()
        
        # Set up logging
        log_file = setup_logging()
        logging.info(f"Log file: {log_file}")
        
        # Validate arguments
        validate_arguments(args)
        
        # Estimate memory usage
        estimated_bytes = estimate_memory_usage(args)
        logging.info(f"Estimated memory usage: {estimated_bytes / (1024 * 1024):.2f} MB")
        
        # Print configuration
        print_configuration(args)
        
        # Check output file
        check_output_file(args.output_file)
        
        # Create RainbowTable instance
        rt = RainbowTable(args.algorithm, args.charset, args.min_length, args.max_length, args.chain_length, args.number_of_chains)
        
        # Generate rainbow table
        start_time = time.time()
        rt.generate_table()
        end_time = time.time()
        logging.info(f"Rainbow table generation took {end_time - start_time:.2f} seconds")
        
        # Save to file
        rt.save_to_file(args.output_file)
        logging.info(f"Rainbow table saved to {args.output_file}")
        
    except Exception as e:
        logging.error(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
# Rainbow Table Hash Cracker

## Overview

The Rainbow Table Hash Cracker is a command-line tool designed to crack hashed passwords using precomputed rainbow tables. This tool leverages the efficiency of rainbow tables to quickly find the original password corresponding to a given hash.

## Features

- Supports cracking of hexadecimal formatted hashes.
- Loads rainbow tables generated from `rainbowgen.py`.
- Displays detailed information about the loaded rainbow table.
- Provides human-readable execution time for operations.
- Handles errors gracefully with informative messages.

## Requirements

- Python 3.x
- Required libraries:
  - `argparse`
  - `os`
  - `sys`
  - `time`
  - `datetime`
  - `rainbowtable` (custom module)

## Installation

1. Clone the repository:
   ``` bash git clone https://github.com/yourusername/rainbow-table-hash-cracker.git cd rainbow-table-hash-cracker ```

2. Ensure you have the required libraries installed. You may need to install the rainbowtable module if it's not included in your environment.

## Usage
To use the Rainbow Table Hash Cracker, run the following command in your terminal:
```python3 hash_cracker.py <hash_value> <rainbow_file>```
## Example
```python3 rainbowgen.py sha1 alphanumeric 1 6 20 1000 test_table.rt```
```python3 rainbowcrack.py "4fb2e5324b31c12a116e11a0885d184bcf0cc0fc" test_table.rt```

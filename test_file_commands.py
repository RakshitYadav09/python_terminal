#!/usr/bin/env python3

# Test the updated AI parser with file listing commands
import sys
import os
sys.path.append(os.path.dirname(__file__))

from terminal.ai_parser import parse_nl

def test_file_commands():
    test_cases = [
        "show all python files",
        "show python files", 
        "list all python files",
        "find python files",
        "show all files",
        "what files are here"
    ]
    
    print("=== Testing File Listing Commands ===")
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test}'")
        result = parse_nl(test)
        print(f"   Output: {result}")

if __name__ == "__main__":
    test_file_commands()
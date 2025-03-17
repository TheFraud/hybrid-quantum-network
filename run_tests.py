#!/usr/bin/env python3
import pytest
import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    # Add the project root to PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    exit_code = pytest.main([
        'tests',
        '-v',
        '--disable-warnings',
        '-s'
    ])
    sys.exit(exit_code)


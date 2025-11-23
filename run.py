#!/usr/bin/env python
"""
Convenience script to run dev-standup without needing to type the full module path.
Usage: python run.py [OPTIONS]
"""

import sys
from dev_standup.cli import main

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import os
import sys
from lib import scanner

if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    scanner(sys.argv[1])
else:
    scanner()

#!/usr/bin/env python3

import os
import sys
from lib import scanner

if os.path.exists(sys.argv[1]):
    scanner(sys.argv[1])
else:
    scanner()

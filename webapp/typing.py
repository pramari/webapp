"""
Cheat Sheet
https://www.pythonsheets.com/notes/python-typing.html
"""

import re

from typing import Pattern, Set  # Dict, Optional, Set

url: Pattern = re.compile("(https?)://([^/\r\n]+)(/[^\r\n]*)?")
method: Set[str] = {"GET", "POST"}

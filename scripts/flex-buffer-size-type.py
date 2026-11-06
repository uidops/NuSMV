#!/usr/bin/env python
"""Print the C type of the `size` parameter of yy_create_buffer().

Depending on its version (and on distribution patches), flex declares

    YY_BUFFER_STATE yy_create_buffer(FILE *file, int size);        /* e.g. 2.5.x, OpenBSD */
    YY_BUFFER_STATE yy_create_buffer(FILE *file, yy_size_t size);  /* e.g. macOS */

The hand-written parser headers re-declare the prefixed function, and must
agree with the scanner flex generates, or C compilers report
"conflicting types". This runs FLEX on a minimal scanner and reports the type
it uses: `int`, or `size_t` (which yy_size_t is a typedef of).
"""

import re
import subprocess
import sys
import tempfile

from pathlib import Path

SCANNER = "%option noyywrap\n%%\n.|\\n ;\n%%\n"

PROTOTYPE = re.compile(
    r"yy_create_buffer\s*\(\s*FILE\s*\*\s*\w+\s*,\s*(\w+)\s+\w+\s*\)")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} FLEX", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "probe.l"
        src.write_text(SCANNER)
        out = subprocess.run(
            [sys.argv[1], "-t", str(src)],
            check=True, capture_output=True, text=True,
        ).stdout
    match = PROTOTYPE.search(out)
    if match is None:
        print("cannot find yy_create_buffer() in the generated scanner",
              file=sys.stderr)
        return 1
    ctype = match.group(1)
    print("size_t" if ctype == "yy_size_t" else ctype)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Pins the colours the GPU rendered into the fixtures of generated packages.

usage: python bless.py <packages-dir> <test-output-file>

Reads `every_package_probe_holds` failures ("<id>: <label>\\n  expected [...]
\\n  rendered [...]") and rewrites that probe's `expect` line - only in the
packages this generator wrote (generated.txt), never a hand-made one.
"""

import os
import re
import sys

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated.txt")


def fmt(x):
    x = float(x)
    if x == 0:
        return "0"
    s = f"{x:.5g}"
    return s


def main():
    root, log = sys.argv[1], sys.argv[2]
    mine = set(open(LEDGER).read().split())
    text = open(log, encoding="utf-8", errors="replace").read()
    pattern = re.compile(r"(concat\.[a-z0-9-]+): ([^\n]+)\n\s+expected \[[^\]]*\]\n\s+rendered \[([^\]]*)\]")
    fixed = 0
    skipped = set()
    for pid, label, got in pattern.findall(text):
        slug = pid[len("concat."):]
        if slug not in mine:
            skipped.add(pid)
            continue
        values = [fmt(v) for v in got.split(",")]
        if any(v in ("NaN", "nan", "inf", "-inf") for v in values):
            print(f"{pid}: {label}: rendered {got} - not pinned")
            continue
        path = os.path.join(root, pid, "fixtures.toml")
        src = open(path, encoding="utf-8").read()
        blocks = src.split("[[probe]]")
        for i, block in enumerate(blocks):
            if re.search(r'^name = "' + re.escape(label) + '"$', block, re.M):
                blocks[i] = re.sub(r"^expect = \[.*\]$", "expect = [" + ", ".join(values) + "]", block, flags=re.M)
                fixed += 1
                break
        open(path, "w", encoding="utf-8", newline="\n").write("[[probe]]".join(blocks))
    print(f"pinned {fixed} probes")
    if skipped:
        print("failing in packages not generated here:", ", ".join(sorted(skipped)))


if __name__ == "__main__":
    main()

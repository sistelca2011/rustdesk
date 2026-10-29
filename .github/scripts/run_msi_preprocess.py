#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper to invoke res/msi/preprocess.py with Sistelca ARP metadata without
PowerShell / Win32 command-line quote-escaping pitfalls.
"""

import json
import pathlib
import subprocess
import sys


def main() -> int:
    msi_dir = pathlib.Path(__file__).resolve().parents[2] / "res" / "msi"
    preprocess_py = msi_dir / "preprocess.py"
    custom_arp = json.dumps(
        {
            "Contact": {"msi": "ARPCONTACT", "v": "https://sistelca2011.com"},
            "HelpLink": {"msi": "ARPHELPLINK", "v": "https://sistelca2011.com"},
            "ReadMe": {"msi": "ARPREADME", "v": "https://sistelca2011.com"},
        }
    )
    cmd = [
        sys.executable,
        str(preprocess_py),
        "--arp",
        "--custom",
        "--app-name",
        "Sistelca",
        "-m",
        "Sistelca",
        "--custom-arp",
        custom_arp,
        "-d",
        "../../rustdesk",
    ]
    return subprocess.call(cmd, cwd=str(msi_dir))


if __name__ == "__main__":
    sys.exit(main())

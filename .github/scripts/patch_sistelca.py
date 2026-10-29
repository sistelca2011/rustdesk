#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patches the checked-out libs/hbb_common submodule so all compiled binaries
connect exclusively to Sistelca's own RustDesk OSS server and use Sistelca branding.
"""

import pathlib
import sys

SERVER_HOST = "soporte.sistelca2011.com"
SERVER_PUB_KEY = "S4Ta6ePKuvedUQ1R+f7tDcHoTja+sP5xaFxo5b5wkl0="
CUSTOM_APP_NAME = "Sistelca"


def apply_exact_replacement(content: str, old: str, new: str, label: str) -> str:
    if new in content and old not in content:
        print(f"[patch_sistelca] Already patched: {label}")
        return content
    count = content.count(old)
    if count != 1:
        print(
            f"[patch_sistelca] ERROR: Expected exactly 1 match for {label}, found {count}.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"[patch_sistelca] Patched: {label}")
    return content.replace(old, new, 1)


def main() -> None:
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    config_rs = repo_root / "libs" / "hbb_common" / "src" / "config.rs"

    if not config_rs.is_file():
        print(
            f"[patch_sistelca] ERROR: Submodule file not found: {config_rs}",
            file=sys.stderr,
        )
        sys.exit(1)

    text = config_rs.read_text(encoding="utf-8")

    # 1. Force PROD_RENDEZVOUS_SERVER (overrides any cached RustDesk2.toml servers)
    text = apply_exact_replacement(
        text,
        'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new("".to_owned());',
        f'pub static ref PROD_RENDEZVOUS_SERVER: RwLock<String> = RwLock::new("{SERVER_HOST}".to_owned());',
        "PROD_RENDEZVOUS_SERVER",
    )

    # 2. Set APP_NAME to Sistelca on Windows/Android/iOS while preserving Linux/macOS service bundle IDs
    app_name_replacement = (
        '#[cfg(any(target_os = "macos", target_os = "linux"))]\n'
        '    pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());\n'
        '    #[cfg(not(any(target_os = "macos", target_os = "linux")))]\n'
        f'    pub static ref APP_NAME: RwLock<String> = RwLock::new("{CUSTOM_APP_NAME}".to_owned());'
    )
    text = apply_exact_replacement(
        text,
        'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
        app_name_replacement,
        "APP_NAME",
    )

    # 3. Replace public RENDEZVOUS_SERVERS list
    text = apply_exact_replacement(
        text,
        'pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
        f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{SERVER_HOST}"];',
        "RENDEZVOUS_SERVERS",
    )

    # 4. Replace public RS_PUB_KEY (used by both rendezvous and peer verification)
    text = apply_exact_replacement(
        text,
        'pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
        f'pub const RS_PUB_KEY: &str = "{SERVER_PUB_KEY}";',
        "RS_PUB_KEY",
    )

    config_rs.write_text(text, encoding="utf-8", newline="\n")
    print(f"[patch_sistelca] Successfully patched {config_rs}")


if __name__ == "__main__":
    main()

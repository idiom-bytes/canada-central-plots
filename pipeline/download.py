"""
Download StatCan bulk CSV files to pipeline/lake/.

Usage: python pipeline/download.py
"""
import os
import sys
import urllib.request
import zipfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import SOURCES, STATCAN_URL, LAKE_DIR


def download_table(table_id: str, description: str) -> bool:
    """Download and extract a StatCan table CSV."""
    # StatCan uses the table ID without dashes in the zip filename
    table_clean = table_id.replace("-", "")
    out_dir = os.path.join(LAKE_DIR, table_id)
    zip_path = os.path.join(LAKE_DIR, f"{table_id}.zip")

    # Skip if already downloaded
    csv_path = os.path.join(out_dir, f"{table_clean}.csv")
    if os.path.exists(csv_path):
        print(f"  [skip] {table_id} already downloaded")
        return True

    url = STATCAN_URL.format(table_id=table_clean)
    print(f"  [download] {table_id}: {description}")
    print(f"    URL: {url}")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                shutil.copyfileobj(resp, f)

        # Extract
        os.makedirs(out_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(out_dir)

        # Clean up zip
        os.remove(zip_path)
        print(f"    -> extracted to {out_dir}")
        return True

    except Exception as e:
        print(f"    [ERROR] Failed to download {table_id}: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return False


def main():
    os.makedirs(LAKE_DIR, exist_ok=True)
    print("=== Downloading StatCan data ===\n")

    success = 0
    failed = 0

    for table_id, info in SOURCES.items():
        if download_table(table_id, info["description"]):
            success += 1
        else:
            failed += 1

    print(f"\nDone: {success} downloaded, {failed} failed")
    if failed:
        print("WARNING: Some downloads failed. Check errors above.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

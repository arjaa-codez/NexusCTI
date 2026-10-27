"""Downloader for authentic cyber threat intelligence datasets:
1. MITRE ATT&CK Enterprise STIX 2.1 (groups, malware, techniques, relationships)
2. CISA Known Exploited Vulnerabilities (KEV) Catalog (exploited CVEs in the wild)
"""
import os
import sys
import time
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data" / "external_datasets"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "cisa_kev.json": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "enterprise_attack.json": "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json",
}

def download_file(url: str, dest_path: Path):
    print(f"[Download] Fetching: {url} -> {dest_path.name}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NexusCTI-Research/1.0"}
    req = urllib.request.Request(url, headers=headers)
    
    start_time = time.time()
    with urllib.request.urlopen(req, timeout=120) as response, open(dest_path, "wb") as out_file:
        total_size = response.getheader("Content-Length")
        if total_size:
            total_size = int(total_size)
            print(f"           Total size: {total_size / (1024 * 1024):.2f} MB")
        
        downloaded = 0
        block_size = 65536
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            out_file.write(buffer)
            downloaded += len(buffer)
            
    elapsed = time.time() - start_time
    mb = downloaded / (1024 * 1024)
    print(f"[Download] Finished {dest_path.name}: {mb:.2f} MB in {elapsed:.1f}s ({mb/max(elapsed, 0.1):.2f} MB/s)")

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 65)
    print("NEXUS-CTI: FETCHING AUTHENTIC REAL-WORLD CTI DATASETS")
    print("=" * 65)
    
    for filename, url in DATASETS.items():
        dest = DATA_DIR / filename
        if dest.exists() and dest.stat().st_size > 100000:
            print(f"[Download] Skipping existing {filename} ({dest.stat().st_size / (1024 * 1024):.2f} MB)")
            continue
        try:
            download_file(url, dest)
        except Exception as e:
            print(f"[Download Error] Failed to fetch {filename}: {e}")
            raise e

    print("=" * 65)
    print("ALL REAL SCIENTIFIC DATASETS DOWNLOADED SUCCESSFULLY")
    print("=" * 65)

if __name__ == "__main__":
    main()

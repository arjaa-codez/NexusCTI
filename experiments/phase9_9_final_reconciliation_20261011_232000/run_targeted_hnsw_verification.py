import hashlib
import json
import os
import shutil
import struct
import sys
import gc
from pathlib import Path

# Paths
CAE_ROOT = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine")
MASTER_DIR = CAE_ROOT / "data" / "chroma_db"
EXP_DIR = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\experiments\phase9_9_final_reconciliation_20261011_232000")
TEMP_DIR = EXP_DIR / "scratch" / "targeted_hnsw_verification_temp"

sys.path.insert(0, str(CAE_ROOT))

def compute_dir_manifest(directory: Path):
    manifest = {}
    for p in sorted(directory.rglob("*")):
        if p.is_file():
            rel = p.relative_to(directory).as_posix()
            with open(p, "rb") as f:
                content = f.read()
            manifest[rel] = {
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest()
            }
    return manifest

def main():
    print("=" * 80)
    print("NEXUSCTI — TARGETED HNSW VERIFICATION EXECUTION")
    print("=" * 80)

    # 1. Record pre-run master manifest
    print("\n--- STEP 1: RECORDING PRE-RUN MASTER MANIFEST ---")
    pre_manifest = compute_dir_manifest(MASTER_DIR)
    for rel, meta in pre_manifest.items():
        print(f"  {rel:<60} {meta['size']:>8} bytes  sha256={meta['sha256']}")

    # 2. Direct structural inspection of master HNSW files
    print("\n--- STEP 2: DIRECT STRUCTURAL INSPECTION OF MASTER HNSW FILES ---")
    segment_dir = MASTER_DIR / "3962f896-273d-4039-b97e-d0aa4e6d29ed"
    header_path = segment_dir / "header.bin"
    length_path = segment_dir / "length.bin"
    data0_path = segment_dir / "data_level0.bin"
    links_path = segment_dir / "link_lists.bin"

    with open(header_path, "rb") as f:
        hdr = f.read()

    # Unpack header exactly according to chromadb_rust_bindings layout:
    # 0..3: uint32 version
    # 4..11: uint64 reserved/num_deleted
    # 12..19: uint64 max_elements_
    # 20..27: uint64 cur_element_count
    # 28..35: uint64 size_data_per_element_
    # 36..43: uint64 size_links_per_element_
    # 44..51: uint64 offset_data_
    # 52..55: int32 enterpoint_node_
    # 56..59: int32 max_level_
    # 60..67: uint64 M_
    # 68..75: uint64 maxM0_
    # 76..83: uint64 maxM_
    # 84..91: double mult_
    # 92..99: uint64 ef_construction_
    version = struct.unpack("<I", hdr[0:4])[0]
    reserved = struct.unpack("<Q", hdr[4:12])[0]
    max_elements = struct.unpack("<Q", hdr[12:20])[0]
    cur_element_count = struct.unpack("<Q", hdr[20:28])[0]
    size_data_per_element = struct.unpack("<Q", hdr[28:36])[0]
    size_links_per_element = struct.unpack("<Q", hdr[36:44])[0]
    offset_data = struct.unpack("<Q", hdr[44:52])[0]
    enterpoint_node = struct.unpack("<i", hdr[52:56])[0]
    max_level = struct.unpack("<i", hdr[56:60])[0]
    M = struct.unpack("<Q", hdr[60:68])[0]
    maxM0 = struct.unpack("<Q", hdr[68:76])[0]
    maxM = struct.unpack("<Q", hdr[76:84])[0]
    mult = struct.unpack("<d", hdr[84:92])[0]
    ef_construction = struct.unpack("<Q", hdr[92:100])[0]

    header_info = {
        "header_file_size": len(hdr),
        "version": version,
        "reserved": reserved,
        "max_elements": max_elements,
        "cur_element_count": cur_element_count,
        "size_data_per_element": size_data_per_element,
        "size_links_per_element": size_links_per_element,
        "offset_data": offset_data,
        "enterpoint_node": enterpoint_node,
        "max_level": max_level,
        "M": M,
        "maxM0": maxM0,
        "maxM": maxM,
        "mult": mult,
        "ef_construction": ef_construction
    }

    for k, v in header_info.items():
        print(f"  {k:<25}: {v}")

    # Inspect length.bin
    length_size = length_path.stat().st_size
    print(f"\n  length.bin size          : {length_size} bytes (capacity = {length_size // 4} ints)")

    # Inspect data_level0.bin
    data0_size = data0_path.stat().st_size
    print(f"  data_level0.bin size     : {data0_size} bytes (expected = {max_elements} * {size_data_per_element} = {max_elements * size_data_per_element})")

    # Inspect link_lists.bin
    links_size = links_path.stat().st_size
    print(f"  link_lists.bin size      : {links_size} bytes")

    # Conclusion on structural validity of 0-byte link_lists.bin
    # In Chroma's HNSW format, link_lists.bin exclusively stores link lists for levels >= 1.
    # When max_level == -1 (or 0), no levels >= 1 exist, so zero link lists exist for upper layers.
    # Therefore, link_lists.bin having 0 bytes is mathematically and structurally mandatory.
    is_valid_0byte = (links_size == 0) and (max_level == -1 or max_level == 0)
    print(f"\n  -> link_lists.bin 0-byte validity: {is_valid_0byte} (max_level={max_level})")

    # 3. Create disposable temporary copy
    print("\n--- STEP 3: CREATING DISPOSABLE RUNTIME SNAPSHOT ---")
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(MASTER_DIR, TEMP_DIR)
    print(f"  Cloned master store to: {TEMP_DIR}")

    # Verify copy integrity
    copy_manifest = compute_dir_manifest(TEMP_DIR)
    for rel, meta in pre_manifest.items():
        assert rel in copy_manifest, f"Missing file in copy: {rel}"
        assert copy_manifest[rel]["sha256"] == meta["sha256"], f"Hash mismatch in copy: {rel}"
    print("  Copy manifest verification: 100% BIT-FOR-BIT MATCH")

    # 4. Load with actual installed ChromaDB runtime and execute representative queries
    print("\n--- STEP 4: LOADING DISPOSABLE COPY & RUNNING RETRIEVAL QUERIES ---")
    import chromadb
    from chromadb.api.client import SharedSystemClient

    client = chromadb.PersistentClient(path=str(TEMP_DIR))
    collection = client.get_collection("cti_threat_reports")
    count = collection.count()
    print(f"  Collection loaded successfully: 'cti_threat_reports' (count = {count})")
    assert count == 7, f"Expected count == 7, got {count}"

    test_queries = [
        "SolarWinds Orion supply chain backdoor SUNBURST DLL memory injection",
        "Industroyer2 malware substation IEC 60870-5-104 grid outage Ukraine",
        "AppleJeus cryptocurrency exchange trojan macOS Lazarus Group",
        "Volt Typhoon living-off-the-land PowerShell wmic critical infrastructure",
        "FIN7 Carbanak syndicate POS malware financial retail hospitality"
    ]

    retrieval_results = []
    for q in test_queries:
        res = collection.query(query_texts=[q], n_results=3)
        top_id = res["ids"][0][0]
        top_dist = res["distances"][0][0] if res["distances"] else None
        top_meta = res["metadatas"][0][0]
        actor = top_meta.get("threat_actor")
        retrieval_results.append({
            "query": q,
            "top_id": top_id,
            "threat_actor": actor,
            "distance": top_dist
        })
        print(f"  Query: '{q[:50]}...' -> Actor: {actor} (dist: {top_dist:.4f})")

    # 5. Clean up disposable copy
    print("\n--- STEP 5: TEARDOWN AND CLEANUP OF DISPOSABLE COPY ---")
    del collection
    del client
    SharedSystemClient.clear_system_cache()
    gc.collect()
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print(f"  Temporary snapshot removed: {not TEMP_DIR.exists()}")

    # 6. Record post-run master manifest and assert zero delta
    print("\n--- STEP 6: VERIFYING MASTER IMMUTABILITY (PRE/POST DELTA) ---")
    post_manifest = compute_dir_manifest(MASTER_DIR)
    delta_found = False
    for rel, meta in pre_manifest.items():
        if rel not in post_manifest:
            print(f"  DELETED: {rel}")
            delta_found = True
        elif post_manifest[rel]["sha256"] != meta["sha256"]:
            print(f"  MODIFIED: {rel} (pre: {meta['sha256']}, post: {post_manifest[rel]['sha256']})")
            delta_found = True
        elif post_manifest[rel]["size"] != meta["size"]:
            print(f"  SIZE CHANGED: {rel}")
            delta_found = True

    for rel in post_manifest:
        if rel not in pre_manifest:
            print(f"  NEW FILE: {rel}")
            delta_found = True

    if not delta_found:
        print("  Master immutability verification: ZERO DELTA DETECTED (Pre == Post)")
    else:
        print("  CRITICAL FAILURE: Master files modified!")

    # Overall verdict
    verdict = "PASS" if (is_valid_0byte and count == 7 and len(retrieval_results) == 5 and not delta_found) else "FAIL"
    print("\n" + "=" * 80)
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 80)

    # Save verification output to JSON for report generation
    out_data = {
        "verdict": verdict,
        "is_valid_0byte": is_valid_0byte,
        "header_info": header_info,
        "length_size": length_size,
        "data0_size": data0_size,
        "links_size": links_size,
        "retrieval_results": retrieval_results,
        "master_pre_manifest": pre_manifest,
        "master_post_manifest": post_manifest,
        "delta_found": delta_found
    }

    with open(EXP_DIR / "targeted_hnsw_verification_results.json", "w") as f:
        json.dump(out_data, f, indent=2)

if __name__ == "__main__":
    main()

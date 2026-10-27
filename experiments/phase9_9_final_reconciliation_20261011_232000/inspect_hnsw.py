import struct
import os
from pathlib import Path

MASTER_DIR = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db")
SEGMENT_DIR = MASTER_DIR / "3962f896-273d-4039-b97e-d0aa4e6d29ed"

header_path = SEGMENT_DIR / "header.bin"
length_path = SEGMENT_DIR / "length.bin"
data0_path = SEGMENT_DIR / "data_level0.bin"
links_path = SEGMENT_DIR / "link_lists.bin"

print(f"Header size: {header_path.stat().st_size}")
print(f"Length size: {length_path.stat().st_size}")
print(f"Data0 size: {data0_path.stat().st_size}")
print(f"Links size: {links_path.stat().st_size}")

with open(header_path, "rb") as f:
    header_bytes = f.read()

print(f"Header hex ({len(header_bytes)} bytes): {header_bytes.hex()}")

# Let's inspect integers in header_bytes
# Typically HNSW headers in hnswlib or Chroma Rust:
# Let's unpack 4-byte and 8-byte ints:
print("Header as 32-bit unsigned ints (little endian):")
for i in range(0, len(header_bytes) - 3, 4):
    val = struct.unpack("<I", header_bytes[i:i+4])[0]
    print(f"  offset {i:2d}: {val} (0x{val:08x})")

print("Header as 64-bit unsigned ints (little endian):")
for i in range(0, len(header_bytes) - 7, 8):
    val = struct.unpack("<Q", header_bytes[i:i+8])[0]
    print(f"  offset {i:2d}: {val} (0x{val:016x})")

with open(length_path, "rb") as f:
    length_bytes = f.read()

print(f"\nLength hex (first 64 bytes): {length_bytes[:64].hex()}")
print(f"Total ints in length.bin ({len(length_bytes)} bytes / 4 = {len(length_bytes)//4}):")
length_ints = [struct.unpack("<I", length_bytes[i:i+4])[0] for i in range(0, len(length_bytes), 4)]
print(f"Values in length.bin: {length_ints}")

# Also check as 64-bit:
length_qwords = [struct.unpack("<Q", length_bytes[i:i+8])[0] for i in range(0, len(length_bytes), 8)]
print(f"Values in length.bin as 64-bit ints ({len(length_qwords)} elements): {length_qwords[:20]}")

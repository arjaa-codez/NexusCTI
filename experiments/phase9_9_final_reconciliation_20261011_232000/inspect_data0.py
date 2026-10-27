import struct
from pathlib import Path

MASTER_DIR = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db")
SEGMENT_DIR = MASTER_DIR / "3962f896-273d-4039-b97e-d0aa4e6d29ed"

data0_path = SEGMENT_DIR / "data_level0.bin"
with open(data0_path, "rb") as f:
    raw = f.read()

print(f"data_level0.bin size: {len(raw)} bytes")
elem_size = 1676 # from header.bin

# Inspect all 7 elements
for i in range(7):
    offset = i * elem_size
    chunk = raw[offset:offset+elem_size]
    # In hnswlib data_level0:
    # offset 0..131: link list at level 0
    # first 2 or 4 bytes is link count
    cnt_u16 = struct.unpack("<H", chunk[:2])[0]
    cnt_u32 = struct.unpack("<I", chunk[:4])[0]
    
    # Let's inspect the links
    # If cnt_u16 or cnt_u32 is link count:
    # Let's unpack the first 16 bytes:
    links_u32 = struct.unpack("<4I", chunk[:16])
    
    # Vector starts at offset 132 (1536 bytes = 384 floats)
    vec_floats = struct.unpack("<4f", chunk[132:132+16])
    
    # Label is at offset 1668 (8 bytes)
    label = struct.unpack("<Q", chunk[1668:1668+8])[0]
    
    print(f"Element {i}:")
    print(f"  Level-0 header bytes: {chunk[:8].hex()} | u32 count: {cnt_u32} | links: {links_u32[1:]}")
    # print all links up to cnt_u32
    if cnt_u32 < 32:
        all_links = [struct.unpack("<I", chunk[4+j*4:8+j*4])[0] for j in range(cnt_u32)]
        print(f"  All {cnt_u32} Level-0 neighbors: {all_links}")
    print(f"  First 4 floats of 384d vector: {vec_floats}")
    print(f"  Label (ID in SQLite): {label}")

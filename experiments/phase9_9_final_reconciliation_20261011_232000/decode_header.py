import struct
from pathlib import Path

MASTER_DIR = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db")
SEGMENT_DIR = MASTER_DIR / "3962f896-273d-4039-b97e-d0aa4e6d29ed"

header_file = SEGMENT_DIR / "header.bin"
with open(header_file, "rb") as f:
    hdr = f.read()

print(f"Header length: {len(hdr)} bytes")

# Let's inspect the fields in header.bin
# We know:
# offset 84: mult_ = 0.36067376022224085 (which is 1 / ln(16), corresponding to M = 16)
# Let's unpack with various offsets:
# Let's examine every 8 bytes as uint64, int64, and double:
for i in range(0, len(hdr), 8):
    chunk = hdr[i:i+8]
    if len(chunk) < 8:
        chunk = chunk.ljust(8, b'\x00')
    u64 = struct.unpack('<Q', chunk)[0]
    i64 = struct.unpack('<q', chunk)[0]
    d64 = struct.unpack('<d', chunk)[0]
    u32_0, u32_1 = struct.unpack('<II', chunk)
    i32_0, i32_1 = struct.unpack('<ii', chunk)
    print(f"Offset {i:2d}: hex={chunk.hex()} | u64={u64:12d} | i64={i64:12d} | u32=({u32_0}, {u32_1}) | i32=({i32_0}, {i32_1}) | double={d64:.6g}")

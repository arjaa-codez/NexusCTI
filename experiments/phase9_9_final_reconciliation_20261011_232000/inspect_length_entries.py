import struct
from pathlib import Path

MASTER_DIR = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db")
SEGMENT_DIR = MASTER_DIR / "3962f896-273d-4039-b97e-d0aa4e6d29ed"

length_path = SEGMENT_DIR / "length.bin"
with open(length_path, "rb") as f:
    data = f.read()

print(f"Total length.bin size: {len(data)} bytes ({len(data)//4} uint32 entries)")

entries = [struct.unpack("<I", data[i:i+4])[0] for i in range(0, len(data), 4)]
for i, val in enumerate(entries[:20]):
    print(f"Node {i:2d}: {val} (0x{val:08x})")

import struct
from pathlib import Path

p = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Lib\site-packages\chromadb_rust_bindings\chromadb_rust_bindings.pyd")
with open(p, "rb") as f:
    data = f.read()

text_start = 0x400
text_rva = 0x1000

for off in range(0x22e3100, 0x22e4500):
    val = struct.unpack("<i", data[off:off+4])[0]
    rva = text_rva + (off - text_start)
    target = rva + 4 + val
    if 0x252e000 <= target < 0x3a75000:
        target_off = target - 0x252e000 + 0x252d000
        if 0 <= target_off < len(data):
            end = data.find(b"\x00", target_off)
            if end != -1 and end - target_off < 100:
                s = data[target_off:end]
                if len(s) > 3 and all(32 <= b < 127 for b in s):
                    print(f"Off 0x{off:x} (RVA 0x{rva:x}) refs string: {s.decode('ascii')}")

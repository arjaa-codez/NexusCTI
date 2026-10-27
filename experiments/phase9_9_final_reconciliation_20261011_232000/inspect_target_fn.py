from pathlib import Path
import struct

p = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Lib\site-packages\chromadb_rust_bindings\chromadb_rust_bindings.pyd")
with open(p, "rb") as f:
    data = f.read()

text_start = 0x400
text_rva = 0x1000

# Let's inspect the call at 0x22e6e14: e8 a6 d2 ff ff
off = 0x22e6e14
rel = struct.unpack('<i', data[off+1:off+5])[0]
target_off = off + 5 + rel
print(f"Call at 0x{off:x} targets file off 0x{target_off:x}")

# Let's inspect 200 bytes at target_off
chunk = data[target_off:target_off+200]
for i in range(0, len(chunk), 16):
    hex_str = " ".join(f"{b:02x}" for b in chunk[i:i+16])
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk[i:i+16])
    print(f"{target_off + i:07x}:  {hex_str:<48}  {ascii_str}")

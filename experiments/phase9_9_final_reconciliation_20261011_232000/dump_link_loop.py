from pathlib import Path

p = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Lib\site-packages\chromadb_rust_bindings\chromadb_rust_bindings.pyd")
with open(p, "rb") as f:
    data = f.read()

off_base = 0x22e40c0
chunk = data[off_base:off_base+300]
for i in range(0, len(chunk), 16):
    hex_str = " ".join(f"{b:02x}" for b in chunk[i:i+16])
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk[i:i+16])
    print(f"{off_base + i:07x}:  {hex_str:<48}  {ascii_str}")

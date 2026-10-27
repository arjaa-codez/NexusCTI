from pathlib import Path
import struct

p = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Lib\site-packages\chromadb_rust_bindings\chromadb_rust_bindings.pyd")
with open(p, "rb") as f:
    data = f.read()

# Let's inspect the instructions between 0x22e6d40 and 0x22e6e30
# In 0x22e6d40:
# It calls memory allocation and reads data_level0.bin, length.bin, link_lists.bin!
# Let's print the calls and jumps
chunk = data[0x22e6d40:0x22e6e40]
print(f"Chunk length: {len(chunk)}")
off_base = 0x22e6d40
for i in range(0, len(chunk), 16):
    hex_str = " ".join(f"{b:02x}" for b in chunk[i:i+16])
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk[i:i+16])
    print(f"{off_base + i:07x}:  {hex_str:<48}  {ascii_str}")

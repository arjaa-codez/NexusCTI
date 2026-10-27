import struct
from pathlib import Path

p = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Lib\site-packages\chromadb_rust_bindings\chromadb_rust_bindings.pyd")
with open(p, "rb") as f:
    data = f.read()

text_start = 0x400
text_rva = 0x1000

# find string in data
target_str = b"Cannot read persisted index"
s_off = data.find(target_str)
print(f"String '{target_str.decode()}' at file off 0x{s_off:x}")

# RVA of string
s_rva = 0x252e000 + (s_off - 0x252d000)
print(f"RVA of string: 0x{s_rva:x}")

# Find references to this string in .text
for off in range(text_start, 0x252d000):
    val = struct.unpack("<i", data[off:off+4])[0]
    rva = text_rva + (off - text_start)
    if rva + 4 + val == s_rva:
        print(f"Reference at file off 0x{off:x}, RVA 0x{rva:x}")

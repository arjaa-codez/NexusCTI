import shutil, hashlib, sys
sys.path.insert(0, ".")
from pathlib import Path
from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine

master_dir = Path('cyber_attribution_engine/data/chroma_db')
snap_dir = Path('experiments/phase9_7_independent_approval/scratch/test_hnsw_check')
if snap_dir.exists(): shutil.rmtree(snap_dir)
shutil.copytree(master_dir, snap_dir)

pre = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in snap_dir.rglob('*') if p.is_file()}

# run query
rag = ThreatRAGEngine(persist_directory=str(snap_dir))
res = rag.hybrid_search('test', top_k=2)

post = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in snap_dir.rglob('*') if p.is_file()}

print('PRE VS POST COMPARISON:')
for k in pre:
    print(f'{k:20s}: match={pre[k] == post.get(k)} pre={pre[k][:12]} post={post.get(k, "")[:12]}')

import gc
del rag
gc.collect()
shutil.rmtree(snap_dir, ignore_errors=True)

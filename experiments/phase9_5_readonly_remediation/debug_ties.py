import sys
sys.path.insert(0, ".")
from experiments.phase9_5_readonly_remediation.run_phase9_5_validation import orig_rag, adapter, test_queries

for tid, q_text, gnn_actor, k in [test_queries[7], test_queries[9]]:
    o = orig_rag.hybrid_search(q_text, gnn_top_group=gnn_actor, top_k=k)
    r = adapter.hybrid_search(q_text, gnn_top_group=gnn_actor, top_k=k)
    print(f"=== {tid} ===")
    for idx in range(max(len(o), len(r))):
        oi = o[idx] if idx < len(o) else {}
        ri = r[idx] if idx < len(r) else {}
        print(f"Rank {idx+1}:")
        print(f"  Orig: actor={oi.get('threat_actor')} | doc={oi.get('report_id')} | sim={oi.get('similarity')}")
        print(f"  Adap: actor={ri.get('threat_actor')} | doc={ri.get('report_id')} | sim={ri.get('similarity')}")

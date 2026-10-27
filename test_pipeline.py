import sys
from nexuscti.service import get_service

def main():
    print("[1] Initializing service...")
    s = get_service()
    print("[2] Analyzing indicator: 185.225.17.42")
    res = s.analyze("185.225.17.42")
    print(f"Attributed Actor: {res.top_actor.actor_name if res.top_actor else 'None'}")
    print(f"Fused Confidence: {res.top_actor.fused_confidence if res.top_actor else 0.0}")
    print(f"Structural Conf:  {res.top_actor.structural_confidence if res.top_actor else 0.0}")
    print(f"Textual Conf:     {res.top_actor.textual_confidence if res.top_actor else 0.0}")
    print(f"Multi-Hop Depth:  {res.multi_hop_depth} hops")
    print(f"Hallucination:    {res.hallucination_risk}")
    if res.graph_trail:
        print("Graph Trail:")
        for h in res.graph_trail.hops:
            print(f"  Step {h.step}: {h.source_name} --({h.relation})--> {h.target_name} [{h.citation}]")
    print("\nSUCCESS!")

if __name__ == "__main__":
    main()

r"""Streamlit Interactive SOC Dashboard for Cyber-Threat Attribution Engine.
Complies with Step 6 of the System Specification:
1. Sidebar configuration: Ollama model selection, alpha balance weight slider, quick sample IOCs.
2. Main input box for anomalous IOCs (IP, domain, malware, CVE).
3. 4-part investigative visualization:
   - GNN Structural Traversal Path & Confidence Score
   - Exact CTI Report Excerpts retrieved via RAG
   - Final Synthesized LLM Attribution Brief
   - Mathematical Score Breakdown Matrix & Candidate Distribution
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import streamlit as st

# Setup python path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cyber_attribution_engine.src.gnn_model import AttributionReasoner
from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine
from cyber_attribution_engine.src.fusion_layer import HybridFusionEngine

# Streamlit page layout configuration
st.set_page_config(
    page_title="NexusCTI | Hybrid GNN + RAG Threat Attribution",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End Cyber Glassmorphism CSS scoped specifically to custom classes
st.markdown(
    """
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .metric-card {
        background: #1e293b;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 800;
        color: #38bdf8;
        font-family: monospace;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    
    .rag-box {
        background: #0f172a;
        border-left: 4px solid #a855f7;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 14px;
        font-size: 14px;
        line-height: 1.6;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Initializing RGCN Graph Model & ChromaDB Vector Store...")
def load_attribution_engine():
    """Initializes and caches the Hybrid Attribution Engine."""
    processed_dir = ROOT / "cyber_attribution_engine" / "data" / "processed_graph"
    chroma_dir = ROOT / "cyber_attribution_engine" / "data" / "chroma_db"
    raw_dir = ROOT / "cyber_attribution_engine" / "data" / "raw_reports"
    weights_path = processed_dir / "rgcn_weights.pt"

    reasoner = AttributionReasoner(
        processed_dir / "hetero_graph.pt",
        processed_dir / "graph_metadata.json",
        model_weights_path=weights_path if weights_path.exists() else None,
    )
    rag = ThreatRAGEngine(
        persist_directory=chroma_dir,
        raw_reports_dir=raw_dir,
    )
    return HybridFusionEngine(reasoner, rag)


# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Engine Parameters")

    ollama_model = st.selectbox(
        "🧠 Ollama LLM Model",
        options=["llama3", "mistral", "deepseek-r1:8b", "qwen2.5:7b"],
        index=0,
        help="Local LLM model to synthesize the final CTI attribution brief.",
    )

    alpha_weight = st.slider(
        "⚖️ Balance Weight (α)",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.05,
        help="α balances GNN structural graph confidence vs (1-α) RAG semantic cosine similarity.",
    )

    st.markdown("---")
    st.markdown("### 🎯 Verified Benchmark Scenarios")
    sample_iocs = {
        "SolarWinds (185.225.17.42)": "185.225.17.42",
        "Fancy Bear (auth-microsoft365.com)": "auth-microsoft365.com",
        "Lazarus Group (175.45.176.8)": "175.45.176.8",
        "Sandworm Team (194.28.172.10)": "194.28.172.10",
        "Volt Typhoon (198.51.100.44)": "198.51.100.44",
        "FIN7 Syndicate (193.106.191.4)": "193.106.191.4",
        "ProxyLogon CVE (CVE-2021-26855)": "CVE-2021-26855",
    }
    selected_sample = st.selectbox("Select Pre-loaded Real IOC:", list(sample_iocs.keys()))
    if st.button("Load Scenario IOC", use_container_width=True):
        st.session_state["ioc_input"] = sample_iocs[selected_sample]
        st.session_state["trigger_analysis"] = True

    st.markdown("---")
    st.markdown("#### 📐 Mathematical Formulation")
    st.latex(r"S(A_i \mid \text{IOC}) = \alpha \cdot \text{Softmax}(z_{\text{IOC}}^T z_{A_i}) + (1-\alpha) \cdot \max_{d \in \mathcal{D}_k} \text{Sim}(E_q, E_d)")

# Main Header
st.markdown(
    """
    <div class="hero-banner">
        <h1 style="margin: 0; color: #38bdf8; font-size: 26px;">🛡️ HYBRID GNN + RAG CYBER-THREAT ATTRIBUTION ENGINE</h1>
        <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 14px;">
            Heterogeneous Graph Neural Network (RGCN) message passing with Contrastive Link Prediction & ChromaDB Vector RAG Score Fusion.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Search Bar
col_input, col_btn = st.columns([5, 1])
with col_input:
    default_val = st.session_state.get("ioc_input", "185.225.17.42")
    user_ioc = st.text_input(
        "Investigate Anomalous Indicator of Compromise (IP, Domain, Malware, CVE):",
        value=default_val,
        placeholder="Enter IP (e.g. 185.225.17.42) or Domain (e.g. auth-microsoft365.com)...",
    )
with col_btn:
    st.write("")
    st.write("")
    run_btn = st.button("⚡ Attribute IOC", use_container_width=True, type="primary")

should_run = run_btn or st.session_state.get("trigger_analysis", False) or bool(user_ioc)
if should_run:
    st.session_state["trigger_analysis"] = False
    engine = load_attribution_engine()

    with st.spinner("Executing RGCN graph convolution and ChromaDB vector retrieval..."):
        result = engine.compute_hybrid_attribution(
            ioc=user_ioc.strip(),
            alpha=alpha_weight,
            top_k_rag=3,
            ollama_model=ollama_model,
        )

    # Top KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Attributed Actor</div>
                <div class="metric-val" style="color: #10b981;">{result['attributed_group']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Hybrid Score S(A_i | IOC)</div>
                <div class="metric-val">{result['final_attribution_score']:.4f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">GNN Graph Confidence</div>
                <div class="metric-val" style="color: #38bdf8;">{result['gnn_structural_score']:.4f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">RAG Semantic Sim</div>
                <div class="metric-val" style="color: #a855f7;">{result['rag_semantic_score']:.4f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 4-Tab Detailed Investigation Panel
    tab_path, tab_rag, tab_llm, tab_matrix = st.tabs([
        "📍 1. GNN Structural Traversal Path",
        "📄 2. Exact CTI Report Excerpts",
        "📝 3. Synthesized LLM Attribution Brief",
        "📊 4. Candidate Distribution Matrix",
    ])

    with tab_path:
        st.markdown("#### 🔗 Multi-Hop Relational Provenance Walk")
        st.caption("Traces relational link prediction updates across HeteroData edges: resolves_to, drops, attributed_to, uses.")
        
        path = result.get("gnn_traversal_path", [])
        if path:
            st.markdown(
                '<div style="background: #0f172a; padding: 18px; border-radius: 10px; border: 1px solid rgba(56, 189, 248, 0.2);">',
                unsafe_allow_html=True,
            )
            for idx, step in enumerate(path):
                from_color = "#38bdf8" if step["from_type"] == "ip" else "#a855f7" if step["from_type"] == "domain" else "#ef4444"
                to_color = "#10b981" if step["to_type"] == "attack_group" else "#f59e0b" if step["to_type"] == "technique" else "#ef4444"

                st.markdown(
                    f"""
                    <div style="margin: 10px 0; display: flex; align-items: center; flex-wrap: wrap;">
                        <span style="background: rgba(56, 189, 248, 0.1); border: 1px solid {from_color}; color: {from_color}; padding: 6px 12px; border-radius: 6px; font-family: monospace;">
                            [{step['from_type'].upper()}] {step['from']}
                        </span>
                        <span style="color: #94a3b8; margin: 0 12px; font-weight: bold;">
                            ──( {step['relation']} )──►
                        </span>
                        <span style="background: rgba(16, 185, 129, 0.1); border: 1px solid {to_color}; color: {to_color}; padding: 6px 12px; border-radius: 6px; font-family: monospace;">
                            [{step['to_type'].upper()}] {step['to']}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No direct multi-hop path mapped. Indicator evaluated via dense latent embedding space.")

    with tab_rag:
        st.markdown("#### 📚 ChromaDB Top-k Semantic Report Chunks")
        st.caption("Retrieved using sentence-transformers all-MiniLM-L6-v2 with threat-actor metadata filtering.")
        
        chunks = result.get("retrieved_cti_chunks", [])
        if chunks:
            for idx, c in enumerate(chunks):
                st.markdown(
                    f"""
                    <div class="rag-box">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-weight: 700; color: #c084fc;">Chunk #{idx+1} | Source: {c.get('report_id')}</span>
                            <span style="color: #38bdf8; font-family: monospace;">Cosine Sim: {c.get('similarity'):.4f}</span>
                        </div>
                        <div style="color: #cbd5e1; font-style: italic;">"{c.get('text')}"</div>
                        <div style="margin-top: 8px; font-size: 12px; color: #64748b;">
                            Origin: {c.get('origin', 'N/A')} | Aliases: {c.get('aliases', 'N/A')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("No corroborating CTI document chunks retrieved.")

    with tab_llm:
        st.markdown("#### 🧠 Synthesized Threat Attribution Brief")
        st.caption(f"Generated via Ollama ({ollama_model}) with grounded mathematical context.")
        st.markdown(result.get("llm_brief", "No brief generated."))

        with st.expander("🔍 View Structured Prompt Fed to LLM"):
            st.code(result.get("llm_prompt", ""), language="text")

    with tab_matrix:
        st.markdown("#### 📈 Candidate Attack Group Confidence Comparison")
        st.caption("Full Softmax and Hybrid probability distributions across all indexed APT entities.")
        group_scores = result.get("all_group_scores", {})
        
        col_chart, col_raw = st.columns([3, 2])
        with col_chart:
            for grp, scr in sorted(group_scores.items(), key=lambda x: x[1], reverse=True):
                pct = min(100, max(2, int(scr * 100)))
                bar_color = "#10b981" if grp == result["attributed_group"] else "#38bdf8"
                st.markdown(
                    f"""
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 4px;">
                            <span>{grp}</span>
                            <span style="font-family: monospace; color: {bar_color};">{scr:.4f} ({pct}%)</span>
                        </div>
                        <div style="background: #1e293b; border-radius: 6px; overflow: hidden; height: 10px; border: 1px solid rgba(255,255,255,0.08);">
                            <div style="width: {pct}%; background: {bar_color}; height: 100%; border-radius: 6px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with col_raw:
            st.dataframe(
                [{"Attack Group": k, "Hybrid Score": f"{v:.4f}"} for k, v in group_scores.items()],
                use_container_width=True,
                hide_index=True,
            )

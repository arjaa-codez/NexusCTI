/**
 * NexusCTI Web Dashboard Application
 * Handles workbench interactions, dual-layer attribution briefs,
 * interactive knowledge graph rendering, and empirical benchmarks.
 */

let currentGraphData = { nodes: [], edges: [] };
let activeTrailHops = [];
let currentAnalysisResult = null;
let currentMarkdownReport = "";

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadScenarios();
    loadKnowledgeGraph();
    loadBenchmarkData();
    setupEventListeners();
});

// ==========================================
// 1. TAB NAVIGATION
// ==========================================
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const viewPanels = document.querySelectorAll(".view-panel");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            tabBtns.forEach(b => b.classList.remove("active"));
            viewPanels.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const activePanel = document.getElementById(`view-${targetTab}`);
            if (activePanel) {
                activePanel.classList.add("active");
            }

            if (targetTab === "graph-view") {
                resizeCanvas();
                drawGraph();
            }
        });
    });
}

// ==========================================
// 2. SCENARIO LOADER
// ==========================================
async function loadScenarios() {
    const container = document.getElementById("scenario-list");
    try {
        const resp = await fetch("/api/cases");
        const cases = await resp.json();

        container.innerHTML = "";
        cases.forEach(c => {
            const item = document.createElement("div");
            item.className = "scenario-item";
            item.innerHTML = `
                <div>
                    <strong>${c.name}</strong>
                    <div style="font-size:0.7rem; color:#64748b;">${c.category.replace(/_/g, " ")}</div>
                </div>
                <span class="hop-tag">${c.expected_hops} Hops</span>
            `;
            item.addEventListener("click", () => {
                document.querySelectorAll(".scenario-item").forEach(el => el.classList.remove("active"));
                item.classList.add("active");
                document.getElementById("incident-query").value = c.query;
                document.getElementById("anchor-ioc").value = c.anchor_ioc;
                runAttribution(c.query, c.anchor_ioc);
            });
            container.appendChild(item);
        });

        // Trigger first scenario automatically on load
        if (cases.length > 0) {
            const first = cases[0];
            document.getElementById("incident-query").value = first.query;
            document.getElementById("anchor-ioc").value = first.anchor_ioc;
            runAttribution(first.query, first.anchor_ioc);
        }
    } catch (err) {
        console.error("Failed to load scenarios:", err);
        container.innerHTML = "<div class='empty-state'>Failed to load scenarios.</div>";
    }
}

// ==========================================
// 3. ATTRIBUTION PIPELINE
// ==========================================
function setupEventListeners() {
    const runBtn = document.getElementById("btn-run-attribution");
    runBtn.addEventListener("click", () => {
        const query = document.getElementById("incident-query").value.trim();
        const anchor = document.getElementById("anchor-ioc").value.trim();
        if (query) {
            runAttribution(query, anchor || null);
        }
    });

    const liveBmBtn = document.getElementById("btn-run-live-benchmark");
    if (liveBmBtn) {
        liveBmBtn.addEventListener("click", () => runLiveBenchmark());
    }

    const copyReportBtn = document.getElementById("btn-copy-report");
    if (copyReportBtn) {
        copyReportBtn.addEventListener("click", () => {
            if (currentMarkdownReport) {
                navigator.clipboard.writeText(currentMarkdownReport);
                copyReportBtn.innerText = "Copied to Clipboard!";
                setTimeout(() => { copyReportBtn.innerText = "Copy Markdown"; }, 2000);
            }
        });
    }

    const downloadReportBtn = document.getElementById("btn-download-report");
    if (downloadReportBtn) {
        downloadReportBtn.addEventListener("click", () => {
            if (currentMarkdownReport) {
                const blob = new Blob([currentMarkdownReport], { type: "text/markdown" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `nexuscti_attribution_brief_${Date.now()}.md`;
                a.click();
            }
        });
    }

    const resetGraphBtn = document.getElementById("btn-reset-graph");
    if (resetGraphBtn) {
        resetGraphBtn.addEventListener("click", () => resetGraphZoom());
    }

    const highlightTrailBtn = document.getElementById("btn-highlight-trail");
    if (highlightTrailBtn) {
        highlightTrailBtn.addEventListener("click", () => {
            graphState.onlyTrail = !graphState.onlyTrail;
            highlightTrailBtn.innerText = graphState.onlyTrail ? "Show All Nodes" : "Highlight Current Trail";
            drawGraph();
        });
    }
}

async function runAttribution(query, anchor) {
    const runBtn = document.getElementById("btn-run-attribution");
    runBtn.disabled = true;
    runBtn.innerText = "Analyzing Telemetry...";

    try {
        const resp = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, ioc_override: anchor })
        });

        const data = await resp.json();
        currentAnalysisResult = data.analysis;
        currentMarkdownReport = data.markdown_report;

        renderAttributionResults(data.analysis);
        renderReportView(data.markdown_report);

        if (data.analysis.graph_trail) {
            activeTrailHops = data.analysis.graph_trail.hops || [];
        } else {
            activeTrailHops = [];
        }
    } catch (err) {
        console.error("Attribution error:", err);
        alert("Attribution execution failed. Check console or server logs.");
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            Execute Attribution Engine
        `;
    }
}

function renderAttributionResults(res) {
    const top = res.top_attribution;
    if (!top) return;

    // Header & Verdict
    const verdictEl = document.getElementById("actor-verdict");
    verdictEl.className = `verdict-tag ${top.verdict}`;
    verdictEl.innerText = `${top.verdict.replace(/_/g, " ")} ATTRIBUTION`;

    document.getElementById("actor-name").innerText = top.actor_name;
    document.getElementById("actor-rationale").innerText = res.investigation.synergistic_rationale;

    // Fused Confidence Radial
    const fusedPct = Math.round(top.fused_confidence * 100);
    document.getElementById("fused-conf-val").innerText = `${fusedPct}%`;

    // 4 Pillars
    const gnnPct = Math.round(top.structural_confidence * 100);
    const ragPct = Math.round(top.textual_confidence * 100);
    const cvPct = Math.round(top.cross_validation_score * 100);

    document.getElementById("val-gnn").innerText = `${gnnPct}%`;
    document.getElementById("bar-gnn").style.width = `${gnnPct}%`;

    document.getElementById("val-rag").innerText = `${ragPct}%`;
    document.getElementById("bar-rag").style.width = `${ragPct}%`;

    document.getElementById("val-cv").innerText = `${cvPct}%`;
    document.getElementById("bar-cv").style.width = `${cvPct}%`;

    document.getElementById("val-hops").innerText = `${res.investigation.multi_hop_depth} Hops`;
    document.getElementById("val-hallucination").innerText = `Risk: ${res.investigation.hallucination_risk}`;

    // Layer 1: The Graph Trail
    renderGraphTrail(res.graph_trail);

    // Layer 2: The Narrative Proof
    renderNarrativeProofs(res.narrative_proofs);

    // Candidate Confidence Matrix
    renderCandidatesTable(res.all_candidates);
}

function renderGraphTrail(trail) {
    const container = document.getElementById("trail-flow-container");
    const countEl = document.getElementById("trail-step-count");

    if (!trail || !trail.hops || trail.hops.length === 0) {
        container.innerHTML = "<div class='empty-state'>Direct structural proximity (no multi-hop intermediary nodes required).</div>";
        countEl.innerText = "0 Steps";
        return;
    }

    countEl.innerText = `${trail.hops.length} Steps`;
    container.innerHTML = "";

    trail.hops.forEach(hop => {
        const card = document.createElement("div");
        card.className = "trail-step-card";
        card.innerHTML = `
            <div class="step-header">
                <span class="step-number">Step ${hop.step} — Multi-Hop Pivot</span>
                <span class="step-citation">${hop.citation || "Knowledge Graph Topology"}</span>
            </div>
            <div class="step-chain">
                <span class="node-chip ${hop.source_type}">${hop.source_name}</span>
                <span class="rel-chip">--[ ${hop.relation} ]--></span>
                <span class="node-chip ${hop.target_type}">${hop.target_name}</span>
            </div>
            <div class="step-rationale">${hop.rationale}</div>
        `;
        container.appendChild(card);
    });
}

function renderNarrativeProofs(proofs) {
    const container = document.getElementById("narrative-cards-container");
    const countEl = document.getElementById("proof-citation-count");

    if (!proofs || proofs.length === 0) {
        container.innerHTML = "<div class='empty-state'>No direct narrative citations retrieved.</div>";
        countEl.innerText = "0 Citations";
        return;
    }

    countEl.innerText = `${proofs.length} Citations`;
    container.innerHTML = "";

    proofs.forEach(p => {
        const card = document.createElement("div");
        card.className = "narrative-card";

        const iocBadges = (p.matched_iocs || []).map(ioc => `<span class="ioc-badge">${ioc}</span>`).join(" ");

        card.innerHTML = `
            <div class="narrative-header">
                <span class="source-tag">${p.source} (${p.date})</span>
                <span class="score-tag">RRF Rank Score: ${p.retrieval_score.toFixed(2)}</span>
            </div>
            <div class="narrative-quote">"${p.relevant_text.trim()}"</div>
            ${iocBadges ? `
                <div class="matched-iocs-row">
                    <span class="matched-label">Corroborated IOCs:</span>
                    ${iocBadges}
                </div>
            ` : ''}
        `;
        container.appendChild(card);
    });
}

function renderCandidatesTable(candidates) {
    const tbody = document.getElementById("candidates-table-body");
    if (!candidates || candidates.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7' class='text-center'>No candidates evaluated.</td></tr>";
        return;
    }

    tbody.innerHTML = "";
    candidates.forEach((c, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>#${idx + 1}</td>
            <td><strong>${c.actor_name}</strong></td>
            <td><strong style="color:var(--neon-cyan)">${(c.fused_confidence * 100).toFixed(1)}%</strong></td>
            <td>${(c.structural_confidence * 100).toFixed(1)}%</td>
            <td>${(c.textual_confidence * 100).toFixed(1)}%</td>
            <td>${(c.cross_validation_score * 100).toFixed(1)}%</td>
            <td><span class="verdict-tag ${c.verdict}" style="font-size:0.65rem; padding:0.15rem 0.5rem">${c.verdict}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderReportView(markdown) {
    const el = document.getElementById("report-rendered-content");
    if (el) {
        el.innerText = markdown;
    }
}

// ==========================================
// 4. KNOWLEDGE GRAPH CANVAS VISUALIZER
// ==========================================
let canvas, ctx;
let graphState = {
    zoom: 1.0,
    panX: 0,
    panY: 0,
    isDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    hoveredNode: null,
    onlyTrail: false
};

const TYPE_COLORS = {
    ThreatActor: "#ef4444",
    Malware: "#f59e0b",
    Indicator: "#00f0ff",
    TTP: "#10b981",
    Vulnerability: "#a855f7"
};

async function loadKnowledgeGraph() {
    try {
        const resp = await fetch("/api/graph");
        currentGraphData = await resp.json();

        // Update status pill
        const statPill = document.getElementById("graph-stat-pill");
        if (statPill) {
            statPill.innerText = `${currentGraphData.nodes.length} Nodes • ${currentGraphData.edges.length} Edges`;
        }

        layoutGraphNodes();
        initCanvas();
    } catch (err) {
        console.error("Failed to load knowledge graph:", err);
    }
}

function layoutGraphNodes() {
    // Arrange nodes into concentric structural tiers:
    // Center: ThreatActors
    // Ring 1: Malwares & TTPs
    // Ring 2: Vulnerabilities
    // Ring 3: Indicators
    const nodes = currentGraphData.nodes;
    const actors = nodes.filter(n => n.type === "ThreatActor");
    const malwares = nodes.filter(n => n.type === "Malware");
    const ttps = nodes.filter(n => n.type === "TTP");
    const cves = nodes.filter(n => n.type === "Vulnerability");
    const iocs = nodes.filter(n => n.type === "Indicator");

    const assignRing = (list, radius, centerOffset = 0) => {
        const count = list.length;
        list.forEach((n, i) => {
            const angle = (2 * Math.PI * i) / (count || 1) + centerOffset;
            n.x = Math.cos(angle) * radius;
            n.y = Math.sin(angle) * radius;
        });
    };

    assignRing(actors, 100);
    assignRing(malwares, 240);
    assignRing(ttps, 360, 0.4);
    assignRing(cves, 480, 0.8);
    assignRing(iocs, 600, 0.2);
}

function initCanvas() {
    canvas = document.getElementById("kg-canvas");
    if (!canvas) return;
    ctx = canvas.getContext("2d");

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Center viewport
    graphState.panX = canvas.width / 2;
    graphState.panY = canvas.height / 2;

    // Pan & Zoom events
    canvas.addEventListener("mousedown", (e) => {
        graphState.isDragging = true;
        graphState.dragStartX = e.clientX - graphState.panX;
        graphState.dragStartY = e.clientY - graphState.panY;
    });

    window.addEventListener("mousemove", (e) => {
        if (graphState.isDragging) {
            graphState.panX = e.clientX - graphState.dragStartX;
            graphState.panY = e.clientY - graphState.dragStartY;
            drawGraph();
        } else {
            handleCanvasHover(e);
        }
    });

    window.addEventListener("mouseup", () => {
        graphState.isDragging = false;
    });

    canvas.addEventListener("wheel", (e) => {
        e.preventDefault();
        const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
        graphState.zoom = Math.max(0.3, Math.min(3.0, graphState.zoom * zoomFactor));
        drawGraph();
    });

    drawGraph();
}

function resizeCanvas() {
    if (!canvas) return;
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
    drawGraph();
}

function resetGraphZoom() {
    graphState.zoom = 0.85;
    graphState.panX = canvas.width / 2;
    graphState.panY = canvas.height / 2;
    graphState.onlyTrail = false;
    drawGraph();
}

function handleCanvasHover(e) {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - graphState.panX) / graphState.zoom;
    const mouseY = (e.clientY - rect.top - graphState.panY) / graphState.zoom;

    let found = null;
    for (const node of currentGraphData.nodes) {
        const dx = node.x - mouseX;
        const dy = node.y - mouseY;
        if (Math.sqrt(dx * dx + dy * dy) < 14) {
            found = node;
            break;
        }
    }

    const tooltip = document.getElementById("node-tooltip");
    if (found) {
        graphState.hoveredNode = found;
        tooltip.style.display = "block";
        tooltip.style.left = `${e.clientX + 14}px`;
        tooltip.style.top = `${e.clientY + 14}px`;
        tooltip.innerHTML = `
            <div style="font-weight:700; color:${TYPE_COLORS[found.type] || '#fff'}">${found.label}</div>
            <div style="font-size:0.7rem; color:#94a3b8; text-transform:uppercase;">${found.type}</div>
            <div style="font-size:0.72rem; margin-top:0.3rem;">${found.description || "Active Knowledge Graph Entity"}</div>
        `;
    } else {
        graphState.hoveredNode = null;
        tooltip.style.display = "none";
    }
    drawGraph();
}

function drawGraph() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.translate(graphState.panX, graphState.panY);
    ctx.scale(graphState.zoom, graphState.zoom);

    // Identify active trail nodes & edges
    const trailNodeIds = new Set();
    const trailEdgeKeys = new Set();

    activeTrailHops.forEach(h => {
        trailNodeIds.add(h.source_id);
        trailNodeIds.add(h.target_id);
        trailEdgeKeys.add(`${h.source_id}->${h.target_id}`);
        trailEdgeKeys.add(`${h.target_id}->${h.source_id}`);
    });

    const nodeMap = new Map();
    currentGraphData.nodes.forEach(n => nodeMap.set(n.id, n));

    // Draw Edges
    currentGraphData.edges.forEach(e => {
        const src = nodeMap.get(e.source);
        const tgt = nodeMap.get(e.target);
        if (!src || !tgt) return;

        const isTrailEdge = trailEdgeKeys.has(`${e.source}->${e.target}`);

        if (graphState.onlyTrail && !isTrailEdge) return;

        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);

        if (isTrailEdge) {
            ctx.strokeStyle = "#00f0ff";
            ctx.lineWidth = 3.5;
            ctx.shadowColor = "#00f0ff";
            ctx.shadowBlur = 12;
        } else {
            ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
            ctx.lineWidth = 1;
            ctx.shadowBlur = 0;
        }
        ctx.stroke();
    });

    // Reset shadow
    ctx.shadowBlur = 0;

    // Draw Nodes
    currentGraphData.nodes.forEach(n => {
        const isTrailNode = trailNodeIds.has(n.id);
        if (graphState.onlyTrail && !isTrailNode) return;

        const radius = n.type === "ThreatActor" ? 18 : 10;
        const color = TYPE_COLORS[n.type] || "#ffffff";

        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
        ctx.fillStyle = color;

        if (isTrailNode) {
            ctx.shadowColor = color;
            ctx.shadowBlur = 20;
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2.5;
            ctx.stroke();
        } else {
            ctx.shadowBlur = 0;
            ctx.fill();
        }

        // Draw Labels
        ctx.shadowBlur = 0;
        ctx.fillStyle = isTrailNode ? "#ffffff" : "#94a3b8";
        ctx.font = isTrailNode ? "bold 11px Inter" : "9px Inter";
        ctx.textAlign = "center";
        ctx.fillText(n.label, n.x, n.y + radius + 12);
    });

    ctx.restore();
}

// ==========================================
// 5. EMPIRICAL BENCHMARKS VIEW
// ==========================================
async function loadBenchmarkData() {
    try {
        const resp = await fetch("/api/benchmark");
        const data = await resp.json();
        updateBenchmarkUI(data);
    } catch (err) {
        console.error("Benchmark fetch error:", err);
    }
}

async function runLiveBenchmark() {
    const btn = document.getElementById("btn-run-live-benchmark");
    btn.disabled = true;
    btn.innerText = "Executing Evaluation Matrix...";

    try {
        const resp = await fetch("/api/benchmark");
        const data = await resp.json();
        updateBenchmarkUI(data);
        alert("Live benchmark evaluation completed successfully across all 12 test challenges!");
    } catch (err) {
        console.error("Live benchmark failed:", err);
        alert("Benchmark execution failed.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            Run Live Benchmark Suite
        `;
    }
}

function updateBenchmarkUI(data) {
    const summary = data.summary;
    if (!summary) return;

    const v = summary["Naive Vector-only RAG"];
    const g = summary["Standalone GNN Classifier"];
    const h = summary["NexusCTI Hybrid (GNN + RAG)"];

    // Update Big Numbers
    document.getElementById("bm-top1-hybrid").innerText = `${h.top1_accuracy}%`;
    document.getElementById("bm-multihop-hybrid").innerText = `${h.multihop_reasoning_success}%`;
    document.getElementById("bm-halluc-hybrid").innerText = `${h.hallucination_rate}%`;
    document.getElementById("bm-mrr-hybrid").innerText = h.mrr.toFixed(4);

    // Update Comparison Bars
    document.getElementById("bm-bar-top1-rag").style.width = `${v.top1_accuracy}%`;
    document.getElementById("bm-bar-top1-rag").innerText = `${v.top1_accuracy}%`;
    document.getElementById("bm-bar-top1-gnn").style.width = `${g.top1_accuracy}%`;
    document.getElementById("bm-bar-top1-gnn").innerText = `${g.top1_accuracy}%`;
    document.getElementById("bm-bar-top1-hybrid").style.width = `${h.top1_accuracy}%`;
    document.getElementById("bm-bar-top1-hybrid").innerText = `${h.top1_accuracy}%`;

    document.getElementById("bm-bar-mh-rag").style.width = `${v.multihop_reasoning_success}%`;
    document.getElementById("bm-bar-mh-rag").innerText = `${v.multihop_reasoning_success}%`;
    document.getElementById("bm-bar-mh-gnn").style.width = `${g.multihop_reasoning_success}%`;
    document.getElementById("bm-bar-mh-gnn").innerText = `${g.multihop_reasoning_success}%`;
    document.getElementById("bm-bar-mh-hybrid").style.width = `${h.multihop_reasoning_success}%`;
    document.getElementById("bm-bar-mh-hybrid").innerText = `${h.multihop_reasoning_success}%`;

    document.getElementById("bm-bar-hl-rag").style.width = `${v.hallucination_rate}%`;
    document.getElementById("bm-bar-hl-rag").innerText = `${v.hallucination_rate}%`;
    document.getElementById("bm-bar-hl-gnn").style.width = `${g.hallucination_rate}%`;
    document.getElementById("bm-bar-hl-gnn").innerText = `${g.hallucination_rate}%`;
    document.getElementById("bm-bar-hl-hybrid").style.width = `${h.hallucination_rate}%`;
    document.getElementById("bm-bar-hl-hybrid").innerText = `${h.hallucination_rate}%`;

    // Detailed Table
    const tbody = document.getElementById("benchmark-cases-body");
    const recs = data.detailed_case_evaluations || [];

    // Group records by case_id
    const grouped = {};
    recs.forEach(r => {
        if (!grouped[r.case_id]) {
            grouped[r.case_id] = {
                case_id: r.case_id,
                case_name: r.case_name,
                category: r.category,
                ground_truth: r.ground_truth,
                models: {}
            };
        }
        grouped[r.case_id].models[r.model] = r;
    });

    tbody.innerHTML = "";
    Object.values(grouped).forEach(gCase => {
        const tr = document.createElement("tr");

        const vRec = gCase.models["Naive Vector-only RAG"] || {};
        const gRec = gCase.models["Standalone GNN Classifier"] || {};
        const hRec = gCase.models["NexusCTI Hybrid (GNN + RAG)"] || {};

        const renderHit = (r) => r.is_correct ?
            `<span style="color:var(--neon-green)">✓ Correct</span>` :
            `<span style="color:var(--neon-red)">✗ Fail</span>`;

        tr.innerHTML = `
            <td><code>${gCase.case_id}</code></td>
            <td><strong>${gCase.case_name}</strong></td>
            <td><span class="badge neon-badge">${gCase.category.replace(/_/g, " ")}</span></td>
            <td><strong>${hRec.hops || 2} Hops</strong></td>
            <td><code>${gCase.ground_truth.replace("actor_", "").toUpperCase()}</code></td>
            <td>${renderHit(vRec)}</td>
            <td>${renderHit(gRec)}</td>
            <td>${renderHit(hRec)}</td>
        `;
        tbody.appendChild(tr);
    });
}

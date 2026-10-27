"""
System configuration and hyperparameters for NexusCTI.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "nexuscti" / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
WEB_DIR = BASE_DIR / "web"

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# GNN Model Hyperparameters
GNN_EMBEDDING_DIM = 64
GNN_HIDDEN_DIM = 64
GNN_NUM_LAYERS = 2
GNN_DROPOUT = 0.1
GNN_LEARNING_RATE = 0.01
GNN_EPOCHS = 120
GNN_WEIGHT_DECAY = 1e-4

# Hybrid RAG Configuration
RAG_BM25_K1 = 1.5
RAG_BM25_B = 0.75
RAG_DENSE_DIM = 64
RAG_TOP_K = 5
RAG_RRF_K = 60  # Reciprocal Rank Fusion constant

# Fusion & Decision Layer
FUSION_WEIGHT_GNN = 0.45      # Alpha: structural evidence weight
FUSION_WEIGHT_RAG = 0.35      # Beta: textual evidence weight
FUSION_WEIGHT_CROSS_VAL = 0.20 # Gamma: joint verification bonus

ATTRIBUTION_THRESHOLD_HIGH = 0.75
ATTRIBUTION_THRESHOLD_MEDIUM = 0.50

# Server Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

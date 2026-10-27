"""
Threat report chunking and metadata enrichment engine for CTI documents.
"""

from typing import List, Dict, Any
import re
from pydantic import BaseModel, Field

from ..data.corpus import ThreatReport


class TextChunk(BaseModel):
    chunk_id: str
    doc_id: str
    source: str
    date: str
    target_actor: str
    content: str
    iocs_mentioned: List[str] = Field(default_factory=list)
    cves_mentioned: List[str] = Field(default_factory=list)
    ttps_mentioned: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CTIChunker:
    """
    Chunks threat intelligence narratives while preserving technical indicator boundaries.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_report(self, report: ThreatReport) -> List[TextChunk]:
        raw_text = re.sub(r"\s+", " ", report.text.strip())
        sentences = re.split(r"(?<=[.!?])\s+", raw_text)

        chunks: List[TextChunk] = []
        current_sentences = []
        current_len = 0
        chunk_idx = 0

        for sent in sentences:
            sent_len = len(sent)
            if current_len + sent_len > self.chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append(self._create_chunk(report, chunk_text, chunk_idx))
                chunk_idx += 1
                # Retain last sentence for overlap
                current_sentences = [current_sentences[-1], sent] if len(current_sentences) > 1 else [sent]
                current_len = sum(len(s) for s in current_sentences)
            else:
                current_sentences.append(sent)
                current_len += sent_len

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append(self._create_chunk(report, chunk_text, chunk_idx))

        return chunks

    def _create_chunk(self, report: ThreatReport, text: str, idx: int) -> TextChunk:
        # Detect mentions
        text_lower = text.lower()
        mentioned_iocs = [ioc for ioc in report.iocs if ioc.lower() in text_lower or ioc.lower().replace("[.]", ".") in text_lower]
        mentioned_cves = [cve for cve in report.cves if cve.lower() in text_lower]
        mentioned_ttps = [ttp for ttp in report.ttps if ttp.lower() in text_lower]

        return TextChunk(
            chunk_id=f"{report.id}_c{idx}",
            doc_id=report.id,
            source=report.source,
            date=report.date,
            target_actor=report.target_actor,
            content=text,
            iocs_mentioned=mentioned_iocs,
            cves_mentioned=mentioned_cves,
            ttps_mentioned=mentioned_ttps,
            metadata={"title": report.title, "tags": report.tags}
        )

    def chunk_corpus(self, corpus: List[ThreatReport]) -> List[TextChunk]:
        all_chunks = []
        for report in corpus:
            all_chunks.extend(self.chunk_report(report))
        return all_chunks

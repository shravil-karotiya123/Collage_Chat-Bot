"""
MRPL AI Workbench — Claim Extraction Module
Parses generated engineering drafts into individual verifiable claim assertions.
"""

import re
from typing import List, Dict, Any


class ClaimExtractor:
    """
    Extracts atomic claims and citations from raw draft response text.
    """

    def extract_claims(self, draft_text: str) -> List[Dict[str, Any]]:
        """
        Extract sentences as individual claims alongside embedded citation tags.
        """
        if not draft_text:
            return []

        # Split text into candidate sentence claims
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", draft_text) if len(s.strip()) > 5]
        claims = []
        for idx, sentence in enumerate(sentences):
            # Extract citations like [doc-1] or [Chunk 02]
            citations = re.findall(r"\[([^\]]+)\]", sentence)
            claims.append({
                "claim_id": f"claim-{idx+1:02d}",
                "text": sentence,
                "citations": citations,
            })
        return claims

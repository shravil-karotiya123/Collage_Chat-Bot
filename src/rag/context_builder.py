"""
Context Builder Module for MRPL AI Workbench.
Filters retrieved chunks, builds compact context payloads, enforces max size limits,
and constructs strict grounding prompts for LLM synthesis.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from config.settings import settings
from src.schemas.rag import SourceCitationSchema

logger = logging.getLogger("MRPL.RAG.ContextBuilder")

GROUNDED_SYSTEM_PROMPT_TEMPLATE = """You are an AI assistant for MRPL AI Workbench operating in strict Grounded Document Retrieval Mode.

DOCUMENT CONTEXT:
======================================================================
{context_text}
======================================================================

STRICT INSTRUCTIONS:
1. Answer the user's question ONLY using the facts explicitly stated in the DOCUMENT CONTEXT above.
2. Do NOT invent, assume, or extrapolate any facts not directly mentioned in the context.
3. If the provided DOCUMENT CONTEXT does not contain enough information to answer the question, state clearly and concisely:
   "The available documents do not contain sufficient information to answer this query."
"""


@dataclass
class BuiltContext:
    """
    Container holding formatted compact context string, source citations, and availability status.
    """

    context_text: str
    sources: List[SourceCitationSchema]
    has_sufficient_context: bool
    grounded_prompt: str


class ContextBuilder:
    """
    Context Builder responsible for filtering retrieved chunks, enforcing character limits,
    extracting source citations, and formatting grounded prompts for Qwen LLM.
    """

    def __init__(self, max_context_length: Optional[int] = None) -> None:
        self.max_context_length = max_context_length or settings.MAX_RAG_CONTEXT

    def build_context(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        query: str,
    ) -> BuiltContext:
        """
        Build compact context string and citations from retrieved chunks.

        Args:
            retrieved_chunks: Output list from DocumentRetriever.
            query: User question string.

        Returns:
            BuiltContext object containing context_text, sources, and grounded_prompt.
        """
        if not retrieved_chunks:
            return BuiltContext(
                context_text="",
                sources=[],
                has_sufficient_context=False,
                grounded_prompt=self._format_prompt("", query),
            )

        context_blocks: List[str] = []
        sources: List[SourceCitationSchema] = []
        current_len = 0

        for chunk in retrieved_chunks:
            text = (chunk.get("text") or "").strip()
            if not text:
                continue

            doc_id = str(chunk.get("document_id", "unknown"))
            fname = str(chunk.get("filename", "unknown"))
            page = chunk.get("page")
            chunk_id = chunk.get("chunk_id", 0)
            file_hash = chunk.get("file_hash", "")
            score = chunk.get("score")

            header = f"[Source: {fname} | Chunk #{chunk_id}]"
            block = f"{header}\n{text}"
            block_len = len(block) + 2

            # Enforce max context length limit
            if current_len + block_len > self.max_context_length and context_blocks:
                break

            context_blocks.append(block)
            current_len += block_len

            sources.append(
                SourceCitationSchema(
                    document_id=doc_id,
                    filename=fname,
                    page=page if isinstance(page, int) else None,
                    chunk_id=chunk_id,
                    file_hash=file_hash if isinstance(file_hash, str) else None,
                    score=score if isinstance(score, float) else None,
                    snippet=text[:150] + "..." if len(text) > 150 else text,
                )
            )

        context_text = "\n\n".join(context_blocks)
        has_context = len(context_blocks) > 0

        grounded_prompt = self._format_prompt(context_text, query)

        return BuiltContext(
            context_text=context_text,
            sources=sources,
            has_sufficient_context=has_context,
            grounded_prompt=grounded_prompt,
        )

    def _format_prompt(self, context_text: str, query: str) -> str:
        """Format final grounded prompt string combining system instructions, context, and user question."""
        if not context_text:
            context_text = "[No relevant document chunks found in vector store]"

        system_part = GROUNDED_SYSTEM_PROMPT_TEMPLATE.format(context_text=context_text)
        return f"{system_part}\n\nUSER QUESTION: {query}\n\nGROUNDED ANSWER:"

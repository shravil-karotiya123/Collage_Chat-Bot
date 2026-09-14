"""
Intent Classification Engine for MRPL AI Workbench.
Classifies user prompts and context payloads into 10 distinct operational intents.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class UserIntent(str, Enum):
    """
    Standardized operational intent classification tags.
    """

    GENERAL_CHAT = "GENERAL_CHAT"
    DOCUMENT = "DOCUMENT"
    APPROVAL_NOTE = "APPROVAL_NOTE"
    SUMMARIZATION = "SUMMARIZATION"
    CODING = "CODING"
    DEBUGGING = "DEBUGGING"
    IMAGE = "IMAGE"
    OCR = "OCR"
    DIAGRAM = "DIAGRAM"
    UNKNOWN = "UNKNOWN"


@dataclass
class ClassificationResult:
    """
    Structured outcome of intent classification analysis.
    """

    intent: UserIntent
    confidence: float
    matched_rule: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentClassifier:
    """
    Production-grade Intent Classifier evaluating text features, regex patterns,
    keywords, and request context to categorize operational intent.
    """

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif", ".svg"}
    DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".csv", ".txt", ".pptx"}

    def __init__(self) -> None:
        self._initialize_pattern_rules()

    def _initialize_pattern_rules(self) -> None:
        """Initialize heuristic regex patterns and keyword rules for intent classification."""
        self.rules: List[Tuple[UserIntent, re.Pattern[str], float, str]] = [
            # OCR Patterns
            (
                UserIntent.OCR,
                re.compile(
                    r"\b(ocr|read\s+text|extract\s+text|transcribe\s+image|scanned\s+text|image\s+to\s+text|read\s+scanned)\b",
                    re.IGNORECASE,
                ),
                0.95,
                "ocr_keyword_pattern",
            ),
            # Diagram Analysis Patterns
            (
                UserIntent.DIAGRAM,
                re.compile(
                    r"\b(diagram|flowchart|architecture\s+diagram|schematic|p&id|pnd|block\s+diagram|uml|topology|process\s+flow)\b",
                    re.IGNORECASE,
                ),
                0.92,
                "diagram_keyword_pattern",
            ),
            # General Image Analysis Patterns
            (
                UserIntent.IMAGE,
                re.compile(
                    r"\b(image|picture|photo|snapshot|visual\s+inspection|describe\s+this\s+image|what\s+is\s+in\s+this|inspect\s+visual|visual\s+analysis)\b",
                    re.IGNORECASE,
                ),
                0.88,
                "image_keyword_pattern",
            ),
            # Debugging Patterns
            (
                UserIntent.DEBUGGING,
                re.compile(
                    r"\b(debug|stack\s*trace|traceback|exception|error\s+log|fix\s+bug|failing\s+test|syntaxerror|typeerror|nullpointer|bug\s+in|troubleshoot\s+code|why\s+is\s+this\s+failing)\b",
                    re.IGNORECASE,
                ),
                0.93,
                "debugging_keyword_pattern",
            ),
            # Coding Patterns
            (
                UserIntent.CODING,
                re.compile(
                    r"```|\b(code|python|javascript|function|class\s+\w+|script|sql\s+query|api\s+endpoint|algorithm|implement|refactor|unit\s+test|write\s+a\s+program|def\s+\w+|import\s+\w+)\b",
                    re.IGNORECASE,
                ),
                0.90,
                "coding_keyword_pattern",
            ),
            # Approval Note Patterns
            (
                UserIntent.APPROVAL_NOTE,
                re.compile(
                    r"\b(approval\s+note|note\s+sheet|sanction\s+note|financial\s+approval|management\s+approval|inter-office\s+memo|iom|concurrence\s+note|proposal\s+for\s+approval)\b",
                    re.IGNORECASE,
                ),
                0.95,
                "approval_note_pattern",
            ),
            # Summarization Patterns
            (
                UserIntent.SUMMARIZATION,
                re.compile(
                    r"\b(summarize|summary|tl;?dr|brief\s+summary|key\s+takeaways|gist|condense|executive\s+summary|overview\s+of)\b",
                    re.IGNORECASE,
                ),
                0.90,
                "summarization_pattern",
            ),
            # Document Processing Patterns
            (
                UserIntent.DOCUMENT,
                re.compile(
                    r"\b(document|docx|pdf|report\s+template|word\s+doc|excel\s+sheet|memo\s+draft|draft\s+document|formal\b.*report)\b",
                    re.IGNORECASE,
                ),
                0.85,
                "document_pattern",
            ),
            # General Chat Patterns
            (
                UserIntent.GENERAL_CHAT,
                re.compile(
                    r"\b(hello|hi|hey|good\s+morning|good\s+afternoon|who\s+are\s+you|what\s+can\s+you\s+do|tell\s+me|explain|what\s+is|how\s+does|chat|thanks|thank\s+you)\b",
                    re.IGNORECASE,
                ),
                0.75,
                "general_chat_pattern",
            ),
        ]

    def classify(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        """
        Classify user prompt and optional contextual parameters into a UserIntent.

        Args:
            request: The prompt string.
            context: Context details (e.g., file paths, mime types, image flags).

        Returns:
            ClassificationResult containing UserIntent, confidence score, and match reasoning.
        """
        ctx = context or {}
        cleaned_request = (request or "").strip()

        # Handle empty/blank request edge case
        if not cleaned_request and not ctx:
            return ClassificationResult(
                intent=UserIntent.UNKNOWN,
                confidence=0.0,
                matched_rule="empty_input_fallback",
                metadata={"reason": "No query or context provided"},
            )

        # 1. Explicit Context Overrides / File Attachment Indicators
        image_path = ctx.get("image_path") or ctx.get("file_path")
        has_image_flag = ctx.get("has_image", False)
        file_ext = ctx.get("file_extension", "").lower()

        if image_path and isinstance(image_path, str):
            for ext in self.IMAGE_EXTENSIONS:
                if image_path.lower().endswith(ext):
                    has_image_flag = True
                    break

        if has_image_flag or file_ext in self.IMAGE_EXTENSIONS:
            # Check prompt for specific Vision sub-intents (OCR vs Diagram vs general Image)
            if self._matches(request, r"\b(ocr|text|extract|read|scanned|transcribe)\b"):
                return ClassificationResult(
                    intent=UserIntent.OCR,
                    confidence=0.98,
                    matched_rule="context_image_ocr_override",
                    metadata={"has_image": True, "file_path": image_path},
                )
            if self._matches(request, r"\b(diagram|flowchart|schematic|p&id|pnd|block|architecture)\b"):
                return ClassificationResult(
                    intent=UserIntent.DIAGRAM,
                    confidence=0.98,
                    matched_rule="context_image_diagram_override",
                    metadata={"has_image": True, "file_path": image_path},
                )
            return ClassificationResult(
                intent=UserIntent.IMAGE,
                confidence=0.95,
                matched_rule="context_image_override",
                metadata={"has_image": True, "file_path": image_path},
            )

        # 2. Document file extension context check
        if file_ext in self.DOCUMENT_EXTENSIONS or ctx.get("is_document", False):
            if self._matches(request, r"\b(summarize|summary|gist|overview)\b"):
                return ClassificationResult(
                    intent=UserIntent.SUMMARIZATION,
                    confidence=0.95,
                    matched_rule="context_document_summarization",
                    metadata={"file_ext": file_ext},
                )
            return ClassificationResult(
                intent=UserIntent.DOCUMENT,
                confidence=0.90,
                matched_rule="context_document_override",
                metadata={"file_ext": file_ext},
            )

        # 3. Rule / Pattern Matching Engine
        matched_results: List[Tuple[UserIntent, float, str]] = []
        for intent, pattern, base_confidence, rule_name in self.rules:
            if pattern.search(cleaned_request):
                # Adjust confidence based on match specificity
                match_len = len(pattern.findall(cleaned_request))
                boosted_conf = min(0.99, base_confidence + (0.02 * (match_len - 1)))
                matched_results.append((intent, boosted_conf, rule_name))

        if matched_results:
            # Sort by highest confidence score
            matched_results.sort(key=lambda x: x[1], reverse=True)
            top_intent, top_confidence, top_rule = matched_results[0]
            return ClassificationResult(
                intent=top_intent,
                confidence=top_confidence,
                matched_rule=top_rule,
                metadata={"matches_count": len(matched_results)},
            )

        # 4. Heuristic Fallback for Code Snippets / Backticks
        if "```" in cleaned_request or "def " in cleaned_request or "class " in cleaned_request:
            return ClassificationResult(
                intent=UserIntent.CODING,
                confidence=0.85,
                matched_rule="heuristic_code_syntax",
                metadata={"syntax_detected": True},
            )

        # 5. Default General Chat Fallback for valid textual inputs
        if len(cleaned_request) > 0:
            return ClassificationResult(
                intent=UserIntent.GENERAL_CHAT,
                confidence=0.60,
                matched_rule="default_general_chat_fallback",
                metadata={"input_length": len(cleaned_request)},
            )

        return ClassificationResult(
            intent=UserIntent.UNKNOWN,
            confidence=0.0,
            matched_rule="unknown_fallback",
            metadata={},
        )

    def _matches(self, text: str, pattern_str: str) -> bool:
        """Helper regex match checker."""
        return bool(re.search(pattern_str, text, re.IGNORECASE))

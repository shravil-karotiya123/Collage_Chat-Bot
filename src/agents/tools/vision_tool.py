"""
Vision & OCR Service Tool Adapter.
Delegates image, scanned document, and diagram inspection to existing OCRService (MiniCPM-V 8B).
"""

import time
from typing import Any, Dict, Optional

from src.agents.agent_types import ToolRiskLevel
from src.agents.tool import BaseTool
from src.agents.tool_result import ToolResult
from src.ocr.ocr_service import OCRService


class VisionTool(BaseTool):
    """
    Agent tool adapter wrapping OCR and multimodal vision analysis.
    """

    name: str = "vision_tool"
    description: str = "Extract OCR text or perform multimodal vision analysis on images, diagrams, and scanned pages."
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    requires_approval: bool = False

    def __init__(self, ocr_service: Optional[OCRService] = None) -> None:
        self.ocr_service = ocr_service or OCRService()

    async def execute(self, task_id: str, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.perf_counter()
        image_bytes = parameters.get("image_bytes") or parameters.get("content_bytes") or b""
        if isinstance(image_bytes, str):
            image_bytes = image_bytes.encode("utf-8")

        filename = parameters.get("filename", "image.png")
        prompt = parameters.get("prompt") or parameters.get("query")

        try:
            analysis_dict = self.ocr_service.process_image(
                image_bytes=image_bytes,
                filename=filename,
                prompt=prompt,
            )
            exec_time = time.perf_counter() - start_time

            return ToolResult(
                success=True,
                tool_name=self.name,
                task_id=task_id,
                data={
                    "filename": analysis_dict.get("filename", filename),
                    "visual_analysis": analysis_dict.get("visual_analysis", ""),
                    "model_used": analysis_dict.get("model_used", "minicpm-v:8b"),
                    "status": analysis_dict.get("status", "SUCCESS"),
                },
                execution_time_seconds=exec_time,
                metadata={"width": analysis_dict.get("width"), "height": analysis_dict.get("height")},
            )
        except Exception as exc:
            exec_time = time.perf_counter() - start_time
            return ToolResult(
                success=False,
                tool_name=self.name,
                task_id=task_id,
                error=str(exc),
                execution_time_seconds=exec_time,
            )

    def health(self) -> Dict[str, Any]:
        h = self.ocr_service.health()
        return {
            "name": self.name,
            "status": "healthy" if h.get("ocr_enabled") else "degraded",
            "risk_level": self.risk_level.value,
            "requires_approval": self.requires_approval,
            "ocr_details": h,
        }

"""
Document generation service interface definition.
"""

from typing import Any, Dict


class DocumentService:
    """
    Service layer contract for Word report and Excel spreadsheet automated generation.
    """

    async def generate_word_report(self, content_data: Dict[str, Any], template: str) -> str:
        """
        Contract for generating structured Word (.docx) documents.
        """
        raise NotImplementedError("Service interface contract only.")

    async def generate_excel_spreadsheet(self, table_data: Dict[str, Any], output_path: str) -> str:
        """
        Contract for generating Excel (.xlsx) financial or operational workbooks.
        """
        raise NotImplementedError("Service interface contract only.")

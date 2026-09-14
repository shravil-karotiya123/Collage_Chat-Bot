"""
Artifact Generation and Persistence Subsystem.
Provides local generation for DOCX, XLSX, PPTX, and Code deliverables.
"""

from src.artifacts.models import ArtifactMetadata, ArtifactType
from src.artifacts.manager import ArtifactManager

__all__ = ["ArtifactMetadata", "ArtifactType", "ArtifactManager"]

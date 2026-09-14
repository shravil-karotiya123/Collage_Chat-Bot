"""
Configurable Routing Rules for MRPL AI Workbench.
Maps operational UserIntents to corresponding local model managers.
Target Model Mappings:
- GENERAL_CHAT, DOCUMENT, APPROVAL_NOTE, SUMMARIZATION -> QwenManager (Qwen2.5-7B-Instruct)
- CODING, DEBUGGING -> CoderManager (Qwen2.5-Coder-7B-Instruct)
- IMAGE, DIAGRAM, OCR -> VisionManager (Qwen2.5-VL-3B-Instruct) / PaddleOCR
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from config.settings import settings
from src.routing.intent_classifier import UserIntent

if TYPE_CHECKING:
    from src.models.base_model import BaseModel


class RoutingRules:
    """
    Configurable Routing Rules mapping intent classifications to local BaseModel manager targets.
    Strictly isolated from network endpoints and direct Ollama APIs.
    """

    def __init__(
        self,
        custom_mappings: Optional[Dict[UserIntent, Union[Type[Any], Any]]] = None,
        cached_instances: bool = True,
    ) -> None:
        from src.models.coder_manager import CoderManager
        from src.models.qwen_manager import QwenManager
        from src.models.vision_manager import VisionManager

        self.cached_instances = cached_instances
        self._manager_instances: Dict[str, Any] = {}
        self._default_mappings: Dict[UserIntent, Type[Any]] = {
            UserIntent.GENERAL_CHAT: QwenManager,
            UserIntent.DOCUMENT: QwenManager,
            UserIntent.APPROVAL_NOTE: QwenManager,
            UserIntent.SUMMARIZATION: QwenManager,
            UserIntent.CODING: CoderManager,
            UserIntent.DEBUGGING: CoderManager,
            UserIntent.IMAGE: VisionManager,
            UserIntent.OCR: VisionManager,
            UserIntent.DIAGRAM: VisionManager,
            UserIntent.UNKNOWN: QwenManager,
        }
        self._mappings: Dict[UserIntent, Union[Type[Any], Any]] = dict(
            self._default_mappings
        )

        if custom_mappings:
            self._mappings.update(custom_mappings)

    def get_manager_type(self, intent: UserIntent) -> Any:
        """
        Get the BaseModel target manager class mapped to a specific intent.
        """
        from src.models.base_model import BaseModel
        from src.models.qwen_manager import QwenManager
        target = self._mappings.get(intent, self._mappings.get(UserIntent.UNKNOWN, QwenManager))
        if isinstance(target, BaseModel):
            return target.__class__
        return target

    def get_manager(self, intent: UserIntent) -> Any:
        """
        Resolve and return appropriate BaseModel manager instance for an intent.

        Args:
            intent: Categorized UserIntent.

        Returns:
            Instantiated BaseModel manager (QwenManager, CoderManager, or VisionManager).
        """
        from src.models.base_model import BaseModel
        from src.models.qwen_manager import QwenManager

        target = self._mappings.get(intent, self._mappings.get(UserIntent.UNKNOWN, QwenManager))

        if isinstance(target, BaseModel):
            return target

        manager_cls = target
        cls_name = manager_cls.__name__

        if self.cached_instances:
            if cls_name not in self._manager_instances:
                self._manager_instances[cls_name] = manager_cls()
            return self._manager_instances[cls_name]
        else:
            return manager_cls()

    def set_mapping(
        self,
        intent: UserIntent,
        target: Union[Type[BaseModel], BaseModel],
    ) -> None:
        """
        Dynamically update or override intent routing target.
        """
        self._mappings[intent] = target

    def reset_mappings(self) -> None:
        """Reset routing rules to default configuration."""
        self._mappings = dict(self._default_mappings)
        self._manager_instances.clear()

    def get_all_mappings(self) -> Dict[str, str]:
        """Return human-readable map of intents to model manager class names."""
        from src.models.base_model import BaseModel
        result = {}
        for intent, target in self._mappings.items():
            if isinstance(target, BaseModel):
                result[intent.value] = target.__class__.__name__
            else:
                result[intent.value] = target.__name__
        return result

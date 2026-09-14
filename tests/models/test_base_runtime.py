"""
Unit tests for BaseRuntime abstraction contract.
"""

import unittest
from typing import Any, Dict, List
from src.models.runtime.base_runtime import BaseRuntime


class MockRuntime(BaseRuntime):
    """Concrete mock class implementing BaseRuntime for test verification."""

    def load_model(self, model_name: str, **kwargs: Any) -> bool:
        return True

    def unload_model(self, model_name: str, **kwargs: Any) -> bool:
        return True

    def generate(self, prompt: str, model_name: str, **kwargs: Any) -> str:
        return f"Mock response for {model_name}: {prompt}"

    def health(self) -> Dict[str, Any]:
        return {"runtime": "mock", "available": True}

    def list_models(self) -> List[str]:
        return ["mock-model:7b"]


class TestBaseRuntime(unittest.TestCase):
    """Test suite verifying BaseRuntime abstract contract behavior."""

    def test_cannot_instantiate_abstract_base_runtime(self) -> None:
        """Verify that BaseRuntime cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseRuntime()  # type: ignore

    def test_mock_runtime_implementation(self) -> None:
        """Verify that concrete implementations of BaseRuntime satisfy interface methods."""
        runtime = MockRuntime()
        self.assertTrue(runtime.load_model("test-model"))
        self.assertTrue(runtime.unload_model("test-model"))
        self.assertEqual(runtime.generate("Hello", "test-model"), "Mock response for test-model: Hello")
        self.assertEqual(runtime.health(), {"runtime": "mock", "available": True})
        self.assertEqual(runtime.list_models(), ["mock-model:7b"])


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for BaseModel abstraction and runtime delegation.
"""

import unittest
from unittest.mock import MagicMock
from src.models.base_model import BaseModel
from src.models.runtime.base_runtime import BaseRuntime


class ConcreteModel(BaseModel):
    """Concrete model subclass for testing BaseModel delegation."""

    def get_metadata(self):
        return {"model_name": self.model_name, "family": "test"}


class TestBaseModel(unittest.TestCase):
    """Test suite verifying BaseModel behavior and runtime delegation."""

    def setUp(self) -> None:
        self.mock_runtime = MagicMock(spec=BaseRuntime)
        self.mock_runtime.load_model.return_value = True
        self.mock_runtime.unload_model.return_value = True
        self.mock_runtime.generate.return_value = "Generated text"
        self.mock_runtime.health.return_value = {
            "available": True,
            "installed_models": ["test-model:latest"],
            "gpu_enabled": True,
        }

        self.model = ConcreteModel(model_name="test-model:latest", runtime=self.mock_runtime)

    def test_load_delegates_to_runtime(self) -> None:
        """Verify load() delegates to runtime.load_model()."""
        result = self.model.load()
        self.assertTrue(result)
        self.assertTrue(self.model.is_loaded)
        self.mock_runtime.load_model.assert_called_once_with("test-model:latest")

    def test_unload_delegates_to_runtime(self) -> None:
        """Verify unload() delegates to runtime.unload_model()."""
        self.model.is_loaded = True
        result = self.model.unload()
        self.assertTrue(result)
        self.assertFalse(self.model.is_loaded)
        self.mock_runtime.unload_model.assert_called_once_with("test-model:latest")

    def test_generate_delegates_to_runtime(self) -> None:
        """Verify generate() delegates to runtime.generate()."""
        output = self.model.generate("Explain clean architecture")
        self.assertEqual(output, "Generated text")
        self.mock_runtime.generate.assert_called_once_with(
            prompt="Explain clean architecture",
            model_name="test-model:latest",
        )

    def test_health_structure(self) -> None:
        """Verify health() returns structured dictionary as required by Task 7."""
        health_data = self.model.health()
        self.assertIn("loaded", health_data)
        self.assertIn("available", health_data)
        self.assertIn("runtime_status", health_data)
        self.assertIn("gpu_available", health_data)
        self.assertIn("model_exists", health_data)
        self.assertTrue(health_data["model_exists"])


if __name__ == "__main__":
    unittest.main()

"""
Qwen 2.5 7B Local Model Integration Demo Script.

Demonstrates loading the local Qwen model into VRAM, generating an answer
for an operational query, printing the result, and evicting the model from VRAM.
"""

import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from src.models.qwen_manager import QwenManager
from utils.logger import logger


def main() -> None:
    """
    Execute Qwen local model inference workflow.
    """
    print("====================================================")
    print(" Sovereign Agentic AI Workbench - Qwen 2.5 7B Demo")
    print("====================================================")

    # 1. Initialize Qwen Manager using configured runtime
    qwen = QwenManager()
    print(f"\n[1] Initialized QwenManager for model: '{qwen.model_name}'")
    print(f"    Active Runtime: {settings.ACTIVE_RUNTIME}")
    print(f"    Ollama Base URL: {settings.OLLAMA_BASE_URL}")

    # 2. Check Health Status
    health_status = qwen.health()
    print(f"\n[2] Health Check Status:")
    print(f"    Available: {health_status.get('available')}")
    print(f"    Model Exists: {health_status.get('model_exists')}")

    # 3. Load Qwen into VRAM
    print(f"\n[3] Loading Qwen model '{qwen.model_name}' into memory/VRAM...")
    loaded = qwen.load()
    if not loaded:
        print("    [ERROR] Failed to load Qwen model into VRAM. Verify Ollama service.")
        return

    print("    [SUCCESS] Model loaded successfully.")

    # 4. Generate Response for Approval Note Query
    prompt = "Explain what an approval note is."
    print(f"\n[4] Submitting Query to Qwen:\n    Prompt: \"{prompt}\"")
    print("\n--- Model Generation Response ---")

    try:
        response = qwen.generate(prompt)
        print(response)
    except Exception as e:
        print(f"    [ERROR] Generation failed: {e}")
    finally:
        print("-----------------------------------")

        # 5. Unload Model from VRAM
        print(f"\n[5] Unloading Qwen model '{qwen.model_name}' from VRAM...")
        unloaded = qwen.unload()
        if unloaded:
            print("    [SUCCESS] Model evicted from VRAM. Resources released.")
        else:
            print("    [WARNING] Model eviction returned status False.")

    print("\n====================================================")
    print(" Qwen Demo Execution Completed Successfully")
    print("====================================================")


if __name__ == "__main__":
    main()

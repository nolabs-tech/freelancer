import asyncio
import aiohttp
import os
from typing import List, Dict, Any, Optional


class ReplicateProvider:
    """Replicate-based image generation provider using logo-diffusion"""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        self.base_url = "https://api.replicate.com/v1/predictions"
        self.model_version = "fofr/logo-diffusion"  # You can switch to any other model

    async def generate_text(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Not supported for image generation-only models"""
        raise NotImplementedError("ReplicateProvider does not support text generation")

    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Trigger image generation on Replicate"""
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": self.model_version,
            "input": {
                "prompt": prompt,
                "num_outputs": kwargs.get("num_outputs", 1),
                "guidance_scale": kwargs.get("guidance_scale", 7.5),
                "num_inference_steps": kwargs.get("steps", 50)
            }
        }

        async with aiohttp.ClientSession() as session:
            # Submit prediction
            async with session.post(self.base_url, headers=headers, json=payload) as resp:
                if resp.status != 201:
                    raise Exception(f"Failed to start prediction: {await resp.text()}")
                result = await resp.json()
                prediction_id = result["id"]

            # Poll for result
            poll_url = f"{self.base_url}/{prediction_id}"
            for _ in range(60):  # Poll for up to 5 minutes
                async with session.get(poll_url, headers=headers) as poll_resp:
                    poll_data = await poll_resp.json()

                    if poll_data["status"] == "succeeded":
                        return {
                            "image_urls": poll_data["output"],
                            "model": "replicate:logo-diffusion",
                            "prompt": prompt
                        }
                    elif poll_data["status"] == "failed":
                        raise Exception(f"Generation failed: {poll_data.get('error', 'Unknown error')}")

                await asyncio.sleep(5)

            raise Exception("Image generation timed out after polling")

from langchain_openai import ChatOpenAI
import os
from typing import TypedDict, List, Dict, Any, Optional, Protocol
from langchain_core.messages import HumanMessage, SystemMessage

class OpenAIProvider:
    """OpenAI LLM Provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = ChatOpenAI(
            openai_api_key=self.api_key,
            model=self.model,
            temperature=0.7
        )
        
    async def generate_text(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text using OpenAI"""
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                formatted_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
        
        response = self.client.invoke(formatted_messages)
        return response.content
    
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image using DALL-E 3"""
        import openai
        
        client = openai.OpenAI(api_key=self.api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=kwargs.get("size", "1024x1024"),
            quality=kwargs.get("quality", "hd"),
            n=1,
        )
        
        return {
            "image_url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt,
            "model": "dall-e-3"
        }
    
    async def analyze_image(self, image_url: str, prompt: str, **kwargs) -> str:
        """Analyze image using GPT-4 Vision"""
        vision_client = ChatOpenAI(
            openai_api_key=self.api_key,
            model="gpt-4-vision-preview"
        )
        
        messages = [
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]
        
        response = vision_client.invoke(messages)
        return response.content
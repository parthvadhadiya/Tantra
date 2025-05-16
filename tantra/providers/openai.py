from typing import AsyncGenerator
from openai import OpenAI, AsyncOpenAI
from ..llm import BaseLLM, LLMConfig

class OpenAILLM(BaseLLM):
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.async_client = AsyncOpenAI(api_key=config.api_key)
        
    async def chat(self, prompt: str, **kwargs) -> str:
        response = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            **{**self.config.extra_config, **kwargs}
        )
        return response.choices[0].message.content
    
    async def stream_chat(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        stream = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **{**self.config.extra_config, **kwargs}
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

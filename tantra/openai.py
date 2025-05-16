import openai
from .llm import BaseLLM

class OpenAILLM(BaseLLM):
    def __init__(self, api_key, model="gpt-4o"):
        openai.api_key = api_key
        self.model = model
    
    def chat(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

from tantra.agent import Agent
from tantra.llm import BaseLLM
from tantra.session import Session
from tantra.context import Context

class EchoLLM(BaseLLM):
    def chat(self, prompt: str) -> str:
        return f"Echo: {prompt}"

class SimpleAgent(Agent):
    def on_event(self, event):
        if event["type"] == "USER_MESSAGE":
            prompt = f"{self.instructions}\n{event['content']}"
            response = self.llm.chat(prompt)
            return response

llm = EchoLLM()
agent = SimpleAgent(llm, instructions="Respond politely to the user.")
session = Session(agent, Context(user_id="123"))

print(session.send("Hello, Tantra!"))

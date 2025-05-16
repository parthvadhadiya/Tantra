from typing import TYPE_CHECKING, Optional
from .context import Context

if TYPE_CHECKING:
    from .agent import Agent

class Session:
    def __init__(self, agent: 'Agent', context: Context = None):
        self.agent = agent
        self.context = context or Context()
        agent.attach_session(self)
        
    async def say(self, message: str) -> None:
        """Send a message from the agent to the user"""
        # Add a newline after each message for better readability
        print(message, flush=True)
        
    async def send(self, message: str) -> Optional[str]:
        """Send a message from the user to the agent"""
        event = {"type": "USER_MESSAGE", "content": message, "context": self.context}
        return await self.agent.on_event(event)

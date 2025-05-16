from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ToolParameter(BaseModel):
    name: str
    value: Any
    collected_at: datetime = Field(default_factory=datetime.now)

class ToolParameterStore(BaseModel):
    tool_name: str
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.now)
    
    def add_parameter(self, name: str, value: Any) -> None:
        self.parameters[name] = ToolParameter(
            name=name,
            value=value
        )
    
    def get_parameter(self, name: str) -> Optional[Any]:
        param = self.parameters.get(name)
        return param.value if param else None
    
    def has_parameter(self, name: str) -> bool:
        return name in self.parameters
    
    def get_all_parameters(self) -> Dict[str, Any]:
        return {name: param.value for name, param in self.parameters.items()}
    
    def clear(self) -> None:
        self.parameters.clear()

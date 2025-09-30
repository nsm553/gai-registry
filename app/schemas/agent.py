
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AgentBase(BaseModel):
    agent_name: str
    workload_name: Optional[str] = None
    environment: str
    status: str
    trust_score: Optional[float] = None
    compliance_status: Optional[str] = None
    models_in_use: Optional[dict] = None  # JSONB field
    mcp_connectivity_status: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    agent_name: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None

class AgentInDB(AgentBase):
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Agent(AgentInDB):
    pass

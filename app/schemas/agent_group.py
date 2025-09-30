
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class AgentGroupBase(BaseModel):
    group_name: str
    description: Optional[str] = None

class AgentGroupCreate(AgentGroupBase):
    pass

class AgentGroupInDB(AgentGroupBase):
    group_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AgentGroup(AgentGroupInDB):
    pass

class AgentGroupMemberBase(BaseModel):
    group_id: int
    agent_id: int
    role_in_group: Optional[str] = None

class AgentGroupMemberCreate(AgentGroupMemberBase):
    pass

class AgentGroupMemberInDB(AgentGroupMemberBase):
    class Config:
        orm_mode = True

class AgentGroupMember(AgentGroupMemberInDB):
    pass

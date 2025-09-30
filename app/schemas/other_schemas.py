
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class AgentConnectionBase(BaseModel):
    agent_id: int
    protocol: str
    endpoint: str
    connection_meta: Optional[dict] = None
    last_seen_at: Optional[datetime] = None
    connection_state: Optional[str] = None

class AgentConnectionCreate(AgentConnectionBase):
    pass

class AgentConnectionInDB(AgentConnectionBase):
    connection_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AgentConnection(AgentConnectionInDB):
    pass

class AgentSessionBase(BaseModel):
    agent_id: int
    session_type: str
    started_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    session_meta: Optional[dict] = None

class AgentSessionCreate(AgentSessionBase):
    pass

class AgentSessionInDB(AgentSessionBase):
    session_id: UUID

    class Config:
        orm_mode = True

class AgentSession(AgentSessionInDB):
    pass

class AgentMessageBase(BaseModel):
    session_id: Optional[UUID] = None
    agent_id: int
    protocol: str
    direction: str
    message_type: str
    payload: Optional[dict] = None
    detected_at: Optional[datetime] = None
    processed: Optional[bool] = False

class AgentMessageCreate(AgentMessageBase):
    pass

class AgentMessageInDB(AgentMessageBase):
    message_id: int

    class Config:
        orm_mode = True

class AgentMessage(AgentMessageInDB):
    pass

class TrustScoreHistoryBase(BaseModel):
    agent_id: int
    old_score: float
    new_score: float
    reason: Optional[str] = None
    change_context: Optional[dict] = None

class TrustScoreHistoryCreate(TrustScoreHistoryBase):
    pass

class TrustScoreHistoryInDB(TrustScoreHistoryBase):
    history_id: int
    changed_at: datetime

    class Config:
        orm_mode = True

class TrustScoreHistory(TrustScoreHistoryInDB):
    pass

class EnforcementActionBase(BaseModel):
    event_id: Optional[int] = None
    agent_id: int
    policy_id: Optional[int] = None
    opa_decision: Optional[dict] = None
    executed_actions: Optional[dict] = None
    requested_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    executor: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class EnforcementActionCreate(EnforcementActionBase):
    pass

class EnforcementActionInDB(EnforcementActionBase):
    action_id: int

    class Config:
        orm_mode = True

class EnforcementAction(EnforcementActionInDB):
    pass


from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import UUID

from app.database.database import Base

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    workload_name = Column(String)
    environment = Column(String)
    status = Column(String)
    trust_score = Column(DECIMAL(5, 2))
    compliance_status = Column(String)
    models_in_use = Column(JSON)
    mcp_connectivity_status = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    connections = relationship("AgentConnection", back_populates="agent")
    sessions = relationship("AgentSession", back_populates="agent")
    messages = relationship("AgentMessage", back_populates="agent")
    trust_history = relationship("TrustScoreHistory", back_populates="agent")
    enforcement_actions = relationship("EnforcementAction", back_populates="agent")
    group_memberships = relationship("AgentGroupMember", back_populates="agent")

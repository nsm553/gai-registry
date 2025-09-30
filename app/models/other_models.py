
from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, JSON, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import UUID, uuid4

from app.database.database import Base

class AgentConnection(Base):
    __tablename__ = "agent_connections"

    connection_id = Column(BigInteger, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id", ondelete="CASCADE"))
    protocol = Column(String)
    endpoint = Column(String)
    connection_meta = Column(JSON)
    last_seen_at = Column(DateTime)
    connection_state = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    agent = relationship("Agent", back_populates="connections")

class AgentSession(Base):
    __tablename__ = "agent_sessions"

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    agent_id = Column(Integer, ForeignKey("agents.agent_id", ondelete="CASCADE"))
    session_type = Column(String)
    started_at = Column(DateTime, server_default=func.now())
    last_active_at = Column(DateTime)
    session_meta = Column(JSON)
    
    agent = relationship("Agent", foreign_keys=[agent_id], back_populates="sessions")
    messages = relationship("AgentMessage", back_populates="session")

class AgentMessage(Base):
    __tablename__ = "agent_messages"

    message_id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("agent_sessions.session_id", ondelete="SET NULL"))
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    protocol = Column(String)
    direction = Column(String)
    message_type = Column(String)
    payload = Column(JSON)
    # embedding = Column(VECTOR)  -- if using pgvector, uncomment this
    detected_at = Column(DateTime, server_default=func.now())
    processed = Column(Boolean, default=False)

    session = relationship("AgentSession", back_populates="messages")
    agent = relationship("Agent", foreign_keys=[agent_id], back_populates="messages")

class TrustScoreHistory(Base):
    __tablename__ = "trust_score_history"

    history_id = Column(BigInteger, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id", ondelete="CASCADE"))
    old_score = Column(DECIMAL(5, 2))
    new_score = Column(DECIMAL(5, 2))
    changed_at = Column(DateTime, server_default=func.now())
    reason = Column(String)
    change_context = Column(JSON)

    agent = relationship("Agent", back_populates="trust_history")

# Assuming anomaly_events and policies tables exist or will be created
class EnforcementAction(Base):
    __tablename__ = "enforcement_actions"

    action_id = Column(BigInteger, primary_key=True, index=True)
    event_id = Column(Integer) # REFERENCES anomaly_events(event_id) ON DELETE SET NULL,
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    policy_id = Column(Integer) # REFERENCES policies(policy_id),
    opa_decision = Column(JSON)
    executed_actions = Column(JSON)
    requested_at = Column(DateTime, server_default=func.now())
    executed_at = Column(DateTime)
    executor = Column(String)
    status = Column(String)
    notes = Column(Text)

    agent = relationship("Agent", back_populates="enforcement_actions")


from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class AgentGroup(Base):
    __tablename__ = "agent_groups"

    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    members = relationship("AgentGroupMember", back_populates="agent_group")

class AgentGroupMember(Base):
    __tablename__ = "agent_group_members"

    group_id = Column(Integer, ForeignKey("agent_groups.group_id", ondelete="CASCADE"), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id", ondelete="CASCADE"), primary_key=True)
    role_in_group = Column(String)

    agent_group = relationship("AgentGroup", back_populates="members")
    agent = relationship("Agent", back_populates="group_memberships")

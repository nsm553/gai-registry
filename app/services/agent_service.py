
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.agent import Agent as DBAgent
from app.schemas.agent import AgentCreate, AgentUpdate
from app.schemas.agent_group import AgentGroup, AgentGroupMember
from app.schemas.all_schemas import *

class AgentService:
    def get_agent(self, db: Session, agent_id: int) -> Optional[DBAgent]:
        return db.query(DBAgent).filter(DBAgent.agent_id == agent_id).first()

    def get_agents(self, db: Session, skip: int = 0, limit: int = 100) -> List[DBAgent]:
        return db.query(DBAgent).offset(skip).limit(limit).all()

    def get_agents_by_environment(self, db: Session, environment: str, skip: int = 0, limit: int = 100) -> List[DBAgent]:
        return db.query(DBAgent).filter(DBAgent.environment == environment).offset(skip).limit(limit).all()

    def create_agent(self, db: Session, agent: AgentCreate) -> DBAgent:
        db_agent = DBAgent(**agent.dict())
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent

    def update_agent(self, db: Session, agent_id: int, agent: AgentUpdate) -> Optional[DBAgent]:
        db_agent = db.query(DBAgent).filter(DBAgent.agent_id == agent_id).first()
        if db_agent:
            for key, value in agent.dict(exclude_unset=True).items():
                setattr(db_agent, key, value)
            db.commit()
            db.refresh(db_agent)
        return db_agent

    def delete_agent(self, db: Session, agent_id: int):
        db_agent = db.query(DBAgent).filter(DBAgent.agent_id == agent_id).first()
        if db_agent:
            db.delete(db_agent)
            db.commit()
            return True
        return False

agent_service = AgentService()

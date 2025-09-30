
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.agent import Agent as AgentSchema, AgentCreate, AgentUpdate
from app.services.agent_service import agent_service

router = APIRouter()

@router.post("/agents/", response_model=AgentSchema, status_code=status.HTTP_201_CREATED)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_service.create_agent(db=db, agent=agent)

@router.get("/agents/", response_model=List[AgentSchema])
def read_agents(skip: int = 0, limit: int = 100, environment: Optional[str] = None, db: Session = Depends(get_db)):
    if environment:
        agents = agent_service.get_agents_by_environment(db=db, environment=environment, skip=skip, limit=limit)
    else:
        agents = agent_service.get_agents(db=db, skip=skip, limit=limit)
    return agents

@router.get("/agents/{agent_id}", response_model=AgentSchema)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = agent_service.get_agent(db=db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.put("/agents/{agent_id}", response_model=AgentSchema)
def update_agent(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    db_agent = agent_service.update_agent(db=db, agent_id=agent_id, agent=agent)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    if not agent_service.delete_agent(db=db, agent_id=agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}

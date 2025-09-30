import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.models.all_models import *

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='module')
def override_get_db():
    try:
        db = SessionTesting()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope='session')
def client_fixture():
    with LifespanManager(app):
        with AsyncClient(base_url="http://test") as c:
            Base.metadata.create_all(bind=engine)
            yield c
            Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def test_create_agent(client):
    response = client.post(
        "/v1/agents/",
        json={
            "agent_name": "test_agent_1",
            "workload_name": "workload_A",
            "environment": "pre-prod",
            "status": "active",
            "trust_score": 0.95,
            "compliance_status": "compliant",
            "models_in_use": {"model1": "v1"},
            "mcp_connectivity_status": "connected",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["agent_name"] == "test_agent_1"
    assert "agent_id" in data

@pytest.fixture(scope='function')
def test_read_agents(client):
    response = client.get("/v1/agents/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

@pytest.fixture(scope='function')
def test_read_agent(client):
    create_response = client.post(
        "/v1/agents/",
        json={
            "agent_name": "test_agent_2",
            "workload_name": "workload_B",
            "environment": "prod",
            "status": "inactive",
            "trust_score": 0.70,
            "compliance_status": "non-compliant",
            "models_in_use": {"model2": "v1"},
            "mcp_connectivity_status": "disconnected",
        },
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["agent_id"]

    response = client.get(f"/v1/agents/{agent_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["agent_name"] == "test_agent_2"
    assert data["agent_id"] == agent_id

@pytest.fixture(scope='function')
def test_update_agent(client):
    create_response = client.post(
        "/v1/agents/",
        json={
            "agent_name": "test_agent_to_update",
            "workload_name": "workload_C",
            "environment": "pre-prod",
            "status": "active",
            "trust_score": 0.80,
            "compliance_status": "compliant",
            "models_in_use": {"model3": "v1"},
            "mcp_connectivity_status": "connected",
        },
    )
    assert create_response.status_code == 201
    agent_id = create_response.json()["agent_id"]

    update_data = {
        "status": "compromised",
        "trust_score": 0.10,
        "compliance_status": "non-compliant",
    }
    response = client.put(f"/v1/agents/{agent_id}", json=update_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "compromised"
    assert data["trust_score"] == 0.10

# @pytest.mark.asyncio
# async def test_delete_agent(client: AsyncClient):
#     create_response = await client.post(
#         "/v1/agents/",
#         json={
#             "agent_name": "test_agent_to_delete",
#             "workload_name": "workload_D",
#             "environment": "prod",
#             "status": "active",
#             "trust_score": 0.90,
#             "compliance_status": "compliant",
#             "models_in_use": {"model4": "v1"},
#             "mcp_connectivity_status": "connected",
#         },
#     )
#     assert create_response.status_code == 201
#     agent_id = create_response.json()["agent_id"]

#     response = await client.delete(f"/v1/agents/{agent_id}")
#     assert response.status_code == 204

#     get_response = await client.get(f"/v1/agents/{agent_id}")
#     assert get_response.status_code == 404

# @pytest.mark.asyncio
# async def test_read_agents_by_environment(client: AsyncClient):
#     await client.post(
#         "/v1/agents/",
#         json={
#             "agent_name": "env_test_preprod_1",
#             "workload_name": "workload_E",
#             "environment": "pre-prod",
#             "status": "active",
#             "trust_score": 0.85,
#             "compliance_status": "compliant",
#             "models_in_use": {},
#             "mcp_connectivity_status": "connected",
#         },
#     )
#     await client.post(
#         "/v1/agents/",
#         json={
#             "agent_name": "env_test_preprod_2",
#             "workload_name": "workload_E",
#             "environment": "pre-prod",
#             "status": "active",
#             "trust_score": 0.85,
#             "compliance_status": "compliant",
#             "models_in_use": {},
#             "mcp_connectivity_status": "connected",
#         },
#     )
#     await client.post(
#         "/v1/agents/",
#         json={
#             "agent_name": "env_test_prod_1",
#             "workload_name": "workload_F",
#             "environment": "prod",
#             "status": "active",
#             "trust_score": 0.99,
#             "compliance_status": "compliant",
#             "models_in_use": {},
#             "mcp_connectivity_status": "connected",
#         },
#     )

#     response_preprod = await client.get("/v1/agents/?environment=pre-prod")
#     assert response_preprod.status_code == 200
#     preprod_agents = response_preprod.json()
#     assert len(preprod_agents) >= 2
#     for agent in preprod_agents:
#         assert agent["environment"] == "pre-prod"

#     response_prod = await client.get("/v1/agents/?environment=prod")
#     assert response_prod.status_code == 200
#     prod_agents = response_prod.json()
#     assert len(prod_agents) >= 1
#     for agent in prod_agents:
#         assert agent["environment"] == "prod"

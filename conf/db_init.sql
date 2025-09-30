-- Create the database
CREATE USER guardu WITH PASSWORD 'gaiDBv25';
CREATE DATABASE gaidb;
GRANT ALL PRIVILEGES ON DATABASE gaidb TO guardu;
-- Use the database
\c gaidb;

CREATE TABLE agents (
  agent_id        SERIAL PRIMARY KEY,
  agent_name      VARCHAR(255) NOT NULL,
  workload_name   VARCHAR(255),
  environment     VARCHAR(50) CHECK (environment IN ('pre-prod','prod')),
  status          VARCHAR(50) CHECK (status IN ('active','inactive','compromised')),
  trust_score     DECIMAL(5,2),
  compliance_status VARCHAR(50) CHECK (compliance_status IN ('compliant','non-compliant')),
  models_in_use   JSONB,
  mcp_connectivity_status VARCHAR(50) CHECK (mcp_connectivity_status IN ('connected','disconnected')),
  created_at      TIMESTAMP DEFAULT NOW(),
  updated_at      TIMESTAMP DEFAULT NOW()
);

-- 1. Track agent groups / topology (logical).
CREATE TABLE agent_groups (
  group_id      SERIAL PRIMARY KEY,
  group_name    VARCHAR(255) NOT NULL,
  description   TEXT,
  created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_group_members (
  group_id INT REFERENCES agent_groups(group_id) ON DELETE CASCADE,
  agent_id INT REFERENCES agents(agent_id) ON DELETE CASCADE,
  role_in_group VARCHAR(100),
  PRIMARY KEY (group_id, agent_id)
);

-- 2. Agent connections: protocols & endpoints (one-to-many per agent)
CREATE TABLE agent_connections (
  connection_id   BIGSERIAL PRIMARY KEY,
  agent_id        INT REFERENCES agents(agent_id) ON DELETE CASCADE,
  protocol        VARCHAR(50) CHECK (protocol IN ('MCP','A2A','HTTPS','WS','GRPC','CUSTOM')),
  endpoint        VARCHAR(1024),          -- URL / address / topic / socket id
  connection_meta JSON,                  -- e.g., TLS fingerprint, cert id, client_id, region
  last_seen_at    TIMESTAMP,
  connection_state VARCHAR(50) CHECK (connection_state IN ('connected','disconnected','idle')),
  created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_agent_connections_agent_protocol ON agent_connections(agent_id, protocol);

-- 3. Sessions (logical conversation context)
CREATE TABLE agent_sessions (
  session_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id       INT REFERENCES agents(agent_id) ON DELETE CASCADE,
  session_type   VARCHAR(50) CHECK (session_type IN ('mcp_session','a2a_session','a2p_session','https_session')),
  started_at     TIMESTAMP DEFAULT NOW(),
  last_active_at TIMESTAMP,
  session_meta   JSONB
);
CREATE INDEX idx_sessions_agent_last_active ON agent_sessions(agent_id, last_active_at);

-- 4. High-throughput messages / traces (append-only, partitioned by time)
CREATE TABLE agent_messages (
  message_id     BIGSERIAL PRIMARY KEY,
  session_id     UUID REFERENCES agent_sessions(session_id) ON DELETE SET NULL,
  agent_id       INT REFERENCES agents(agent_id),
  protocol       VARCHAR(50),
  direction      VARCHAR(20) CHECK (direction IN ('inbound','outbound')),
  message_type   VARCHAR(100),            -- e.g., 'prompt','response','control','heartbeat'
  payload        JSON,                   -- full message/trace
--  embedding      VECTOR,                  -- optional (if using pgvector)
  detected_at    TIMESTAMP DEFAULT NOW(),
  processed     BOOLEAN DEFAULT FALSE
);
-- Partitioning recommended by time (see notes below)

-- 5. Trust score history (track changes over time)
CREATE TABLE trust_score_history (
  history_id    BIGSERIAL PRIMARY KEY,
  agent_id      INT REFERENCES agents(agent_id) ON DELETE CASCADE,
  old_score     DECIMAL(5,2),
  new_score     DECIMAL(5,2),
  changed_at    TIMESTAMP DEFAULT NOW(),
  reason        VARCHAR(255),
  change_context JSONB
);
CREATE INDEX idx_trust_history_agent_time ON trust_score_history(agent_id, changed_at DESC);

-- 6. Enforcement actions log - store OPA decision JSON and outcome
CREATE TABLE enforcement_actions (
  action_id       BIGSERIAL PRIMARY KEY,
  -- event_id        INT REFERENCES anomaly_events(event_id) ON DELETE SET NULL,
  event_id        INT,  
  agent_id        INT REFERENCES agents(agent_id),
  -- policy_id       INT REFERENCES policies(policy_id),
  policy_id       INT,  
  opa_decision    JSON,           -- raw OPA result
  executed_actions JSON,          -- what the enforcement controller actually did
  requested_at    TIMESTAMP DEFAULT NOW(),
  executed_at     TIMESTAMP,
  executor        VARCHAR(255),    -- service name or user id
  status          VARCHAR(50) CHECK (status IN ('pending','executed','failed','skipped')),
  notes           TEXT
);
CREATE INDEX idx_enforcement_agent_event ON enforcement_actions(agent_id,event_id);

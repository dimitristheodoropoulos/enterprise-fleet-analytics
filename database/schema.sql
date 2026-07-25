-- Enterprise Fleet Analytics — core schema
-- (Fixed: this file previously contained Python data-generation code by mistake;
--  it now holds the actual CREATE TABLE statements the rest of the project assumes exist.)

CREATE TABLE IF NOT EXISTS vessels (
    vessel_id       SERIAL PRIMARY KEY,
    vessel_name     VARCHAR(100) NOT NULL,
    vessel_type     VARCHAR(50) NOT NULL,
    capacity_dwt    NUMERIC(12, 2),
    year_built      INTEGER
);

CREATE TABLE IF NOT EXISTS telemetry_logs (
    telemetry_id            SERIAL PRIMARY KEY,
    vessel_id               INTEGER NOT NULL REFERENCES vessels(vessel_id),
    log_date                DATE NOT NULL,
    speed_knots             NUMERIC(6, 2),
    fuel_consumption_tons   NUMERIC(8, 2),
    wind_beaufort           INTEGER,
    cargo_weight_tons       NUMERIC(12, 2),
    route_status            VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS ai_chat_logs (
    chat_log_id     SERIAL PRIMARY KEY,
    user_question   TEXT,
    ai_response     TEXT,
    tool_called     VARCHAR(64),
    latency_seconds NUMERIC(6, 2),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

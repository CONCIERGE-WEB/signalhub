"""
SignalHub OS — plataforma determinística de sinais públicos (sem IA no Core).

signalhub/
  apps/           # MCP, API, CLI (interfaces)
  core/           # contracts, models (Signal), registry, orchestrator, pipeline
  providers/      # Scout, Dorking, Google, … (nunca chamam IA)
  rules/          # Rule Engine determinístico
  scoring/        # Score Engine determinístico
  notifications/  # Telegram Notification Adapter
  capabilities/   # produto → tools MCP
  storage/
  observability/
  security/

Ver docs/ARQUITETURA_P1_SINAIS.md
"""

# Scout Signals — Cliente Zero

Este plugin é o **teste definitivo do SDK**: a própria equipe usa só
`create` → `validate` → `doctor`, sem porta dos fundos no Core.

- Provider id registrado: `scout` (compatível com capabilities do Core)
- Até a coleta real: `search()` retorna vazio explícito
- ToS / rate limit / compliance da fonte: responsabilidade **deste** plugin
- Core: só orquestra Signals (RFC-0001)

Ver `docs/CLIENT_ZERO.md`.

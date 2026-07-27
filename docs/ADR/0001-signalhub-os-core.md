# ADR 0001 — SignalHub como OS com MCP como interface

## Status

Aceito (2026-07-27)

## Contexto

A missão pede uma plataforma modular (inteligência comercial/jurídica/mercado) com MCP, REST, CLI, Dashboard e SDKs sobre o mesmo Core — sem regras de negócio na camada MCP.

O repositório já tem `bot/`, `engine/`, `web/` em produção comercial (Business License). Reescrever tudo de uma vez quebraria o produto.

## Decisão

1. Criar o pacote `signalhub/` na raiz como **núcleo Clean Architecture**.
2. Interfaces em `signalhub/apps/*` apenas adaptam protocolo → Orchestrator.
3. Providers implementam contrato único; Dork Engine é um Provider.
4. Capabilities registradas no Core são projetadas automaticamente em Tools MCP.
5. Legado permanece; migração gradual com feature flag.
6. Licença atual permanece Business; open-source do núcleo MCP é decisão futura de produto (arquitetura preparada, sem marketing OSS prematuro).

## Consequências

- Dois contratos temporários (`engine.providers` e `signalhub.providers`) até o adapter P1.
- Stubs retornam vazio explícito — zero dados inventados.
- Observabilidade e SecurityPolicy desde o dia 1.

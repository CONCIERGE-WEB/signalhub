# SignalHub

**Build on Signals, not assumptions.**

Plataforma para descoberta, processamento e distribuição de **sinais públicos** —
determinística, auditável, extensível. Core **sem IA obrigatória**.

[![License: Business](https://img.shields.io/badge/license-Business-blue.svg)](./LICENSE)
[![Compliance](https://img.shields.io/badge/compliance-dados--publicos-green.svg)](./COMPLIANCE.md)
[![Status](https://img.shields.io/badge/status-commercial-orange.svg)](./PLANOS_E_PRECOS.md)

> Software **proprietário** com **Business License**.  
> Não é open source. Uso em produção exige assinatura comercial.

**Titular:** Tiago Aureliano da Rocha · CNPJ 61.699.939/0001-80 (Lex Rocha)

---

## Constituição

Antes de qualquer RFC, guia ou issue: o que o SignalHub **é** (e o que **não** é).

→ **[`docs/SIGNALHUB_SPECIFICATION.md`](./docs/SIGNALHUB_SPECIFICATION.md)**

> O SignalHub não coleta dados. Ele organiza evidências.  
> O SignalHub não toma decisões. Ele entrega sinais.  
> O SignalHub não substitui aplicações. Ele conecta aplicações a sinais públicos
> de forma determinística, auditável e extensível.

**Pergunta de plataforma:** *Como qualquer software pode consumir o SignalHub?*  
(Lex Rocha é um consumidor — não o único.)

---

## O que é

**Infraestrutura de sinais** (OS Core + Discovery Engine + Source Providers + REST/CLI/MCP/Dashboard).

O produto comercial histórico também opera como **robô de captação** em dados públicos
(alerta Telegram + painel), sempre com **humano no loop** — o software **não** envia
mensagens sozinho a desconhecidos. Isso é um *consumer path*, não a definição do Core.

Fluxo canônico:

```text
Source Providers → Discovery Engine → Core → Signals → REST / MCP / Dashboard / Telegram
                                                      → qualquer aplicação
```

Não é advocacia, não emite parecer jurídico e não substitui profissional habilitado.

---

## Módulos

| Módulo | Função |
|--------|--------|
| **Bot** | Monitoramento de fontes públicas, classificação e alerta no Telegram |
| **Engine** | Motor multi-contexto (regras, palavras-chave, varredura configurável) |
| **OS Core** | Pacote `signalhub/` — Core + Providers + Capabilities; interfaces MCP / REST / CLI. Ver `docs/ARQUITETURA_OS.md` |
| **Providers (legado)** | `engine/providers/` — scaffold Discovery; migração gradual para plugins |
| **Certification** | [`docs/PROVIDER_CERTIFICATION_PROGRAM.md`](./docs/PROVIDER_CERTIFICATION_PROGRAM.md) — Prospector → Dork → Google → GitHub (uma por vez) |
| **Open Source Compliance** | [`docs/OPEN_SOURCE_COMPLIANCE.md`](./docs/OPEN_SOURCE_COMPLIANCE.md) · [`docs/THIRD_PARTY_COMPONENTS.md`](./docs/THIRD_PARTY_COMPONENTS.md) — Scout (kiryano) = Source Provider MIT |
| **Specification** | Constituição: [`docs/SIGNALHUB_SPECIFICATION.md`](./docs/SIGNALHUB_SPECIFICATION.md) — identidade do projeto (não é RFC nem README) |
| **Web** | Qualificação assistida de contatos (IA + banco + notificação) |

---

## Licença Business

| | |
|--|--|
| **Modelo** | Assinatura comercial (`LICENSE`) |
| **Avaliação** | Leitura do código + demonstração local (prazo na licença) |
| **Produção** | Somente com plano ativo (`PLANOS_E_PRECOS.md`) |
| **Uso ético** | `COMPLIANCE.md` |

---

## Uso responsável (resumo)

- Apenas **dados públicos** e acessíveis sem autenticação indevida  
- **Revisão humana** antes de qualquer contato  
- Respeito à **LGPD**, ao Marco Civil e aos termos das plataformas  
- Sem promessa de resultado comercial ou jurídico  

Detalhes: [COMPLIANCE.md](./COMPLIANCE.md)

---

## Stack

Python (bot e motor) · Next.js (web) · IA (classificação) · Telegram (alertas) · Supabase (persistência do web)

```powershell
copy .env.example .env
.\signalhub.ps1 -Instalar
.\signalhub.ps1
```

Credenciais mestras na raiz (`.env`); sincronização: `scripts/sincronizar-env.ps1`.

Regras operacionais do robô (palavras-chave, varredura, prompts) **não ficam no Git** — só no cofre local da máquina (`E:\01_Projetos\_cofre`). No repositório há apenas `*.example`.

---

## Ecossistema

| Produto | Repositório |
|---------|-------------|
| SignalHub | este repositório |
| Lex Rocha Brasil | [lex-rocha-brasil](https://github.com/TiagoIA-UX/lex-rocha-brasil) |
| Lex Rocha Portugal | [lex-rocha-portugal](https://github.com/TiagoIA-UX/lex-rocha-portugal) |
| Judicial Intelligence (EUA) | [lex-rocha-estados-unidos](https://github.com/TiagoIA-UX/lex-rocha-estados-unidos) |

---

## Comercial

- [PLANOS_E_PRECOS.md](./PLANOS_E_PRECOS.md)  
- [LICENSE](./LICENSE)  
- [COMPLIANCE.md](./COMPLIANCE.md)

**© 2026 Tiago Aureliano da Rocha — SignalHub, licença business.**  
Todos os direitos reservados.

# Open Source Compliance

| Campo | Valor |
|-------|--------|
| **Milestone** | Open Source Compliance |
| **Status** | Concluída — provider parcial ligado (2026-07-29) |
| **Antes de** | PHASE 3.1 — First Certified Provider |
| **Repo** | `06-SignalHub` |

---

## Objetivo

Deixar o SignalHub sólido em **licença, branding e arquitetura** antes de
certificar ou incorporar qualquer Source Provider de terceiros.

---

## Checklist (4 itens)

- [x] Criar [`THIRD_PARTY_COMPONENTS.md`](./THIRD_PARTY_COMPONENTS.md)
- [x] Criar pasta [`third_party/`](../third_party/) para licenças de componentes incorporados (ou previstos)
- [x] Renomear o conceito arquitetural: ~~Scout (estratégia)~~ → **Discovery Engine** / **Prospector**
- [x] Documentar que **Scout (kiryano)** será Source Provider de terceiros quando integrado

---

## Branding canônico (após esta milestone)

```text
SignalHub
    ↓
Discovery Engine  (estratégia; plugin Prospector | Tiago A. Rocha)
    ↓
Source Providers
    ├── google_dork
    ├── reddit
    ├── scout_kiryano   ← kiryano/Scout (MIT) — plugins/scout_kiryano
    ├── github
    ├── websites
    ├── tiktok
    ├── instagram
    └── …
```

**Scout** deixa de ser nome de plataforma.  
**Scout (kiryano)** = um plugin de terceiros com crédito MIT.

---

## Próximo passo

Só depois desta milestone: **PHASE 3.1 — First Certified Provider**
(Discovery Engine / Prospector — sem incorporar kiryano/Scout ainda).

Constituição: [`SIGNALHUB_SPECIFICATION.md`](./SIGNALHUB_SPECIFICATION.md).

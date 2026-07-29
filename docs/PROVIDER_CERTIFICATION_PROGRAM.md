# Provider Certification Program

| Campo | Valor |
|-------|--------|
| **Milestone** | Provider Certification Program |
| **Status** | Documentado — implementação começa em **PHASE 3.1** |
| **Core** | **LOCKED** — nenhum Provider entra no sistema sem certificação |
| **Atualizado** | 2026-07-29 |
| **Repo** | `06-SignalHub` |
| **Constituição** | [`SIGNALHUB_SPECIFICATION.md`](./SIGNALHUB_SPECIFICATION.md) |

---

## 1. Princípio

A partir desta milestone, **nenhum Provider** pode ser considerado conectado à operação
sem passar pelo processo oficial de certificação.

- Trabalho de certificação e wiring real ocorre **somente no plugin** (fora do Core).
- **Nunca dois Providers ao mesmo tempo** na fila de certificação/implementação.
- Vazio explícito permanece obrigatório até o Provider estar **Certified Level 1**.

Documento-irmão: [`STABILITY_GUARANTEE.md`](./STABILITY_GUARANTEE.md) ·
contrato [`RFC/0001_SIGNAL_SPECIFICATION.md`](./RFC/0001_SIGNAL_SPECIFICATION.md).

---

## 2. Distinção conceitual — Discovery Engine ≠ fonte

Decisão arquitetural (2026-07-29) e branding Open Source Compliance:

| Conceito | Papel |
|----------|--------|
| **Discovery Engine** | Estratégia / mecanismo oficial de **descoberta** (orquestra prospecção) |
| **Prospector** | Cliente Zero da Discovery Engine (`prospector_tiagorocha`) |
| **Source Provider** | Implementação concreta de **uma** fonte (própria ou de terceiros) |
| **Scout (kiryano)** | Source Provider **de terceiros** ([kiryano/Scout](https://github.com/kiryano/Scout), MIT) — **não** é a estratégia |

```
SignalHub
    ↓
Discovery Engine  (Prospector | Tiago A. Rocha)
    ↓
Source Providers
├── Google Dork Provider
├── Reddit Provider
├── Reclame Aqui Provider
├── GitHub Provider
├── Websites Provider
├── Scout (kiryano)          ← terceiros MIT; crédito em third_party/
├── Social (TikTok · YouTube · Instagram · Facebook · …)
└── Future Providers…
```

- **Discovery Engine** não é uma fonte; **Scout (kiryano)** é uma fonte entre outras.
- Cada canal responde só pela sua fonte (ToS, rate-limit, parsing).
- Trocar uma fonte **não** reescreve a lógica da Discovery Engine.
- Plugin atual: `plugins/prospector_tiagorocha`. Layout alvo de plugins:
  `plugins/discovery/{scout_kiryano,google_dork,…}` quando houver integração.

Histórico (nome antigo “Scout” = estratégia): [`ARQUITETURA_PROVIDERS_SCOUT.md`](./ARQUITETURA_PROVIDERS_SCOUT.md).  
Compliance: [`OPEN_SOURCE_COMPLIANCE.md`](./OPEN_SOURCE_COMPLIANCE.md).

---

## 3. Inventário de superfícies sociais (consta nos documentos)

Além das fontes técnicas citadas na fila de certificação, o ecossistema **já prevê**
coleta em superfícies sociais públicas (sempre sob ToS + humano no loop):

| Superfície | Status documental |
|------------|-------------------|
| **TikTok** | Prevista / a certificar como Source Provider (não Core) |
| **YouTube** | Prevista / a certificar |
| **Instagram** | Prevista / a certificar |
| **Facebook** | Prevista / a certificar |
| Outras citadas depois | Entram na mesma fila — **uma por vez**, após Level 1 das anteriores |

Nenhuma dessas superfícies é “Certified” só por constar neste inventário.

---

## 4. Fila oficial de certificação (ordem irrevogável)

| Ordem | Alvo | Nível | Regra |
|-------|------|-------|--------|
| **1º** | **Discovery Engine (Dorking)** | Level 1 | **Certified** — PHASE 3.1 |
| **2º** | Source Providers oficiais (APIs) | Level 1 | Só após necessidade real — sem duplicar Dorking |
| **3º** | **Scout (kiryano)** | Level 1 | Terceiros MIT; NOTICE em `third_party/` |
| … | TikTok API · Instagram API · … | Level 1 | Uma por vez |

**Nunca dois ao mesmo tempo.**

> PHASE 3.1 renomeada: **First Certified Discovery Engine**  
> (não “First Certified Provider” genérico). Ver [`PHASE_3_1_DISCOVERY_ENGINE.md`](./PHASE_3_1_DISCOVERY_ENGINE.md).

### 4.1 Modelo de status (Discovery Engine / Dorking)

```text
Discovery Engine (Dorking)
Certification:
  LEVEL 1
  ✓ Contract
  ✓ Validator
  ✓ Rules
  ✓ Score
  ✓ Storage
  ✓ REST
  ✓ MCP
  ✓ Dashboard
  ✓ Telegram
Status: CERTIFIED
```

Live scan continua opt-in (`SIGNALHUB_DORKING_LIVE=1`); sem live = vazio explícito.---

## 5. Checklist Level 1 (obrigatório)

O Provider só pode ser marcado **Certified Level 1** quando cumprir **todos**:

- [ ] Respeita o contrato Signal **1.0.0**
- [ ] Passa pelo Signal Validator
- [ ] Não produz Signals inválidos
- [ ] Não quebra o Rule Engine
- [ ] Não quebra o Score Engine
- [ ] Produz Provenance completa
- [ ] Funciona no REST
- [ ] Funciona no MCP
- [ ] Funciona no Dashboard
- [ ] Funciona no Telegram Adapter
- [ ] Passa no `doctor --full`
- [ ] Passa em todos os testes de contrato

Comandos de blindagem (referência):

```powershell
cd C:\01_Projetos\06-SignalHub
python -m signalhub.apps.cli doctor --full
python -m signalhub.apps.cli contract-check
python -m signalhub.apps.cli validate plugins/prospector_tiagorocha
python -m signalhub.apps.cli test plugins/prospector_tiagorocha
```

---

## 6. Mission Control — campo Certification

O Mission Control / admin snapshot deve expor, por Provider:

| Campo | Exemplo |
|-------|---------|
| `certification.level` | `1` \| `null` |
| `certification.status` | `certified` \| `pending` \| `not_started` |
| `certification.label` | `Certified Level 1` \| `Pending Certification` |

Exibição:

```text
Discovery Engine (Prospector)
Status: Certified Level 1
```

ou

```text
Discovery Engine (Prospector)
Status: Pending Certification
```
Implementação do campo no snapshot = trabalho de **PHASE 3.1** (plugin + superfície de leitura),
**sem** abrir o Core para regras de negócio de fonte.

---

## 7. Provider Scorecard

Página alvo (web / dashboard SignalHub):

`/providers/prospector` (ou `/providers/discovery`)

Mostrar no mínimo:

- versão do plugin
- contrato Signal (`1.0.0`)
- cobertura (capabilities / checklist Level 1)
- sinais produzidos
- sinais descartados
- duplicados
- tempo médio
- regras aplicadas
- taxa de sucesso
- status de certificação

Scorecards de outros Providers (`/providers/dorking`, `/providers/google`, …)
só após o respectivo Level 1 — **nunca em paralelo** com o primeiro.

---

## 8. PHASE 3.1 — First Certified Provider (próximo trabalho)

> Prompt de execução (não iniciado neste documento — só registrado):

**[PHASE 3.1 — FIRST CERTIFIED PROVIDER]**

1. Core permanece **LOCKED**.
2. Transformar a **Discovery Engine / Prospector** no **primeiro** Provider oficialmente certificado.
3. Não conectar múltiplas fontes nesta fase (inclui **não** incorporar kiryano/Scout ainda).
4. Não adicionar funcionalidades novas ao Core.
5. Todo o trabalho no plugin + scorecard + Mission Control Certification.
6. Somente após **CERTIFIED Level 1** iniciar o próximo da fila (Dork Engine).

Estado atual (2026-07-29, auditoria local): plugin `prospector_tiagorocha` responde
`search not wired (empty explicit)` — **Pending Certification**, não Certified.

---

## 9. O que este documento não autoriza

- Ligar Discovery Engine real / Dork / Google / GitHub / Scout (kiryano) / redes
  **antes** da certificação Level 1 do item anterior na fila.
- Inventar Signals para “passar” o scorecard.
- Alterar Lex CDC (`09LexRocha-Br/signalhub-br`) sob o pretexto desta milestone.
- Abrir o Core para acomodar uma fonte específica.

/**
 * Adapter Web → SignalHub Core.
 * Sem regras de negócio: só transporte + estado vazio explícito.
 */

export type CoreSnapshot = {
  product: string;
  version: string;
  generated_at: string;
  status: string;
  providers: Array<{
    id: string;
    name: string;
    version: string;
    description: string;
    capabilities: string[];
    enabled: boolean;
    contract_version?: string;
    health: { ok: boolean; detail: string; latency_ms: number | null };
    certification?: Record<string, unknown>;
  }>;
  providers_enabled: string[];
  discovery_engine?: Record<string, unknown>;
  capabilities: Array<{
    id: string;
    name: string;
    description: string;
    provider_ids: string[];
    enabled: boolean;
    tool_name: string;
  }>;
  capability_explorer?: Array<Record<string, unknown>>;
  mcp_tools: Array<{ name: string; capability_id: string; description: string }>;
  metrics: Record<string, number>;
  platform_metrics?: Record<string, unknown>;
  integrity?: {
    components_loaded: Record<string, number>;
    versions: Record<string, string>;
    compatibility: Record<string, string | boolean>;
    warnings: string[];
    failures: string[];
    ok: boolean;
  };
  feature_flags: Record<string, boolean | string | number>;
  observability: Record<string, string>;
  security: Record<string, unknown>;
  config: Record<string, unknown>;
  adapter_detail?: string;
};

export type AdapterResult =
  | { ok: true; source: "http" | "unavailable"; snapshot: CoreSnapshot }
  | { ok: false; source: "error"; error: string; snapshot: CoreSnapshot };

function emptySnapshot(detail: string): CoreSnapshot {
  return {
    product: "signalhub",
    version: "unknown",
    generated_at: new Date().toISOString(),
    status: "unavailable",
    providers: [],
    providers_enabled: [],
    capabilities: [],
    capability_explorer: [],
    mcp_tools: [],
    metrics: {
      providers_total: 0,
      providers_healthy: 0,
      capabilities_total: 0,
      mcp_tools_total: 0,
    },
    integrity: {
      components_loaded: {},
      versions: { contract: "1.0.0" },
      compatibility: { rfc_0001: true },
      warnings: [detail],
      failures: [],
      ok: false,
    },
    feature_flags: { p2_platform_hardening: true },
    observability: {},
    security: {},
    config: { note: detail },
    adapter_detail: detail,
  };
}

export async function fetchCoreSnapshot(): Promise<AdapterResult> {
  const base = (process.env.SIGNALHUB_API_URL || process.env.NEXT_PUBLIC_SIGNALHUB_API_URL || "")
    .trim()
    .replace(/\/$/, "");

  if (!base) {
    const snapshot = emptySnapshot(
      "SIGNALHUB_API_URL não configurada — Core offline para este deploy. UI sem inventar dados.",
    );
    return { ok: true, source: "unavailable", snapshot };
  }

  try {
    const res = await fetch(`${base}/v1/admin/snapshot`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });
    if (!res.ok) {
      return {
        ok: false,
        source: "error",
        error: `HTTP ${res.status}`,
        snapshot: emptySnapshot(`Core respondeu HTTP ${res.status}`),
      };
    }
    const snapshot = (await res.json()) as CoreSnapshot;
    return { ok: true, source: "http", snapshot };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Falha de rede ao Core";
    return {
      ok: false,
      source: "error",
      error: msg,
      snapshot: emptySnapshot(msg),
    };
  }
}

function coreBase(): string {
  return (process.env.SIGNALHUB_API_URL || process.env.NEXT_PUBLIC_SIGNALHUB_API_URL || "")
    .trim()
    .replace(/\/$/, "");
}

export async function fetchMissionControl(): Promise<{
  ok: boolean;
  status: number;
  payload: Record<string, unknown>;
}> {
  const base = coreBase();
  if (!base) {
    return {
      ok: false,
      status: 503,
      payload: {
        product: "signalhub",
        phase: 1,
        core: { status: "unavailable", ok: false, version: "—" },
        contract: { version: "1.0.0", ok: true },
        rest: { status: "unavailable", ok: false },
        mcp: { status: "disabled", ok: false },
        cli: { status: "unknown", ok: false },
        dashboard: { status: "connected", ok: true, note: "Web mock / adapter unavailable" },
        storage: { status: "unavailable", ok: false, backend: "—" },
        telegram: { status: "unknown", ok: false },
        plugins: { ok: false, loaded: 0 },
        providers: [],
        metrics: { signals_today: 0, rules: 0, errors: 0, latency_ms: null },
        lab: {
          debug_provider: false,
          modes: [
            "valid",
            "invalid",
            "high_score",
            "low_score",
            "bad_url",
            "duplicate",
            "huge_metadata",
            "unknown_category",
            "bad_timestamp",
          ],
        },
        note: "Fase 1 — configure SIGNALHUB_API_URL (Core local) para Mission Control ao vivo.",
      },
    };
  }
  try {
    const res = await fetch(`${base}/v1/lab/mission-control`, { cache: "no-store" });
    const payload = (await res.json()) as Record<string, unknown>;
    return { ok: res.ok, status: res.status, payload };
  } catch (e) {
    return {
      ok: false,
      status: 503,
      payload: {
        error: e instanceof Error ? e.message : "mission-control unreachable",
      },
    };
  }
}

export async function executeCapability(
  id: string,
  body: Record<string, unknown>,
): Promise<{ status: number; payload: unknown }> {
  const base = coreBase();
  if (!base) {
    return {
      status: 503,
      payload: {
        error: "core_unavailable",
        detail: "Configure SIGNALHUB_API_URL para executar Capabilities.",
      },
    };
  }
  const res = await fetch(`${base}/v1/capabilities/${encodeURIComponent(id)}/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const payload = await res.json().catch(() => ({ error: "invalid_json" }));
  return { status: res.status, payload };
}

export async function labGenerate(
  mode: string,
  limit = 1,
): Promise<{ status: number; payload: unknown }> {
  const base = coreBase();
  if (!base) {
    return {
      status: 503,
      payload: {
        ok: false,
        error: "core_unavailable",
        detail: "Ligue o Core local e defina SIGNALHUB_API_URL (Fase 2).",
      },
    };
  }
  const res = await fetch(`${base}/v1/lab/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode, limit }),
    cache: "no-store",
  });
  const payload = await res.json().catch(() => ({ error: "invalid_json" }));
  return { status: res.status, payload };
}

export async function labReplay(
  signals: unknown[],
): Promise<{ status: number; payload: unknown }> {
  const base = coreBase();
  if (!base) {
    return {
      status: 503,
      payload: { ok: false, error: "core_unavailable" },
    };
  }
  const res = await fetch(`${base}/v1/lab/replay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ signals }),
    cache: "no-store",
  });
  const payload = await res.json().catch(() => ({ error: "invalid_json" }));
  return { status: res.status, payload };
}

export async function labExport(): Promise<{ status: number; payload: unknown }> {
  const base = coreBase();
  if (!base) {
    return { status: 503, payload: { ok: false, error: "core_unavailable" } };
  }
  const res = await fetch(`${base}/v1/lab/export`, { cache: "no-store" });
  const payload = await res.json().catch(() => ({ error: "invalid_json" }));
  return { status: res.status, payload };
}

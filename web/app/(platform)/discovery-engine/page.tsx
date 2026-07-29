import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";
import { PageHeader } from "@/components/layout/page-header";
import { Card, MetricCard } from "@/components/ui/cards";
import { StatusBadge } from "@/components/ui/badge";

export const dynamic = "force-dynamic";

type DiscoveryBlock = {
  name?: string;
  implementation?: string;
  certification?: {
    status?: string;
    label?: string;
    level?: number | null;
    sources_covered?: string[];
    note?: string;
  };
  health?: { ok?: boolean; detail?: string; latency_ms?: number | null };
  metrics?: Record<string, unknown>;
  error?: string;
};

export default async function DiscoveryEnginePage() {
  const { snapshot } = await fetchCoreSnapshot();
  const de =
    ((snapshot as { discovery_engine?: DiscoveryBlock }).discovery_engine as
      | DiscoveryBlock
      | undefined) || {};
  const cert = de.certification || {};
  const m = de.metrics || {};
  const origins = (m.origins as Record<string, number> | undefined) || {};
  const categories = (m.categories as Record<string, number> | undefined) || {};
  const sources = cert.sources_covered || [];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Discovery Engine"
        description="Dorking multi-fonte certificado — métricas reais do Core (sem dados fictícios)."
      />

      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge ok={cert.status === "certified"} label={cert.label || "Pending"} />
        <span className="text-sm text-mute">
          implementação: {de.implementation || "dorking"}
        </span>
      </div>

      {de.error ? (
        <Card>
          <p className="text-sm text-warn">{de.error}</p>
        </Card>
      ) : null}

      {!de.certification && snapshot.status === "unavailable" ? (
        <Card>
          <p className="text-sm text-mute">
            Core offline — configure SIGNALHUB_API_URL. Sem inventar métricas.
          </p>
        </Card>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Signals produzidos" value={Number(m.signals_produced ?? 0)} />
        <MetricCard label="Descartados" value={Number(m.signals_discarded ?? 0)} />
        <MetricCard label="Duplicados" value={Number(m.signals_duplicated ?? 0)} />
        <MetricCard
          label="Páginas consultadas"
          value={Number(m.pages_consulted ?? 0)}
          hint={m.last_run_at ? `última: ${String(m.last_run_at)}` : "sem execução live"}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="mb-2 text-sm font-medium text-ink">Health</h2>
          <p className="text-sm text-mute">{de.health?.detail || "—"}</p>
          <p className="mt-2 text-xs text-mute">
            tempo médio:{" "}
            {m.avg_ms != null ? `${Number(m.avg_ms).toFixed(1)} ms` : "—"}
          </p>
          <p className="mt-1 text-xs text-mute">
            live: {m.live_enabled ? "on" : "off"} · config:{" "}
            {m.config_path ? String(m.config_path) : "não resolvida"}
          </p>
        </Card>
        <Card>
          <h2 className="mb-2 text-sm font-medium text-ink">Fontes monitoradas (via Dorking)</h2>
          {sources.length === 0 ? (
            <p className="text-sm text-mute">vazio explícito</p>
          ) : (
            <ul className="flex flex-wrap gap-2">
              {sources.map((s) => (
                <li key={s} className="rounded border border-line px-2 py-0.5 text-xs text-mute">
                  {s}
                </li>
              ))}
            </ul>
          )}
          {cert.note ? <p className="mt-3 text-xs text-mute">{cert.note}</p> : null}
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="mb-2 text-sm font-medium text-ink">Distribuição por origem</h2>
          {Object.keys(origins).length === 0 ? (
            <p className="text-sm text-mute">0 — aguardando execução live</p>
          ) : (
            <ul className="space-y-1 text-sm text-mute">
              {Object.entries(origins).map(([k, v]) => (
                <li key={k} className="flex justify-between">
                  <span>{k}</span>
                  <span>{v}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <h2 className="mb-2 text-sm font-medium text-ink">Distribuição por categoria</h2>
          {Object.keys(categories).length === 0 ? (
            <p className="text-sm text-mute">0 — aguardando execução live</p>
          ) : (
            <ul className="space-y-1 text-sm text-mute">
              {Object.entries(categories).map(([k, v]) => (
                <li key={k} className="flex justify-between">
                  <span>{k}</span>
                  <span>{v}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}

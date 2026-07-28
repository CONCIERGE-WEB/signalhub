import { PageHeader } from "@/components/layout/page-header";
import { MetricCard, Card } from "@/components/ui/cards";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function MetricsPage() {
  const { snapshot } = await fetchCoreSnapshot();
  const m = snapshot.metrics || {};
  const p = (snapshot.platform_metrics || {}) as Record<string, unknown>;
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="observability"
        title="Métricas"
        description="Internas do Core (sem Prometheus). Ausência = zero explícito."
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard label="Signals produced" value={Number(m.signals_produced ?? p.signals_produced ?? 0)} />
        <MetricCard label="Signals discarded" value={Number(m.signals_discarded ?? p.signals_discarded ?? 0)} />
        <MetricCard label="Signals duplicated" value={Number(m.signals_duplicated ?? p.signals_duplicated ?? 0)} />
        <MetricCard label="Signals invalid" value={Number(m.signals_invalid ?? p.signals_invalid ?? 0)} />
        <MetricCard label="Rules applied" value={Number(m.rules_applied ?? p.rules_applied ?? 0)} />
        <MetricCard label="Providers healthy" value={`${m.providers_healthy ?? 0}/${m.providers_total ?? 0}`} />
      </div>
      <Card>
        <p className="font-mono text-[10px] uppercase text-mute">platform_metrics</p>
        <pre className="mt-3 overflow-auto text-xs text-mute">{JSON.stringify(p, null, 2)}</pre>
      </Card>
    </div>
  );
}

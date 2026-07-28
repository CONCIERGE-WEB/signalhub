import { PageHeader } from "@/components/layout/page-header";
import { MetricCard } from "@/components/ui/cards";
import { StatusBadge } from "@/components/ui/badge";
import { PipelineRiver } from "@/components/signal/pipeline-river";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const result = await fetchCoreSnapshot();
  const s = result.snapshot;
  const m = s.metrics || {};

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="platform"
        title="Dashboard"
        description="Janela para o Core. Sem regras de negócio nesta camada."
      />
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge
          ok={s.status === "ok"}
          label={`status ${s.status}`}
        />
        <StatusBadge
          ok={result.source === "http"}
          label={result.source === "http" ? "adapter http" : "core offline"}
        />
        <span className="font-mono text-[10px] text-mute">
          v{s.version} · {s.generated_at}
        </span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Providers" value={m.providers_total ?? 0} hint={`${m.providers_healthy ?? 0} healthy`} />
        <MetricCard label="Capabilities" value={m.capabilities_total ?? 0} />
        <MetricCard label="MCP tools" value={m.mcp_tools_total ?? 0} />
        <MetricCard
          label="Integrity"
          value={s.integrity?.ok ? "ok" : "check"}
          hint={s.integrity?.warnings?.[0] || s.adapter_detail || "—"}
        />
      </div>
      <PipelineRiver compact />
    </div>
  );
}

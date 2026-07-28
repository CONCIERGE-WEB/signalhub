import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";
import { StatusBadge } from "@/components/ui/badge";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function PluginsPage() {
  const { snapshot } = await fetchCoreSnapshot();
  const flags = snapshot.feature_flags || {};
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="sdk"
        title="Plugins"
        description="Cliente Zero e exemplos. Version negotiation recusa incompatíveis."
      />
      <div className="grid gap-3 md:grid-cols-2">
        {[
          {
            id: "prospector_tiagorocha",
            flag: "client_zero_prospector",
            note: "Prospector | Tiago A. Rocha · scaffold",
          },
          { id: "dork_signals", flag: "client_zero_dorking", note: "Dork Engine · scaffold" },
        ].map((p) => (
          <Card key={p.id}>
            <div className="flex items-center justify-between">
              <h3 className="font-display font-semibold">{p.id}</h3>
              <StatusBadge ok={Boolean(flags[p.flag])} label={flags[p.flag] ? "registered" : "n/a"} />
            </div>
            <p className="mt-2 text-sm text-mute">{p.note}</p>
            <p className="mt-3 font-mono text-[10px] text-mute">contract_version 1.0.0 · plugin.yaml</p>
          </Card>
        ))}
      </div>
      <Card>
        <p className="font-mono text-[10px] uppercase tracking-widest text-mute">feature flags</p>
        <pre className="mt-3 overflow-auto text-xs text-mute">
          {JSON.stringify(flags, null, 2)}
        </pre>
      </Card>
    </div>
  );
}

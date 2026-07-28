import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";

const ROUTES = [
  { method: "GET", path: "/health", desc: "Health monolítico" },
  { method: "GET", path: "/health/all", desc: "Health por superfície" },
  { method: "GET", path: "/v1/capabilities", desc: "Lista Capabilities" },
  { method: "POST", path: "/v1/capabilities/{id}/execute", desc: "Executa Capability" },
  { method: "GET", path: "/v1/admin/snapshot", desc: "Snapshot admin (Dashboard)" },
];

export default function RestPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="rest"
        title="REST Explorer"
        description="Superfície HTTP do Core. Configure SIGNALHUB_API_URL no deploy Web."
      />
      <div className="space-y-2">
        {ROUTES.map((r) => (
          <Card key={r.path} className="flex flex-wrap items-center gap-3">
            <span className="rounded bg-signal/15 px-2 py-0.5 font-mono text-[10px] text-signal">
              {r.method}
            </span>
            <code className="font-mono text-sm">{r.path}</code>
            <span className="text-xs text-mute">{r.desc}</span>
          </Card>
        ))}
      </div>
      <Card>
        <p className="font-mono text-[10px] uppercase text-mute">curl</p>
        <pre className="mt-3 overflow-auto text-xs text-mute">
{`curl "$SIGNALHUB_API_URL/v1/admin/snapshot"
curl -X POST "$SIGNALHUB_API_URL/v1/capabilities/discover_signals/execute" \\
  -H "content-type: application/json" \\
  -d '{"terms":["exemplo"],"limit":5}'`}
        </pre>
      </Card>
    </div>
  );
}

import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";
import { StatusBadge } from "@/components/ui/badge";

const RFCS = [
  { id: "0001", title: "Signal Specification", status: "accepted" as const, note: "Contrato canônico LOCKED." },
  { id: "0002", title: "Provider Specification", status: "planned" as const, note: "Plugin contract formal." },
  { id: "0003", title: "Capability Specification", status: "planned" as const, note: "Query/derive sem mutar storage." },
  { id: "0004", title: "Adapter Specification", status: "planned" as const, note: "Outbound notifications." },
  { id: "0005", title: "Notification Specification", status: "planned" as const, note: "Telegram e futuros canais." },
  { id: "0006", title: "Rule Engine Specification", status: "planned" as const, note: "Regras determinísticas." },
  { id: "0007", title: "Score Specification", status: "planned" as const, note: "Agregação e confidence." },
];

export default function RfcPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="specification"
        title="RFCs"
        description="Timeline do ecossistema. O Signal vem primeiro; o resto orbitam."
      />
      <ol className="relative space-y-4 border-l border-line pl-6">
        {RFCS.map((rfc) => (
          <li key={rfc.id} className="relative">
            <span className="absolute -left-[1.91rem] top-3 size-2.5 rounded-full border border-line bg-signal" />
            <Card>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs text-signal">RFC-{rfc.id}</span>
                <StatusBadge
                  ok={rfc.status === "accepted" ? true : undefined}
                  label={rfc.status}
                />
              </div>
              <h2 className="mt-2 font-display text-lg font-semibold">{rfc.title}</h2>
              <p className="mt-1 text-sm text-mute">{rfc.note}</p>
            </Card>
          </li>
        ))}
      </ol>
    </div>
  );
}

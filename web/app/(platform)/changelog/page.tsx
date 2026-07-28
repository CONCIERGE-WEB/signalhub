import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";

const NOTES = [
  {
    version: "1.0.0-web",
    date: "2026-07-27",
    items: [
      "Plataforma Web oficial: landing, portal, explorer, playground.",
      "Adapter → Core snapshot (sem inventar dados).",
      "Core permanece LOCKED — evolução só na camada Web.",
    ],
  },
  {
    version: "0.4.0-core",
    date: "2026-07-27",
    items: [
      "SDK, RFC-0001, Cliente Zero Scout+Dork (scaffold).",
      "Platform hardening: doctor --full, version negotiation, métricas internas.",
    ],
  },
];

export default function ChangelogPage() {
  return (
    <div className="space-y-8">
      <PageHeader eyebrow="release" title="Changelog" description="Notas curtas. Sem marketing vazio." />
      <div className="space-y-4">
        {NOTES.map((n) => (
          <Card key={n.version}>
            <div className="flex items-baseline justify-between gap-3">
              <h2 className="font-display text-lg font-semibold">{n.version}</h2>
              <span className="font-mono text-[10px] text-mute">{n.date}</span>
            </div>
            <ul className="mt-3 list-disc space-y-1 pl-4 text-sm text-mute">
              {n.items.map((i) => (
                <li key={i}>{i}</li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
}

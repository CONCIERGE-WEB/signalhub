import Link from "next/link";

import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";

const SECTIONS = [
  {
    id: "signal",
    title: "Signal Contract",
    body: "Tudo produz ou consome Signals. RFC-0001 define objeto canônico, lifecycle, validação, prioridade, confidence, rules, history, provenance e extensões.",
  },
  {
    id: "install",
    title: "Install",
    body: "pip install -e . · python -m signalhub.apps.cli doctor --full · validate plugins/<name>",
  },
  {
    id: "extend",
    title: "Extend",
    body: "Plugin SDK: create → implement → validate → doctor. Version negotiation no loader. Core LOCKED.",
  },
  {
    id: "surfaces",
    title: "Surfaces",
    body: "REST, CLI, MCP e Dashboard são projeções. Sem scraping no MCP. Sem regras Lex no Core.",
  },
];

export default function DocsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="docs"
        title="Documentação"
        description="Portal do protocolo. A especificação manda; o código referencia."
      />
      <div className="grid gap-6 lg:grid-cols-[12rem_1fr]">
        <nav className="space-y-1 text-sm">
          {SECTIONS.map((s) => (
            <a key={s.id} href={`#${s.id}`} className="block rounded px-2 py-1 text-mute hover:bg-panel hover:text-fog">
              {s.title}
            </a>
          ))}
          <Link href="/rfc" className="block rounded px-2 py-1 text-mute hover:bg-panel hover:text-fog">
            RFCs
          </Link>
          <Link href="/examples" className="block rounded px-2 py-1 text-mute hover:bg-panel hover:text-fog">
            Examples
          </Link>
        </nav>
        <div className="space-y-4">
          {SECTIONS.map((s) => (
            <Card key={s.id} id={s.id}>
              <h2 className="font-display text-lg font-semibold">{s.title}</h2>
              <p className="mt-2 text-sm text-mute">{s.body}</p>
            </Card>
          ))}
          <Card>
            <h2 className="font-display text-lg font-semibold">Stability</h2>
            <p className="mt-2 text-sm text-mute">
              Ver <code className="text-signal">docs/STABILITY_GUARANTEE.md</code> no repositório
              Core. Pacote pode versionar; contrato Signal 1.0.0 permanece.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}

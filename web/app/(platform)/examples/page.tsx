import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";

export default function ExamplesPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="dx"
        title="Examples"
        description="Hello, SignalHub — caminho curto até o primeiro Signal válido."
      />
      <Card>
        <h2 className="font-display font-semibold">Hello, SignalHub</h2>
        <pre className="mt-3 overflow-auto rounded-lg bg-panel p-3 font-mono text-[11px] text-mute">
{`# 1. Core
python -m signalhub.apps.cli doctor --full

# 2. Snapshot (Dashboard / Lex Adapter)
python -m signalhub.apps.cli admin-snapshot

# 3. Plugin scaffold
python -m signalhub.apps.cli create provider my_src
python -m signalhub.apps.cli validate plugins/my_src`}
        </pre>
      </Card>
      <Card>
        <h2 className="font-display font-semibold">Telegram adapter</h2>
        <p className="mt-2 text-sm text-mute">
          Formata Signal com ✔ rules_applied. Envio Bot API real é experimental — Core não scrapeia.
        </p>
      </Card>
      <Card>
        <h2 className="font-display font-semibold">Consumidor Lex Rocha</h2>
        <p className="mt-2 text-sm text-mute">
          Adapter local/http no Lex — zero regras SignalHub no site. Core permanece independente.
        </p>
      </Card>
    </div>
  );
}

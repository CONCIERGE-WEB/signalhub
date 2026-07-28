import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";
import { StatusBadge } from "@/components/ui/badge";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function IntegrityPage() {
  const { snapshot, source } = await fetchCoreSnapshot();
  const i = snapshot.integrity;
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="hardening"
        title="Integridade da Plataforma"
        description="Componentes, versões, contratos, warnings e falhas — do Core."
      />
      <StatusBadge ok={Boolean(i?.ok) && source === "http"} label={i?.ok ? "integro" : "verificar"} />
      <div className="grid gap-3 md:grid-cols-2">
        <Card>
          <p className="font-mono text-[10px] uppercase text-mute">versions</p>
          <pre className="mt-2 text-xs">{JSON.stringify(i?.versions || {}, null, 2)}</pre>
        </Card>
        <Card>
          <p className="font-mono text-[10px] uppercase text-mute">components</p>
          <pre className="mt-2 text-xs">{JSON.stringify(i?.components_loaded || {}, null, 2)}</pre>
        </Card>
      </div>
      <Card>
        <p className="font-medium text-warn">Warnings</p>
        <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-mute">
          {(i?.warnings || []).length === 0 ? <li>nenhum</li> : null}
          {(i?.warnings || []).map((w) => (
            <li key={w}>{w}</li>
          ))}
        </ul>
      </Card>
      <Card>
        <p className="font-medium text-fault">Failures</p>
        <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-mute">
          {(i?.failures || []).length === 0 ? <li>nenhuma</li> : null}
          {(i?.failures || []).map((f) => (
            <li key={f}>{f}</li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

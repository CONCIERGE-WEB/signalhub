import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/cards";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function McpPage() {
  const { snapshot } = await fetchCoreSnapshot();
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="mcp"
        title="MCP Tools"
        description="Projeção das Capabilities. Integração com Claude, Cursor e VS Code via stdio."
      />
      <Card>
        <p className="font-mono text-[10px] uppercase text-mute">connect</p>
        <pre className="mt-3 overflow-auto text-xs text-mute">
{`python -m signalhub.apps.cli mcp
# Claude / Cursor: aponte o MCP server stdio para o comando acima`}
        </pre>
      </Card>
      <ul className="space-y-2">
        {snapshot.mcp_tools.map((t) => (
          <li key={t.name}>
            <Card>
              <p className="font-mono text-sm text-signal">{t.name}</p>
              <p className="mt-1 text-xs text-mute">→ {t.capability_id}</p>
              <p className="mt-2 text-sm text-mute">{t.description}</p>
            </Card>
          </li>
        ))}
      </ul>
      {snapshot.mcp_tools.length === 0 ? (
        <p className="text-sm text-mute">Sem tools — Core offline.</p>
      ) : null}
    </div>
  );
}

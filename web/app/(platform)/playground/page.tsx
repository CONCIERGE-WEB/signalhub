import { PageHeader } from "@/components/layout/page-header";
import { PlaygroundClient } from "@/components/signal/explorer-playground";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function PlaygroundPage() {
  const { snapshot } = await fetchCoreSnapshot();
  const caps = snapshot.capabilities.map((c) => ({
    id: c.id,
    name: c.name,
    tool_name: c.tool_name,
  }));

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="playground"
        title="Playground"
        description="Executa Capabilities no Core. Sem IA. Request/Response reais ou erro explícito."
      />
      <PlaygroundClient capabilities={caps} />
    </div>
  );
}

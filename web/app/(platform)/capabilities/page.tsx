import { PageHeader } from "@/components/layout/page-header";
import { CapabilityCard } from "@/components/ui/cards";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function CapabilitiesPage() {
  const { snapshot } = await fetchCoreSnapshot();
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="protocol"
        title="Capabilities"
        description="Cada Capability é consulta/derivação — não muta Signal armazenado."
      />
      <div className="grid gap-3 md:grid-cols-2">
        {snapshot.capabilities.map((c) => (
          <CapabilityCard
            key={c.id}
            id={c.id}
            name={c.name}
            description={c.description}
            toolName={c.tool_name}
            providerIds={c.provider_ids}
          />
        ))}
      </div>
      {snapshot.capabilities.length === 0 ? (
        <p className="text-sm text-mute">Lista vazia — Core offline ou sem registry.</p>
      ) : null}
    </div>
  );
}

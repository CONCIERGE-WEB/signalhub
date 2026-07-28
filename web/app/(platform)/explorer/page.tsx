import { PageHeader } from "@/components/layout/page-header";
import { CapabilityExplorerClient } from "@/components/signal/explorer-playground";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function ExplorerPage() {
  const { snapshot } = await fetchCoreSnapshot();
  const items =
    (snapshot.capability_explorer as Array<Record<string, unknown>> | undefined)?.map((c) => ({
      id: String(c.id),
      name: String(c.name),
      description: String(c.description || ""),
      enabled: Boolean(c.enabled),
      provider_ids: (c.provider_ids as string[]) || [],
      contract_version: String(c.contract_version || "1.0.0"),
      permissions: (c.permissions as string[]) || [],
      parameters: (c.parameters as Record<string, unknown>) || {},
      example_input: (c.example_input as Record<string, unknown>) || {},
      example_output: (c.example_output as Record<string, unknown>) || {},
      rest_example: String(c.rest_example || ""),
      mcp_example: (c.mcp_example as Record<string, unknown>) || {},
      python_example: String(c.python_example || ""),
    })) ||
    snapshot.capabilities.map((c) => ({
      id: c.id,
      name: c.name,
      description: c.description,
      enabled: c.enabled,
      provider_ids: c.provider_ids,
      tool_name: c.tool_name,
      contract_version: "1.0.0",
    }));

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="dx"
        title="Capability Explorer"
        description="Estilo Swagger para o ecossistema SignalHub — documentação viva do Core."
      />
      <CapabilityExplorerClient items={items} />
    </div>
  );
}

import { PageHeader } from "@/components/layout/page-header";
import { ProviderCard } from "@/components/ui/cards";
import { fetchCoreSnapshot } from "@/lib/signalhub/adapter";

export const dynamic = "force-dynamic";

export default async function ProvidersPage() {
  const { snapshot } = await fetchCoreSnapshot();
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="registry"
        title="Providers"
        description="Health e versões vindos do Core. Scaffolds vazios são estado explícito."
      />
      {snapshot.providers.length === 0 ? (
        <p className="text-sm text-mute">
          Nenhum provider no snapshot. Configure SIGNALHUB_API_URL ou rode o Core local.
        </p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {snapshot.providers.map((p) => (
            <ProviderCard
              key={p.id}
              name={p.name}
              id={p.id}
              version={p.version}
              healthOk={p.health.ok}
              healthDetail={p.health.detail}
              capabilities={p.capabilities}
              enabled={p.enabled}
            />
          ))}
        </div>
      )}
    </div>
  );
}

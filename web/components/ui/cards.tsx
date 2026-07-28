import { cn } from "@/lib/cn";
import { HealthIndicator } from "@/components/ui/badge";

export function Card({
  children,
  className,
  id,
}: {
  children: React.ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <div
      id={id}
      className={cn("rounded-xl border border-line bg-ink/80 p-4 shadow-signal", className)}
    >
      {children}
    </div>
  );
}

export function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <Card>
      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-mute">{label}</p>
      <p className="mt-2 font-display text-3xl font-semibold tracking-tight text-fog">{value}</p>
      {hint ? <p className="mt-1 text-xs text-mute">{hint}</p> : null}
    </Card>
  );
}

export function ProviderCard({
  name,
  id,
  version,
  healthOk,
  healthDetail,
  capabilities,
  enabled,
}: {
  name: string;
  id: string;
  version: string;
  healthOk: boolean;
  healthDetail: string;
  capabilities: string[];
  enabled: boolean;
}) {
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-base font-semibold text-fog">{name}</h3>
          <p className="font-mono text-xs text-mute">{id}</p>
        </div>
        <span className="font-mono text-[10px] text-mute">v{version}</span>
      </div>
      <HealthIndicator ok={healthOk} detail={healthDetail} />
      <p className="text-xs text-mute">
        {enabled ? "enabled" : "disabled"} · contract 1.0.0
      </p>
      <div className="flex flex-wrap gap-1">
        {capabilities.length === 0 ? (
          <span className="text-xs text-mute">sem capabilities</span>
        ) : (
          capabilities.map((c) => (
            <span key={c} className="rounded border border-line bg-panel px-1.5 py-0.5 font-mono text-[10px] text-mute">
              {c}
            </span>
          ))
        )}
      </div>
    </Card>
  );
}

export function CapabilityCard({
  id,
  name,
  description,
  toolName,
  providerIds,
}: {
  id: string;
  name: string;
  description: string;
  toolName: string;
  providerIds: string[];
}) {
  return (
    <Card>
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-display text-base font-semibold">{name}</h3>
        <span className="font-mono text-[10px] text-signal">{toolName}</span>
      </div>
      <p className="mt-1 font-mono text-xs text-mute">{id}</p>
      <p className="mt-3 text-sm text-mute">{description}</p>
      <p className="mt-3 font-mono text-[10px] text-mute">
        providers: {providerIds.join(", ") || "—"}
      </p>
    </Card>
  );
}

export function SignalCard({
  title,
  provider,
  score,
  rules,
}: {
  title: string;
  provider: string;
  score?: number | null;
  rules?: string[];
}) {
  return (
    <Card>
      <p className="font-mono text-[10px] uppercase tracking-widest text-signal">signal</p>
      <h3 className="mt-1 font-display text-lg font-semibold">{title}</h3>
      <p className="mt-1 font-mono text-xs text-mute">{provider}</p>
      {score != null ? (
        <p className="mt-3 font-mono text-sm">
          score <span className="text-fog">{score}</span>
        </p>
      ) : null}
      {rules && rules.length > 0 ? (
        <ul className="mt-2 space-y-1 text-xs text-mute">
          {rules.map((r) => (
            <li key={r}>✔ {r}</li>
          ))}
        </ul>
      ) : null}
    </Card>
  );
}

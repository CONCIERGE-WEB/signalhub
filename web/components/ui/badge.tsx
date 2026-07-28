import { cn } from "@/lib/cn";

export function StatusBadge({
  ok,
  label,
  className,
}: {
  ok?: boolean;
  label: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide",
        ok === true && "border-valid/30 bg-valid/10 text-valid",
        ok === false && "border-fault/30 bg-fault/10 text-fault",
        ok === undefined && "border-line bg-panel text-mute",
        className,
      )}
    >
      <span
        className={cn(
          "size-1.5 rounded-full",
          ok === true && "bg-valid",
          ok === false && "bg-fault",
          ok === undefined && "bg-mute",
        )}
      />
      {label}
    </span>
  );
}

export function HealthIndicator({ ok, detail }: { ok: boolean; detail?: string }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <StatusBadge ok={ok} label={ok ? "healthy" : "degraded"} />
      {detail ? <span className="truncate font-mono text-mute">{detail}</span> : null}
    </div>
  );
}

export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <header className="space-y-2">
      {eyebrow ? (
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-signal">{eyebrow}</p>
      ) : null}
      <h1 className="font-display text-3xl font-semibold tracking-tight">{title}</h1>
      {description ? <p className="max-w-2xl text-sm text-mute">{description}</p> : null}
    </header>
  );
}

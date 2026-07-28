"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, MetricCard } from "@/components/ui/cards";
import { StatusBadge } from "@/components/ui/badge";
import { PageHeader } from "@/components/layout/page-header";

type Surface = { status?: string; ok?: boolean; detail?: string; note?: string; backend?: string };
type ProviderRow = {
  id: string;
  name: string;
  ok: boolean;
  detail: string;
  scaffold?: boolean;
  lab?: boolean;
};

function Dot({ ok, warn }: { ok?: boolean; warn?: boolean }) {
  const color = ok ? "bg-valid" : warn ? "bg-warn" : "bg-mute";
  return <span className={`inline-block size-2.5 rounded-full ${color}`} />;
}

export function MissionControlClient() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [mode, setMode] = useState("valid");
  const [out, setOut] = useState("");
  const [pending, setPending] = useState(false);
  const [replayJson, setReplayJson] = useState("");

  const load = useCallback(async () => {
    const res = await fetch("/api/core/mission-control", { cache: "no-store" });
    const json = await res.json();
    setData(json);
  }, []);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), 15000);
    return () => window.clearInterval(id);
  }, [load]);

  async function generate() {
    setPending(true);
    try {
      const res = await fetch("/api/core/lab/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, limit: mode === "duplicate" ? 2 : 1 }),
      });
      const json = await res.json();
      setOut(JSON.stringify(json, null, 2));
      await load();
    } finally {
      setPending(false);
    }
  }

  async function doExport() {
    setPending(true);
    try {
      const res2 = await fetch("/api/core/lab/export");
      const json = await res2.json();
      setOut(JSON.stringify(json, null, 2));
      setReplayJson(JSON.stringify(json.signals || [], null, 2));
    } finally {
      setPending(false);
    }
  }

  async function doReplay() {
    setPending(true);
    try {
      let signals: unknown[] = [];
      try {
        signals = JSON.parse(replayJson || "[]") as unknown[];
      } catch {
        setOut(JSON.stringify({ error: "JSON inválido" }, null, 2));
        return;
      }
      const res = await fetch("/api/core/lab/replay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ signals }),
      });
      const json = await res.json();
      setOut(JSON.stringify(json, null, 2));
      await load();
    } finally {
      setPending(false);
    }
  }

  const core = (data?.core || {}) as Surface & { version?: string };
  const contract = (data?.contract || {}) as { version?: string; ok?: boolean };
  const metrics = (data?.metrics || {}) as Record<string, number | null>;
  const providers = (data?.providers || []) as ProviderRow[];
  const plugins = (data?.plugins || {}) as { loaded?: number; ok?: boolean };
  const lab = (data?.lab || {}) as { modes?: string[]; debug_provider?: boolean };
  const modes = lab.modes || ["valid", "invalid", "high_score", "low_score"];

  const rows: Array<{ label: string; surface: Surface; warn?: boolean }> = [
    { label: "Core", surface: core },
    { label: "REST", surface: (data?.rest || {}) as Surface },
    { label: "MCP", surface: (data?.mcp || {}) as Surface, warn: true },
    { label: "CLI", surface: (data?.cli || {}) as Surface },
    { label: "Dashboard", surface: (data?.dashboard || {}) as Surface },
    { label: "Storage", surface: (data?.storage || {}) as Surface },
    { label: "Telegram", surface: (data?.telegram || {}) as Surface },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="laboratory"
        title="Mission Control"
        description="Valida a plataforma com sinais sintéticos. Sem Scout, Dork ou internet."
      />

      <Card className="font-mono text-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
          <p className="font-display text-lg font-semibold tracking-tight text-fog">SignalHub</p>
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            Refresh
          </Button>
        </div>
        <div className="mt-4 space-y-2">
          {rows.map((r) => (
            <div key={r.label} className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-2 text-mute">
                <Dot ok={r.surface.ok} warn={!r.surface.ok && r.warn} />
                {r.label}
              </span>
              <span className="text-fog">
                {r.surface.status || "—"}
                {r.label === "Core" && core.version ? ` · v${core.version}` : ""}
              </span>
            </div>
          ))}
          <div className="flex items-center justify-between gap-3 pt-2">
            <span className="flex items-center gap-2 text-mute">
              <Dot ok={contract.ok} />
              Contract
            </span>
            <span className="text-fog">{contract.version || "1.0.0"}</span>
          </div>
          <div className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-2 text-mute">
              <Dot ok={Boolean(plugins.ok)} />
              Plugins
            </span>
            <span className="text-fog">{plugins.loaded ?? 0} loaded</span>
          </div>
        </div>
        <div className="mt-6 space-y-2 border-t border-line pt-4">
          <p className="text-[10px] uppercase tracking-widest text-mute">Providers</p>
          {providers.length === 0 ? (
            <p className="text-xs text-mute">Core offline — nenhum provider no retrato.</p>
          ) : (
            providers.map((p) => (
              <div key={p.id} className="flex items-center justify-between gap-2 text-xs">
                <span className="flex items-center gap-2">
                  <Dot ok={p.ok} warn={p.scaffold || p.lab} />
                  {p.name}
                  <span className="text-mute">({p.id})</span>
                </span>
                <StatusBadge
                  ok={p.lab ? true : p.scaffold ? undefined : p.ok}
                  label={p.lab ? "lab" : p.scaffold ? "scaffold" : p.ok ? "active" : "down"}
                />
              </div>
            ))
          )}
        </div>
      </Card>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Signals Today" value={metrics.signals_today ?? 0} />
        <MetricCard label="Rules" value={metrics.rules ?? 0} />
        <MetricCard label="Errors" value={metrics.errors ?? 0} />
        <MetricCard
          label="Latency"
          value={metrics.latency_ms != null ? `${Number(metrics.latency_ms).toFixed(0)} ms` : "—"}
        />
      </div>

      <Card className="space-y-3">
        <h2 className="font-display text-lg font-semibold">Signal Generator</h2>
        <p className="text-sm text-mute">
          Gera sinais sintéticos via provider <code className="text-signal">debug</code>. Sem rede.
        </p>
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-xs text-mute">
            Mode
            <select
              className="mt-1 block rounded-md border border-line bg-panel px-2 py-2 font-mono text-sm text-fog"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              {modes.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
          <Button onClick={() => void generate()} disabled={pending}>
            {pending ? "…" : "Generate Test Signal"}
          </Button>
          <Button variant="secondary" onClick={() => void doExport()} disabled={pending}>
            Export JSON
          </Button>
        </div>
      </Card>

      <Card className="space-y-3">
        <h2 className="font-display text-lg font-semibold">Replay</h2>
        <p className="text-sm text-mute">Cole o JSON exportado e reexecute o pipeline do Core.</p>
        <textarea
          className="h-40 w-full rounded-md border border-line bg-panel p-3 font-mono text-[11px] text-fog"
          value={replayJson}
          onChange={(e) => setReplayJson(e.target.value)}
          placeholder='[ { "title": "…", "provider": "debug", ... } ]'
        />
        <Button variant="outline" onClick={() => void doReplay()} disabled={pending}>
          Replay → Core
        </Button>
      </Card>

      <Card>
        <p className="font-mono text-[10px] uppercase text-mute">Output</p>
        <pre className="mt-3 max-h-80 overflow-auto text-[11px] text-mute">
          {out ||
            (typeof data?.note === "string" ? data.note : null) ||
            "// generate / export / replay"}
        </pre>
      </Card>
    </div>
  );
}

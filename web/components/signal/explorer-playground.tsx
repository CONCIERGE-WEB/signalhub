"use client";

import { useMemo, useState } from "react";

import { Card } from "@/components/ui/cards";
import { Button } from "@/components/ui/button";

type Cap = {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  provider_ids: string[];
  contract_version?: string;
  permissions?: string[];
  parameters?: Record<string, unknown>;
  example_input?: Record<string, unknown>;
  example_output?: Record<string, unknown>;
  rest_example?: string;
  mcp_example?: Record<string, unknown>;
  python_example?: string;
  tool_name?: string;
};

export function CapabilityExplorerClient({ items }: { items: Cap[] }) {
  const [selectedId, setSelectedId] = useState(items[0]?.id ?? "");
  const selected = useMemo(
    () => items.find((i) => i.id === selectedId) ?? items[0] ?? null,
    [items, selectedId],
  );

  if (items.length === 0) {
    return <p className="text-sm text-mute">Sem capabilities no snapshot.</p>;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[16rem_1fr]">
      <ul className="space-y-1">
        {items.map((c) => (
          <li key={c.id}>
            <button
              type="button"
              onClick={() => setSelectedId(c.id)}
              className={`w-full rounded-md border px-2 py-1.5 text-left font-mono text-xs ${
                selected?.id === c.id
                  ? "border-signal/50 bg-signal/15 text-fog"
                  : "border-line bg-ink text-mute hover:border-signal/30"
              }`}
            >
              {c.enabled ? "✓" : "·"} {c.id}
            </button>
          </li>
        ))}
      </ul>
      {selected ? (
        <Card className="space-y-3 text-sm">
          <div>
            <h2 className="font-display text-xl font-semibold">{selected.name}</h2>
            <p className="mt-1 text-mute">{selected.description}</p>
          </div>
          <dl className="grid grid-cols-[7rem_1fr] gap-1 font-mono text-xs">
            <dt className="text-mute">contrato</dt>
            <dd>{selected.contract_version || "1.0.0"}</dd>
            <dt className="text-mute">providers</dt>
            <dd>{selected.provider_ids?.join(", ") || "—"}</dd>
            <dt className="text-mute">REST</dt>
            <dd>{selected.rest_example || `POST /v1/capabilities/${selected.id}/execute`}</dd>
          </dl>
          <div>
            <p className="mb-1 font-mono text-[10px] uppercase text-mute">MCP</p>
            <pre className="overflow-auto rounded-lg bg-panel p-3 text-[11px]">
              {JSON.stringify(selected.mcp_example || { name: selected.tool_name }, null, 2)}
            </pre>
          </div>
          <div>
            <p className="mb-1 font-mono text-[10px] uppercase text-mute">Python</p>
            <pre className="overflow-auto rounded-lg bg-panel p-3 text-[11px]">
              {selected.python_example || `# execute_capability(${JSON.stringify(selected.id)})`}
            </pre>
          </div>
          <div>
            <p className="mb-1 font-mono text-[10px] uppercase text-mute">I/O</p>
            <pre className="overflow-auto rounded-lg bg-panel p-3 text-[11px]">
              {JSON.stringify(
                { input: selected.example_input, output: selected.example_output },
                null,
                2,
              )}
            </pre>
          </div>
        </Card>
      ) : null}
    </div>
  );
}

export function PlaygroundClient({
  capabilities,
}: {
  capabilities: Array<{ id: string; name: string; tool_name: string }>;
}) {
  const [id, setId] = useState(capabilities[0]?.id || "discover_signals");
  const [body, setBody] = useState('{\n  "terms": ["exemplo"],\n  "limit": 5\n}');
  const [out, setOut] = useState<string>("");
  const [pending, setPending] = useState(false);

  async function run() {
    setPending(true);
    setOut("");
    try {
      let parsed: Record<string, unknown> = {};
      try {
        parsed = JSON.parse(body) as Record<string, unknown>;
      } catch {
        setOut(JSON.stringify({ error: "JSON inválido no request" }, null, 2));
        return;
      }
      const res = await fetch("/api/core/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ capability_id: id, arguments: parsed }),
      });
      const json = await res.json();
      setOut(JSON.stringify({ http: res.status, ...json }, null, 2));
    } catch (e) {
      setOut(String(e));
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card className="space-y-3">
        <label className="block text-xs text-mute">
          Capability
          <select
            className="mt-1 w-full rounded-md border border-line bg-panel px-2 py-2 font-mono text-sm text-fog"
            value={id}
            onChange={(e) => setId(e.target.value)}
          >
            {capabilities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.id}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-xs text-mute">
          Request
          <textarea
            className="mt-1 h-48 w-full rounded-md border border-line bg-panel p-3 font-mono text-xs text-fog"
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
        </label>
        <Button onClick={run} disabled={pending}>
          {pending ? "Executando…" : "Execute"}
        </Button>
      </Card>
      <Card>
        <p className="font-mono text-[10px] uppercase text-mute">Response · provenance via Core</p>
        <pre className="mt-3 max-h-[28rem] overflow-auto font-mono text-[11px] text-mute">
          {out || "// resultado aparece aqui — sem inventar sinal"}
        </pre>
      </Card>
    </div>
  );
}

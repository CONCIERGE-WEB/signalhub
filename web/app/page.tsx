import Link from "next/link";

import { PipelineRiver } from "@/components/signal/pipeline-river";
import { SiteFooter, SiteHeader } from "@/components/layout/site-chrome";
import { LinkButton } from "@/components/ui/button";
import { Card } from "@/components/ui/cards";

const SURFACES = [
  { title: "REST", href: "/rest", body: "HTTP canônico sobre Capabilities." },
  { title: "CLI", href: "/docs", body: "doctor · validate · contract-check." },
  { title: "MCP", href: "/mcp", body: "Tools projetadas sem scraping no servidor." },
  { title: "Dashboard", href: "/dashboard", body: "Janela para o protocolo." },
  { title: "Telegram", href: "/examples", body: "Adapter de notificação outbound." },
  { title: "Plugins", href: "/plugins", body: "Loader + version negotiation." },
];

const FAQ = [
  {
    q: "O Core usa IA?",
    a: "Não. Score e regras são determinísticos. IA, se existir, fica em consumers fora do Core.",
  },
  {
    q: "O que é um Signal?",
    a: "A unidade canônica do protocolo (RFC-0001): evidência pública normalizada e auditável.",
  },
  {
    q: "Como estendo o SignalHub?",
    a: "Via Plugin SDK. Providers não entram no Core — passam por validate e doctor.",
  },
  {
    q: "Scout e Dork estão prontos?",
    a: "Existem como plugins Cliente Zero (scaffold). Coleta real é fase posterior ao Core 1.0 LOCKED.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-void">
      <div className="pointer-events-none fixed inset-0 bg-aurora" />
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-[0.35] dark:opacity-20" />
      <SiteHeader />

      <main className="relative">
        <section className="mx-auto max-w-6xl px-4 pb-16 pt-16 md:pt-24">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-signal">
            Signal Contract 1.0 · Core LOCKED
          </p>
          <h1 className="mt-4 max-w-3xl font-display text-4xl font-semibold leading-[1.05] tracking-tight text-balance md:text-6xl">
            Build on Signals, not assumptions.
          </h1>
          <p className="mt-5 max-w-2xl text-lg text-mute">
            Construa sobre sinais, não sobre suposições. Protocolo determinístico para evidências
            públicas — REST, CLI, MCP e Dashboard falam a mesma língua: o Signal.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <LinkButton href="/mission-control" size="lg">
              Mission Control
            </LinkButton>
            <LinkButton href="/playground" variant="secondary" size="lg">
              Get Started
            </LinkButton>
            <LinkButton href="/docs" variant="outline" size="lg">
              Documentation
            </LinkButton>
            <LinkButton
              href="https://github.com/TiagoIA-UX/signalhub"
              variant="ghost"
              size="lg"
            >
              GitHub
            </LinkButton>
          </div>

          <div className="mt-10 overflow-hidden rounded-xl border border-line bg-ink">
            <div className="flex items-center gap-2 border-b border-line px-4 py-2">
              <span className="size-2 rounded-full bg-fault/80" />
              <span className="size-2 rounded-full bg-warn/80" />
              <span className="size-2 rounded-full bg-valid/80" />
              <span className="ml-2 font-mono text-[10px] text-mute">install</span>
            </div>
            <pre className="overflow-x-auto p-4 font-mono text-xs leading-relaxed text-fog md:text-sm">
{`pip install -e .
python -m signalhub.apps.cli doctor --full
python -m signalhub.apps.cli admin-snapshot`}
            </pre>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">Signal Contract</h2>
          <p className="mt-2 max-w-2xl text-mute">
            Tudo no SignalHub produz ou consome Signals. Todo componente existe para manipular
            Signals. O contrato é a linguagem comum da plataforma.
          </p>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            {["Canonical object", "Lifecycle & states", "Validation · Priority · Provenance"].map(
              (t) => (
                <Card key={t}>
                  <p className="font-mono text-[10px] uppercase tracking-widest text-signal">rfc-0001</p>
                  <p className="mt-2 text-sm text-fog">{t}</p>
                </Card>
              ),
            )}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="mb-4 font-display text-2xl font-semibold">Pipeline</h2>
          <PipelineRiver />
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">Como funciona</h2>
          <ol className="mt-6 grid gap-3 md:grid-cols-3">
            {[
              "Provider descobre RawHits públicos (plugin).",
              "Core valida, normaliza, deduplica, aplica regras e score.",
              "Capabilities expõem o resultado em REST / MCP / CLI.",
            ].map((step, i) => (
              <Card key={step}>
                <p className="font-mono text-[10px] text-mute">{String(i + 1).padStart(2, "0")}</p>
                <p className="mt-2 text-sm text-fog">{step}</p>
              </Card>
            ))}
          </ol>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">Arquitetura</h2>
          <p className="mt-2 max-w-2xl text-sm text-mute">
            Apps → Adapter/projection → Core (Orchestrator + Pipeline) → Plugin SDK → plugins/*.
            O Lex Rocha e outros consumidores não duplicam regras.
          </p>
          <pre className="mt-6 overflow-x-auto rounded-xl border border-line bg-ink p-4 font-mono text-[11px] leading-relaxed text-mute">
{`Apps: REST · CLI · MCP · Dashboard · Telegram
              │
         SignalHub Core 1.0 (LOCKED)
              │
         Plugin Loader + Version Negotiation
              │
     Scout · Dork · Google  (scaffolds / empty explicit)`}
          </pre>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">Superfícies</h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {SURFACES.map((s) => (
              <Link key={s.title} href={s.href} className="block transition hover:-translate-y-0.5">
                <Card className="h-full hover:border-signal/40">
                  <h3 className="font-display font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm text-mute">{s.body}</p>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">Developer Experience</h2>
          <p className="mt-2 max-w-2xl text-mute">
            create → validate → doctor → contract-check. Um provider funcional em minutos — sem
            porta dos fundos no Core.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <LinkButton href="/examples" variant="secondary">
              Examples
            </LinkButton>
            <LinkButton href="/explorer" variant="outline">
              Capability Explorer
            </LinkButton>
            <LinkButton href="/changelog" variant="ghost">
              Changelog
            </LinkButton>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">Open Specification</h2>
          <p className="mt-2 text-mute">
            RFC-0001 Signal Specification está estável. RFCs de Provider, Capability, Adapter e
            Score virão sem quebrar o contrato.
          </p>
          <LinkButton href="/rfc" className="mt-6" variant="secondary">
            Ver RFCs
          </LinkButton>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-12">
          <h2 className="font-display text-2xl font-semibold">FAQ</h2>
          <div className="mt-6 space-y-3">
            {FAQ.map((item) => (
              <Card key={item.q}>
                <h3 className="font-medium text-fog">{item.q}</h3>
                <p className="mt-2 text-sm text-mute">{item.a}</p>
              </Card>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-20 text-center">
          <h2 className="font-display text-3xl font-semibold">Pronto para construir sobre Signals?</h2>
          <p className="mx-auto mt-3 max-w-xl text-mute">
            O Core está travado. A evolução agora é DX, plugins e consumidores — pela janela Web.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <LinkButton href="/playground" size="lg">
              Abrir Playground
            </LinkButton>
            <LinkButton href="/docs" variant="secondary" size="lg">
              Ler a spec
            </LinkButton>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

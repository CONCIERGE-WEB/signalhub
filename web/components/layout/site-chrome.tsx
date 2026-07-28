import Link from "next/link";

import { ThemeToggle } from "@/components/layout/theme-toggle";
import { LinkButton } from "@/components/ui/button";
import { cn } from "@/lib/cn";

const NAV = [
  { href: "/mission-control", label: "Mission Control" },
  { href: "/docs", label: "Docs" },
  { href: "/rfc", label: "RFCs" },
  { href: "/playground", label: "Playground" },
];

export function SiteHeader({ solid = false }: { solid?: boolean }) {
  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b border-line/80 backdrop-blur-xl",
        solid ? "bg-void/95" : "bg-void/70",
      )}
    >
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="inline-flex size-7 items-center justify-center rounded-md border border-signal/40 bg-signal/10 font-mono text-[10px] text-signal">
            SH
          </span>
          <span className="font-display text-sm font-semibold tracking-tight">SignalHub</span>
          <span className="hidden font-mono text-[10px] text-mute sm:inline">core 1.0</span>
        </Link>
        <nav className="hidden items-center gap-5 md:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm text-mute transition hover:text-fog"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <LinkButton href="/docs" variant="secondary" size="sm" className="hidden sm:inline-flex">
            Documentation
          </LinkButton>
          <LinkButton href="/playground" size="sm">
            Get Started
          </LinkButton>
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-line bg-ink">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 md:grid-cols-4">
        <div className="md:col-span-2">
          <p className="font-display text-lg font-semibold">SignalHub</p>
          <p className="mt-2 max-w-md text-sm text-mute">
            Build on Signals, not assumptions. Protocolo determinístico para sinais públicos —
            sem IA no Core.
          </p>
        </div>
        <div>
          <p className="font-mono text-[10px] uppercase tracking-widest text-mute">Platform</p>
          <ul className="mt-3 space-y-2 text-sm text-mute">
            <li>
              <Link href="/dashboard">Dashboard</Link>
            </li>
            <li>
              <Link href="/explorer">Explorer</Link>
            </li>
            <li>
              <Link href="/integrity">Integrity</Link>
            </li>
            <li>
              <Link href="/metrics">Metrics</Link>
            </li>
          </ul>
        </div>
        <div>
          <p className="font-mono text-[10px] uppercase tracking-widest text-mute">Protocol</p>
          <ul className="mt-3 space-y-2 text-sm text-mute">
            <li>
              <Link href="/rfc">RFCs</Link>
            </li>
            <li>
              <Link href="/mcp">MCP</Link>
            </li>
            <li>
              <Link href="/rest">REST</Link>
            </li>
            <li>
              <Link href="/examples">Examples</Link>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-4 font-mono text-[10px] text-mute">
          <span>Signal Contract 1.0.0 · Core LOCKED</span>
          <span>© {new Date().getFullYear()} SignalHub</span>
        </div>
      </div>
    </footer>
  );
}

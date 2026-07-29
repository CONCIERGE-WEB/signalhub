"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";

const ITEMS = [
  { href: "/mission-control", label: "Mission Control" },
  { href: "/discovery-engine", label: "Discovery Engine" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/integrity", label: "Integrity" },
  { href: "/metrics", label: "Metrics" },
  { href: "/providers", label: "Providers" },
  { href: "/capabilities", label: "Capabilities" },
  { href: "/plugins", label: "Plugins" },
  { href: "/explorer", label: "Explorer" },
  { href: "/playground", label: "Playground" },
  { href: "/mcp", label: "MCP" },
  { href: "/rest", label: "REST" },
  { href: "/docs", label: "Docs" },
  { href: "/rfc", label: "RFCs" },
  { href: "/examples", label: "Examples" },
  { href: "/changelog", label: "Changelog" },
];

export function PlatformNav() {
  const pathname = usePathname();
  return (
    <aside className="w-full shrink-0 border-b border-line bg-ink md:w-56 md:border-b-0 md:border-r">
      <div className="sticky top-14 p-3">
        <p className="mb-2 px-2 font-mono text-[10px] uppercase tracking-[0.18em] text-mute">
          platform
        </p>
        <nav className="flex gap-1 overflow-x-auto md:flex-col md:overflow-visible">
          {ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "whitespace-nowrap rounded-md px-2.5 py-1.5 text-sm transition",
                  active
                    ? "bg-signal/15 text-fog"
                    : "text-mute hover:bg-panel hover:text-fog",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}

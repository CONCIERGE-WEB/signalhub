"use client";

import { motion, useReducedMotion } from "framer-motion";

const STAGES = [
  "Provider",
  "Signal",
  "Validator",
  "Normalizer",
  "Deduplicator",
  "Rule Engine",
  "Score Engine",
  "Storage",
  "Capabilities",
  "Consumers",
] as const;

/** Assinatura visual: o Signal atravessa o contrato como um pacote no rio. */
export function PipelineRiver({ compact = false }: { compact?: boolean }) {
  const reduce = useReducedMotion();

  return (
    <div
      className={
        compact
          ? "relative overflow-hidden rounded-xl border border-line bg-ink p-4"
          : "relative overflow-hidden rounded-2xl border border-line bg-ink/90 p-6 shadow-signal"
      }
    >
      <div className="pointer-events-none absolute inset-0 bg-aurora opacity-70" />
      <div className="relative mb-4 flex items-center justify-between gap-3">
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-mute">
          signal pipeline · contract 1.0.0
        </p>
        <span className="rounded border border-signal/30 bg-signal/10 px-2 py-0.5 font-mono text-[10px] text-signal">
          deterministic
        </span>
      </div>

      <div className="relative">
        <div className="absolute left-0 right-0 top-1/2 h-px -translate-y-1/2 bg-gradient-to-r from-transparent via-signal/50 to-transparent" />
        {!reduce ? (
          <motion.div
            className="absolute top-1/2 z-10 size-2.5 -translate-y-1/2 rounded-full bg-signal shadow-glow"
            animate={{ left: ["0%", "100%"], opacity: [0, 1, 1, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
            aria-hidden
          />
        ) : null}

        <ol className="relative z-[1] flex gap-2 overflow-x-auto pb-1">
          {STAGES.map((stage, i) => (
            <li
              key={stage}
              className="min-w-[7.5rem] shrink-0 rounded-lg border border-line bg-panel/80 px-3 py-2 backdrop-blur"
            >
              <span className="font-mono text-[10px] text-mute">
                {String(i + 1).padStart(2, "0")}
              </span>
              <p className="mt-1 text-xs font-medium text-fog">{stage}</p>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}

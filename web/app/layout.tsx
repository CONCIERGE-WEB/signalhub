import { IBM_Plex_Mono, Outfit, Syne } from "next/font/google";

import { Providers } from "@/components/layout/providers";

import "./globals.css";

const sans = Outfit({
  subsets: ["latin"],
  variable: "--font-sans",
});

const display = Syne({
  subsets: ["latin"],
  variable: "--font-display",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
});

export const metadata = {
  title: {
    default: "SignalHub — Build on Signals, not assumptions",
    template: "%s · SignalHub",
  },
  description:
    "Plataforma determinística de sinais públicos. Signal Contract 1.0, Capabilities, MCP, REST e Plugin SDK — sem IA no Core.",
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning className="dark">
      <body className={`${sans.variable} ${display.variable} ${mono.variable} font-sans`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

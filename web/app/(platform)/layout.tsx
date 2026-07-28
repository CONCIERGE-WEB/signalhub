import { SiteFooter, SiteHeader } from "@/components/layout/site-chrome";
import { PlatformNav } from "@/components/layout/platform-nav";

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-void">
      <SiteHeader solid />
      <div className="mx-auto flex max-w-6xl flex-col md:flex-row">
        <PlatformNav />
        <main className="min-w-0 flex-1 px-4 py-8 md:px-8">{children}</main>
      </div>
      <SiteFooter />
    </div>
  );
}

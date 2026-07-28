import { NextResponse } from "next/server";

import { labReplay } from "@/lib/signalhub/adapter";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as { signals?: unknown[] } | null;
  if (!body?.signals || !Array.isArray(body.signals)) {
    return NextResponse.json({ ok: false, error: "signals[] obrigatório" }, { status: 400 });
  }
  const result = await labReplay(body.signals);
  return NextResponse.json(result.payload, { status: result.status });
}

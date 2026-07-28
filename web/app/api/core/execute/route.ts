import { NextResponse } from "next/server";

import { executeCapability } from "@/lib/signalhub/adapter";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as {
    capability_id?: string;
    arguments?: Record<string, unknown>;
  } | null;
  if (!body?.capability_id) {
    return NextResponse.json({ error: "capability_id obrigatório" }, { status: 400 });
  }
  const result = await executeCapability(body.capability_id, body.arguments || {});
  return NextResponse.json(result.payload, { status: result.status });
}

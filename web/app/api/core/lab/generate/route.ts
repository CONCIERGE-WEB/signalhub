import { NextResponse } from "next/server";

import { labGenerate } from "@/lib/signalhub/adapter";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as {
    mode?: string;
    limit?: number;
  };
  const result = await labGenerate(body.mode || "valid", body.limit ?? 1);
  return NextResponse.json(result.payload, { status: result.status });
}

import { NextResponse } from "next/server";

import { fetchMissionControl } from "@/lib/signalhub/adapter";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const result = await fetchMissionControl();
  return NextResponse.json(result.payload, { status: result.status });
}

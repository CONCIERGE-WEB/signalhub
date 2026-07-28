import { NextResponse } from "next/server";

import { labExport } from "@/lib/signalhub/adapter";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const result = await labExport();
  return NextResponse.json(result.payload, { status: result.status });
}

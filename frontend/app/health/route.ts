import { NextResponse } from "next/server";

/**
 * GET /health — used by Railway healthcheck.
 * Returns 200 immediately so Railway knows the container is up.
 */
export async function GET() {
  return NextResponse.json({ status: "ok" });
}

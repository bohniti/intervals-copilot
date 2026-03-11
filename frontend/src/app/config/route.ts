import { NextResponse } from "next/server";

/**
 * Returns the Mapy.com API key at runtime so it never gets baked into the
 * client-side JS bundle.  The key is read from the MAPY_API_KEY env var
 * which is set in docker-compose.prod.yml → sourced from VPS .env.
 */
export async function GET() {
  const key = process.env.MAPY_API_KEY;
  if (!key) {
    return NextResponse.json({ error: "MAPY_API_KEY not configured" }, { status: 500 });
  }
  return NextResponse.json({ apiKey: key });
}

import { NextResponse } from "next/server"

// Use the Supabase-hosted Django backend API
const BACKEND_API_URL = "https://remhqhnmphsxufvdpokr.supabase.co/api/products/"

export async function GET() {
  try {
    // Fetch from the actual Django backend URL
    const res = await fetch(BACKEND_API_URL, { next: { revalidate: 0 } }) // disable caching
    if (!res.ok) {
      const errorText = await res.text()
      console.error(`Upstream Django API error: ${res.status} - ${errorText}`)
      return NextResponse.json({ message: `Upstream error: ${res.status} ${res.statusText}` }, { status: res.status })
    }
    const data = await res.json()
    return NextResponse.json(data, { status: 200 })
  } catch (err) {
    console.error("Proxy fetch error:", err)
    return NextResponse.json(
      { message: "Unable to reach Django API. Please ensure it's running and accessible." },
      { status: 502 },
    )
  }
}

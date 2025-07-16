import { NextResponse } from "next/server"

// Use NEXT_PUBLIC_DJANGO_API_URL from environment variables
const BACKEND_API_URL = process.env.NEXT_PUBLIC_DJANGO_API_URL || "http://localhost:8000/api/products/"

export async function GET() {
  try {
    // Fetch from the actual Django backend URL
    const res = await fetch(BACKEND_API_URL, { next: { revalidate: 0 } }) // no-store to ensure fresh data
    if (!res.ok) {
      // If the upstream Django API returns an error, propagate it
      const errorText = await res.text()
      console.error(`Upstream Django API error: ${res.status} - ${errorText}`)
      return NextResponse.json({ message: `Upstream error: ${res.status} ${res.statusText}` }, { status: res.status })
    }
    const data = await res.json()
    return NextResponse.json(data, { status: 200 })
  } catch (err) {
    // Handle network errors or other issues reaching the Django API
    console.error("Proxy fetch error:", err)
    return NextResponse.json(
      { message: "Unable to reach Django API. Please ensure it's running and accessible." },
      { status: 502 },
    )
  }
}

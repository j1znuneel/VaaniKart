import { NextResponse } from "next/server"

const BACKEND = process.env.NEXT_PUBLIC_DJANGO_API_URL ?? "http://localhost:8000/api/products/" // fallback for local dev

export async function GET() {
  try {
    const res = await fetch(BACKEND, { next: { revalidate: 0 } }) // no-store
    if (!res.ok) {
      return NextResponse.json({ message: `Upstream error ${res.status}` }, { status: res.status })
    }
    const data = await res.json()
    return NextResponse.json(data, { status: 200 })
  } catch (err) {
    console.error("Proxy fetch error →", err)
    return NextResponse.json({ message: "Unable to reach Django API" }, { status: 502 })
  }
}

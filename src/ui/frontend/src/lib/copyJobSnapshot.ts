/** Diagnostic job snapshot clipboard write — not email/linkedin copy. */
import api from "./api"

export async function copyJobSnapshotToClipboard(astralJobId: string): Promise<boolean> {
  try {
    const res = await api(`/api/jobs/${encodeURIComponent(astralJobId)}/copy`)
    if (!res.ok) return false
    const body = await res.json()
    await navigator.clipboard.writeText(JSON.stringify(body, null, 2))
    return true
  } catch {
    return false
  }
}

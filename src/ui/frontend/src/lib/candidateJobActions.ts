import api from "./api"

export type CandidateActionKey = "applied" | "interview" | "rejected" | "ghosted" | "review"

export async function postCandidateAction(
  astralJobId: string,
  action: CandidateActionKey,
  notes?: string,
): Promise<void> {
  const res = await api(`/api/jobs/${encodeURIComponent(astralJobId)}/candidate_action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, notes: notes ?? "" }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { error?: string }).error || "Action failed")
  }
}

export async function postSkipJob(astralJobId: string): Promise<void> {
  const res = await api(`/api/jobs/${encodeURIComponent(astralJobId)}/skip`, { method: "POST" })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { error?: string }).error || "Skip failed")
  }
}

/** Start a job's artifact build (RECOMMENDED → BUILD_ARTIFACTS); server enforces legality (409). */
export async function postGenerateArtifacts(astralJobId: string): Promise<void> {
  const res = await api(`/api/jobs/${encodeURIComponent(astralJobId)}/generate_artifacts`, { method: "POST" })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { error?: string }).error || "Generate failed")
  }
}

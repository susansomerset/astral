/** Non-empty rubric list / dict / string stored under candidate_data.artifacts. */
export function artifactBlobHasContent(raw: unknown): boolean {
  if (Array.isArray(raw)) {
    return raw.some(v => {
      if (v && typeof v === "object" && "content" in (v as object)) {
        return String((v as { content?: unknown }).content ?? "").trim() !== ""
      }
      return String(v ?? "").trim() !== ""
    })
  }
  if (typeof raw === "string") return raw.trim() !== ""
  if (raw && typeof raw === "object") {
    return Object.values(raw as Record<string, unknown>).some(v => String(v ?? "").trim() !== "")
  }
  return false
}

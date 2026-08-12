export function browserTabTitle(fullName: string | null | undefined): string {
  const name = (fullName ?? "").trim()
  if (!name) return "Astral"
  return `Astral - ${name}`
}

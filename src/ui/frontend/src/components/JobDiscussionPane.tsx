import { useMemo } from "react"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import { type AgentBlock, type AgentStoryEntry } from "./AgentStoryTab"
import { useCandidate } from "../contexts/CandidateContext"
import { extractAgentPayloadText } from "../lib/recommendedJobReport"

type Props = {
  sections: readonly ReportSectionDef[]
  agentStory: readonly AgentStoryEntry[]
}

/** Recommended Job Report Discussion — RESPONSE agent_payload + named headers (AST-2234). */
export default function JobDiscussionPane({ sections, agentStory }: Props) {
  const { candidates, selectedId } = useCandidate()
  const tz = useMemo(() => {
    const c = candidates.find(x => x.astral_candidate_id === selectedId)
    const contact = c?.candidate_data?.contact as Record<string, string> | undefined
    return contact?.timezone || "UTC"
  }, [candidates, selectedId])

  // Headers only for hops with a non-empty agent_payload body (AST-1609 / AST-2234).
  const labeledSections: ReportSectionDef[] = sections
    .map(s => {
      const body = responseBodyForTask(agentStory, s.section_id)
      if (!body) return null
      const entry = agentStory.find(e => (e.task_key || "") === s.section_id)
      return { ...s, nav_label: discussionSectionLabel(entry, s.nav_label, tz) }
    })
    .filter((s): s is ReportSectionDef => s != null)

  return (
    <ReportSectionList
      sections={labeledSections}
      renderSection={(sectionId) => {
        const body = responseBodyForTask(agentStory, sectionId)
        if (!body) return null
        return (
          <textarea
            className="entity-story-content"
            readOnly
            value={body}
          />
        )
      }}
    />
  )
}

function strip(value: unknown): string {
  return typeof value === "string" ? value.trim() : String(value ?? "").trim()
}

function discussionSectionLabel(
  entry: AgentStoryEntry | undefined,
  fallbackNav: string,
  tz: string,
): string {
  if (!entry) return fallbackNav
  const name = strip(entry.agent_name) || strip(entry.agent_id) || "Agent"
  const task = strip(entry.task_name) || strip(entry.task_key) || fallbackNav
  const stamp = formatDiscussionStamp(entry.created_at, tz)
  return stamp ? `${name}'s ${task} @ ${stamp}` : `${name}'s ${task}`
}

/** m/d/yy hh:mm am/pm in candidate tz — no seconds (AST-2234). */
function formatDiscussionStamp(iso: unknown, tz: string): string | null {
  if (typeof iso !== "string" || !iso.trim()) return null
  const raw = iso.endsWith("Z") || /[+-]\d{2}:\d{2}$/.test(iso) ? iso : iso + "Z"
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return null
  const opts: Intl.DateTimeFormatOptions = {
    year: "2-digit",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }
  try {
    // en-US yields "3/5/26, 4:48 PM" — drop the comma for AC "@ m/d/yy hh:mm am/pm".
    return d.toLocaleString("en-US", { ...opts, timeZone: tz }).replace(", ", " ")
  } catch {
    try {
      return d.toLocaleString("en-US", { ...opts, timeZone: "UTC" }).replace(", ", " ")
    } catch {
      return null
    }
  }
}

function responseBodyForTask(story: readonly AgentStoryEntry[], taskKey: string): string {
  const entry = story.find(e => (e.task_key || "") === taskKey)
  if (!entry) return ""
  // Skip empty RESPONSE first (AgentStoryTab parity) so a blank block cannot hide a later body.
  const block = (entry.blocks ?? []).find(
    (b: AgentBlock) =>
      (b.type === "RESPONSE" || b.type.startsWith("RESPONSE")) && b.content !== "",
  )
  if (!block) return ""
  return extractAgentPayloadText(block.content)
}

import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import { type AgentBlock, type AgentStoryEntry } from "./AgentStoryTab"

type Props = {
  sections: readonly ReportSectionDef[]
  agentStory: readonly AgentStoryEntry[]
}

/** Recommended Job Report Discussion — RESPONSE-only hop stack (AST-1551). */
export default function JobDiscussionPane({ sections, agentStory }: Props) {
  return (
    <ReportSectionList
      sections={sections}
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

// Pretty-print JSON; else raw text — same rules as AgentStoryTab.formatContent.
function formatDiscussionContent(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2)
  } catch {
    return raw
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
  return formatDiscussionContent(block.content)
}

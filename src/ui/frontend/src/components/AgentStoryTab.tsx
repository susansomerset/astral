import { useState } from "react"
import { TabBar } from "./TabbedTextArea"
import Time from "./Time"
import AgentAnalysisHeader from "./AgentAnalysisHeader"

export interface AgentBlock {
  type: string
  id: string
  content: string
}

export interface AgentStoryEntry {
  task_key: string
  created_at?: string
  agent_performance?: string
  failure_note?: string
  blocks: AgentBlock[]
  vector_grades?: Array<{ vector: string; grade: string; reason?: string; confidence?: number }>
  rubric_artifact?: string
  [key: string]: unknown
}

export default function AgentStoryTab({ entry }: { entry: AgentStoryEntry }) {
  const blocks = entry.blocks ?? []
  // Filter out RESPONSE blocks with empty content (old encoded data)
  const displayBlocks = blocks.filter(b => !(b.type === "RESPONSE" && b.content === ""))
  const [activeBlockIdx, setActiveBlockIdx] = useState(0)
  const barTabs = displayBlocks.map((b, i) => ({ key: String(i), label: b.type }))
  const active = displayBlocks[activeBlockIdx]

  // Pretty-print JSON for RESPONSE blocks (and any other block whose content parses as JSON)
  function formatContent(block: AgentBlock | undefined): string {
    if (!block) return ""
    try {
      return JSON.stringify(JSON.parse(block.content), null, 2)
    } catch {
      return block.content
    }
  }

  return (
    <div className="entity-story-tab">
      <div className="entity-story-meta">
        <span className="entity-story-key">{entry.task_key}</span>
        {entry.created_at && <span className="entity-story-time"><Time value={entry.created_at as string} /></span>}
        {entry.agent_performance && <span className="entity-story-perf">{entry.agent_performance}</span>}
        {entry.failure_note && <span className="entity-story-fail">{entry.failure_note}</span>}
      </div>
      {entry.vector_grades && entry.vector_grades.length > 0 && (
        <AgentAnalysisHeader grades={entry.vector_grades} rubricArtifact={entry.rubric_artifact} />
      )}
      {displayBlocks.length === 0
        ? <p className="entity-empty">No prompt blocks recorded.</p>
        : (
          <>
            <TabBar tabs={barTabs} active={String(activeBlockIdx)} onChange={k => setActiveBlockIdx(Number(k))} />
            <textarea className="entity-story-content" readOnly value={formatContent(active)} />
          </>
        )}
    </div>
  )
}

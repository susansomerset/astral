import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import ResumeStructureEditor, {
  type Catalog,
  type SectionRow,
} from "../../../../src/ui/frontend/src/components/ResumeStructureEditor"

const catalog: Catalog = {
  body_formats: ["free_prose", "bullet_list", "word_cloud", "experience_detail"],
  required_ids: ["professional_summary"],
  contact_ids: [],
  extra_id_pattern: "^[a-z][a-z0-9_]*$",
  reserved_extra_ids: ["content"],
  new_extra_default_format: "bullet_list",
}

const rows: SectionRow[] = [
  {
    id: "professional_summary",
    title: "Summary",
    enabled: true,
    order: 0,
    format: "free_prose",
    job_agent_editable: true,
    required: true,
    format_locked: false,
  },
  {
    id: "experience",
    title: "Experience",
    enabled: true,
    order: 1,
    format: "experience_detail",
    job_agent_editable: true,
    required: true,
    format_locked: true,
  },
  {
    id: "prior_experience",
    title: "Prior Experience",
    enabled: true,
    order: 2,
    format: "word_cloud",
    job_agent_editable: true,
    required: false,
    format_locked: false,
  },
]

describe("ResumeStructureEditor", () => {
  it("AST-1306: format options come from catalog; required has no Remove", async () => {
    const user = userEvent.setup()
    const onSave = vi.fn()
    render(
      <ResumeStructureEditor
        sections={rows}
        catalog={catalog}
        disabled={false}
        onSave={onSave}
        saving={false}
        error={null}
      />,
    )
    expect(screen.getByText("Resume sections")).toBeInTheDocument()
    const formatSelects = screen.getAllByRole("combobox")
    const rowFormat = formatSelects[0]
    expect(Array.from(rowFormat.querySelectorAll("option")).map(o => o.textContent)).toEqual(
      catalog.body_formats,
    )
    expect(screen.getAllByRole("combobox")[1]).toBeDisabled()
    expect(screen.getAllByRole("button", { name: "Remove" })).toHaveLength(1)
    await user.type(screen.getAllByRole("textbox")[rows.length], "Highlights")
    await user.click(screen.getByRole("button", { name: "Add section" }))
    await user.click(screen.getByRole("button", { name: "Save sections" }))
    const saved = onSave.mock.calls[0][0] as SectionRow[]
    expect(saved.some(r => r.id.startsWith("_pending_") && r.title === "Highlights")).toBe(true)
    expect(saved.some(r => r.id === "professional_summary")).toBe(true)
  })
})

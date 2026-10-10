import { act, fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

// Children have their own suites (AST-2082 / AST-2083); stubs record the props this modal wires.
const props: Record<string, Record<string, unknown>> = {}
vi.mock("../../../../src/ui/frontend/src/components/ResumeContentEditor", () => ({
  default: (p: Record<string, unknown>) => { props.editor = p; return <div data-testid="resume-editor" /> },
}))
vi.mock("../../../../src/ui/frontend/src/components/ArtifactEditor", () => ({
  default: (p: Record<string, unknown>) => { props.artifact = p; return <div data-testid="artifact-editor" /> },
}))
vi.mock("../../../../src/ui/frontend/src/components/PrintPreview", () => ({
  default: (p: Record<string, unknown>) => { props.preview = p; return <div data-testid="preview" /> },
}))

import JobArtifactEditModal, { type JobArtifactTab } from "../../../../src/ui/frontend/src/components/JobArtifactEditModal"

const RESUME: JobArtifactTab = {
  tab_id: "artifact_resume", nav_label: "Job Resume", artifact_key: "job_resume",
  shapes_key: null, use_resume_structure: true, preview_thumbnail: true,
}
const COVER: JobArtifactTab = {
  tab_id: "artifact_cover", nav_label: "Cover Letter", artifact_key: "cover_letter",
  shapes_key: "cover_letter", use_resume_structure: false, preview_thumbnail: true,
}

describe("AST-2084 JobArtifactEditModal", () => {
  it("renders nothing while tab is null", () => {
    render(<JobArtifactEditModal jobId="j1" tab={null} onClose={vi.fn()} />)
    expect(document.querySelector(".modal-overlay")).toBeNull()
  })

  it("AST-2115 [bug-repro]: job resume opens a stacked 80%-width split pane over the page with the job editor and job_resume preview; a save bumps the preview once", () => {
    render(<JobArtifactEditModal jobId="j1" tab={RESUME} onClose={vi.fn()} />)
    expect(document.querySelector(".modal-overlay--stacked")).toBeTruthy()
    expect(screen.getByRole("heading", { name: "Job Resume" })).toBeInTheDocument()
    // AST-2115: 80vw × 90vh card with its border kept, not the edge-to-edge fullscreen card.
    const card = document.querySelector(".modal-card") as HTMLElement
    expect(card.style.width).toBe("80vw")
    expect(card.style.height).toBe("90vh")
    expect(card.style.borderStyle).toBe("")
    expect((card.querySelector(".modal-body") as HTMLElement).style.padding).toBe("0px")
    expect(screen.getByRole("separator")).toBeInTheDocument()
    expect(screen.queryByTestId("artifact-editor")).toBeNull()
    expect(props.editor.target).toEqual({ kind: "job", id: "j1" })
    expect(props.preview).toMatchObject({ target: { kind: "job_resume", id: "j1" }, refreshKey: 0 })
    act(() => (props.editor.onSaved as () => void)())
    expect(props.preview.refreshKey).toBe(1)
  })

  it("cover letter: existing shapes editor with job persistence and the cover preview; its onSaved bumps the preview", () => {
    render(<JobArtifactEditModal jobId="j1" tab={COVER} onClose={vi.fn()} />)
    expect(screen.queryByTestId("resume-editor")).toBeNull()
    expect(props.artifact).toMatchObject({
      title: "Cover Letter", artifactKey: "cover_letter", taskKey: "craft_cover_letter", shapesKey: "cover_letter",
    })
    const persistence = props.artifact.jobPersistence as { jobId: string; artifactKey: string; onSaved: () => void }
    expect(persistence).toMatchObject({ jobId: "j1", artifactKey: "cover_letter" })
    expect(props.preview).toMatchObject({ target: { kind: "cover", id: "j1" }, refreshKey: 0 })
    act(() => persistence.onSaved())
    expect(props.preview.refreshKey).toBe(1)
  })

  it("Close calls onClose; no footer", () => {
    const onClose = vi.fn()
    render(<JobArtifactEditModal jobId="j1" tab={RESUME} onClose={onClose} />)
    expect(document.querySelector(".modal-footer")).toBeNull()
    fireEvent.click(screen.getByRole("button", { name: "Close" }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })
})

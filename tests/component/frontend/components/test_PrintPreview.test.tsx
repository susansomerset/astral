import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import PrintPreview from "../../../../src/ui/frontend/src/components/PrintPreview"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)
const BODY = "<html><body><h1>Ada Lovelace</h1></body></html>"

function serve(body = BODY) {
  mockedApi.mockResolvedValue({ ok: true, status: 200, text: async () => body } as Response)
}

function iframe(): HTMLIFrameElement {
  return screen.getByTitle("Print preview") as HTMLIFrameElement
}

// AST-2082: preview renders the builder print route body in an iframe; thumbnail is scaled + click-through.
describe("AST-2082 PrintPreview", () => {
  beforeEach(() => mockedApi.mockReset())

  it.each([
    ["base", "c1", "/candidate/resume/base?candidate_id=c1"],
    ["job_resume", "job-1", "/candidate/resume/job-1"],
    ["cover", "job-1", "/candidate/cover/job-1"],
  ] as const)("AC3: %s iframe srcDoc equals the GET body", async (kind, id, path) => {
    serve()
    const { container } = render(<PrintPreview target={{ kind, id }} />)
    // Nothing renders until the fetch lands.
    expect(container).toBeEmptyDOMElement()
    await waitFor(() => expect(iframe().getAttribute("srcdoc")).toBe(BODY))
    expect(mockedApi).toHaveBeenCalledWith(path)
    expect(mockedApi).toHaveBeenCalledTimes(1)
  })

  it("shows the builder error text and no iframe on failure", async () => {
    mockedApi.mockResolvedValue({ ok: false, status: 404, json: async () => ({ error: "Job not found" }) } as unknown as Response)
    render(<PrintPreview target={{ kind: "job_resume", id: "nope" }} />)
    expect(await screen.findByText("Job not found")).toHaveClass("entity-error")
    expect(screen.queryByTitle("Print preview")).toBeNull()
  })

  it("refetches once per refreshKey bump, not for a fresh equal target object", async () => {
    serve()
    const { rerender } = render(<PrintPreview target={{ kind: "base", id: "c1" }} refreshKey={0} />)
    await waitFor(() => expect(mockedApi).toHaveBeenCalledTimes(1))
    rerender(<PrintPreview target={{ kind: "base", id: "c1" }} refreshKey={0} />)
    serve("<p>after save</p>")
    rerender(<PrintPreview target={{ kind: "base", id: "c1" }} refreshKey={1} />)
    await waitFor(() => expect(iframe().getAttribute("srcdoc")).toBe("<p>after save</p>"))
    expect(mockedApi).toHaveBeenCalledTimes(2)
    rerender(<PrintPreview target={{ kind: "base", id: "c2" }} refreshKey={1} />)
    await waitFor(() => expect(mockedApi).toHaveBeenCalledTimes(3))
    expect(mockedApi).toHaveBeenLastCalledWith("/candidate/resume/base?candidate_id=c2")
  })

  it("stale response after unmount is dropped", async () => {
    let resolve!: (r: Response) => void
    mockedApi.mockReturnValue(new Promise<Response>(r => { resolve = r }))
    const err = vi.spyOn(console, "error").mockImplementation(() => {})
    const { unmount } = render(<PrintPreview target={{ kind: "base", id: "c1" }} />)
    unmount()
    resolve({ ok: true, status: 200, text: async () => BODY } as Response)
    await new Promise(r => setTimeout(r, 0))
    expect(err).not.toHaveBeenCalled()
    err.mockRestore()
  })

  it("thumbnail: scaled, non-interactive page; clicks go to onClick", async () => {
    serve()
    const onClick = vi.fn()
    const { container } = render(<PrintPreview target={{ kind: "cover", id: "job-1" }} thumbnail onClick={onClick} />)
    const thumb = container.querySelector(".print-preview-thumb") as HTMLDivElement
    // Box renders before the fetch lands; iframe joins after.
    expect(thumb.style.width).toBe("204px")
    expect(thumb.style.height).toBe("264px")
    expect(thumb.style.cursor).toBe("pointer")
    await waitFor(() => expect(iframe().getAttribute("srcdoc")).toBe(BODY))
    const frame = iframe()
    expect(frame.style.pointerEvents).toBe("none")
    expect(frame.tabIndex).toBe(-1)
    expect(frame.style.transform).toBe("scale(0.25)")
    fireEvent.click(thumb)
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it("thumbnail without onClick has no pointer cursor", async () => {
    serve()
    const { container } = render(<PrintPreview target={{ kind: "base", id: "c1" }} thumbnail />)
    await waitFor(() => expect(iframe()).toBeTruthy())
    expect((container.querySelector(".print-preview-thumb") as HTMLDivElement).style.cursor).toBe("")
  })
})

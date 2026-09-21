import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import ExperienceJobsEditor from "../../../../src/ui/frontend/src/components/ExperienceJobsEditor"

const FIELDS = [
  { key: "company", label: "Company" },
  { key: "title", label: "Title" },
  { key: "dates", label: "Dates" },
  { key: "location", label: "Location" },
  { key: "accomplishments", label: "Accomplishments" },
]

function expandRole(label: RegExp | string) {
  fireEvent.click(screen.getByText(label))
}

describe("ExperienceJobsEditor — AST-1351 / AST-1382", () => {
  it("edits fields, adds/removes/reorders roles (string[] accomplishments + collapsible header)", () => {
    const onChange = vi.fn()
    const { rerender } = render(
      <ExperienceJobsEditor
        fields={FIELDS}
        value={[
          {
            company: "Acme",
            title: "Eng",
            dates: "2020",
            location: "",
            accomplishments: ["Did stuff"],
          },
        ]}
        onChange={onChange}
      />,
    )
    // AST-1381/1382: collapsed header uses company, title / dates — not Role N.
    expect(screen.getByText("Acme, Eng / 2020")).toBeInTheDocument()
    expect(screen.queryByText("Role 1")).not.toBeInTheDocument()
    expandRole("Acme, Eng / 2020")
    fireEvent.change(screen.getByDisplayValue("Acme"), { target: { value: "Beta" } })
    expect(onChange).toHaveBeenLastCalledWith([
      {
        company: "Beta",
        title: "Eng",
        dates: "2020",
        location: "",
        accomplishments: ["Did stuff"],
      },
    ])

    onChange.mockClear()
    fireEvent.click(screen.getByRole("button", { name: "Add role" }))
    expect(onChange).toHaveBeenLastCalledWith([
      {
        company: "Acme",
        title: "Eng",
        dates: "2020",
        location: "",
        accomplishments: ["Did stuff"],
      },
      {
        company: "",
        title: "",
        dates: "",
        location: "",
        accomplishments: [],
      },
    ])

    const twoJobs = [
      {
        company: "First",
        title: "A",
        dates: "1",
        location: "",
        accomplishments: ["x"],
      },
      {
        company: "Second",
        title: "B",
        dates: "2",
        location: "",
        accomplishments: ["y"],
      },
    ]
    rerender(<ExperienceJobsEditor fields={FIELDS} value={twoJobs} onChange={onChange} />)
    expect(screen.getByText("First, A / 1")).toBeInTheDocument()
    expect(screen.getByText("Second, B / 2")).toBeInTheDocument()
    onChange.mockClear()
    fireEvent.click(screen.getAllByTitle("Move down")[0])
    expect(onChange).toHaveBeenLastCalledWith([twoJobs[1], twoJobs[0]])

    onChange.mockClear()
    fireEvent.click(screen.getAllByTitle("Remove")[0])
    expect(onChange).toHaveBeenLastCalledWith([twoJobs[1]])
  })

  it("allows emptying to [] via Remove on last role", () => {
    const onChange = vi.fn()
    render(
      <ExperienceJobsEditor
        fields={FIELDS}
        value={[
          {
            company: "Solo",
            title: "T",
            dates: "2024",
            location: "",
            accomplishments: [],
          },
        ]}
        onChange={onChange}
      />,
    )
    expect(screen.getByText("Solo, T / 2024")).toBeInTheDocument()
    fireEvent.click(screen.getByTitle("Remove"))
    expect(onChange).toHaveBeenLastCalledWith([])
  })
})

import { screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { expect } from "vitest"

// AST-1982: shared Job Title cell checks for the list pages (Ready / Review, Processing, Skipped, Applied, Meteorites).

// 79 chars; "Zanzibar" starts past char 50, so a search hit on it proves search reads the full title.
export const LONG_TITLE = "Principal Software Engineer, Distributed Platform Reliability \u2014 Zanzibar Office"
export const CUT_TITLE = `${LONG_TITLE.slice(0, 50)}\u2026`
// Exactly 50 chars — the boundary stays uncut.
export const EDGE_TITLE = "Edge Title Exactly At The Fifty Character Limit ok"

export function jobTitleJobs(base: Record<string, unknown>) {
  return [
    { ...base, astral_job_id: "jt-long", job_title: LONG_TITLE },
    { ...base, astral_job_id: "jt-edge", job_title: EDGE_TITLE },
  ]
}

// AC1–3 on one rendered table holding jobTitleJobs() rows. header = the Job Title column label.
export async function expectJobTitleCells(table: HTMLElement, header: RegExp = /^Job Title/) {
  // DOM query, not getAllByRole: Skipped's below-floor spacer <th aria-hidden> must still count toward cell indices.
  const headers = Array.from(table.querySelectorAll<HTMLElement>("thead th"))
  const col = headers.findIndex(h => header.test(h.textContent ?? ""))
  expect(col).toBeGreaterThan(-1)
  // Job rows only — Recommended's Analysis row is a single colSpan cell.
  const cells = within(table).getAllByRole("row").slice(1)
    .filter(r => r.children.length === headers.length)
    .map(r => r.children[col] as HTMLElement)
  const long = cells.find(c => c.textContent === CUT_TITLE)
  const edge = cells.find(c => c.textContent === EDGE_TITLE)
  expect(long, "long title cell = first 50 chars + …").toBeTruthy()
  expect(edge, "50-char title cell shown exactly").toBeTruthy()
  expect(within(table).queryByText(LONG_TITLE)).toBeNull()
  // No native title tooltip anywhere in either cell.
  for (const c of [long!, edge!]) expect([c, ...c.querySelectorAll("*")].some(e => e.hasAttribute("title"))).toBe(false)

  // AC2: short title — hover renders no tooltip.
  await userEvent.hover(edge!)
  expect(screen.queryByRole("tooltip")).toBeNull()
  await userEvent.unhover(edge!)

  await expectFullTitleTooltip(within(long!).getByText(CUT_TITLE), table)
}

// AC3 (AST-1982): hovering the cut span shows one tooltip with the full title, portaled straight to body
// (outside `host` — a table, or a modal / report header), gone on mouse-out.
export async function expectFullTitleTooltip(span: HTMLElement, host: HTMLElement) {
  await userEvent.hover(span)
  const tips = screen.getAllByRole("tooltip")
  expect(tips).toHaveLength(1)
  expect(tips[0].textContent).toBe(LONG_TITLE)
  expect(tips[0]).toHaveClass("job-title-tooltip")
  expect(tips[0].parentElement).toBe(document.body)
  expect(host.contains(tips[0])).toBe(false)
  await userEvent.unhover(span)
  expect(screen.queryByRole("tooltip")).toBeNull()
}

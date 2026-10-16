import { within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { expect, type Mock } from "vitest"
import { fmtTime } from "../../../../src/ui/frontend/src/lib/fmt"
import { baseCandidate, jsonResponse } from "./page-mocks"

// AST-1979: shared Created-column checks for the job list pages (Ready / Review, Processing, Skipped, Applied).

// Non-UTC so a Created cell rendered in the wrong zone shows a different day (12/15 23:30Z → 12/16 in Tokyo).
export const CREATED_TZ = "Asia/Tokyo"

// Created order (null, mid, late) differs from the default state_changed_at-desc order (mid, null, late),
// so default load, first click, and second click each produce a distinct row order.
export function createdColumnJobs(base: Record<string, unknown>) {
  return [
    { ...base, astral_job_id: "cr-mid", job_title: "Created Mid", created_at: "2025-12-01T10:00:00Z", state_changed_at: "2026-01-03T00:00:00Z" },
    { ...base, astral_job_id: "cr-null", job_title: "Created Null", created_at: null, state_changed_at: "2026-01-02T00:00:00Z" },
    { ...base, astral_job_id: "cr-late", job_title: "Created Late", created_at: "2025-12-15T23:30:00Z", state_changed_at: "2026-01-01T00:00:00Z" },
  ]
}

// Call after installBaseApiMocks: re-serves the base candidate with CREATED_TZ so <Time> renders in that zone.
export function installTzCandidate(mockedApi: Mock) {
  const base = mockedApi.getMockImplementation()!
  const contact = { ...baseCandidate.candidate_data.contact, timezone: CREATED_TZ }
  const candidate = { ...baseCandidate, candidate_data: { ...baseCandidate.candidate_data, contact } }
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) =>
    url === "/api/candidates" ? jsonResponse([candidate]) : base(url, init))
}

// AC1–4 on one rendered job table holding exactly createdColumnJobs() rows.
// updatedLabel is the neighbouring header (/^Updated/ or /^Failed At/).
export async function expectCreatedColumn(table: HTMLElement, updatedLabel: RegExp) {
  // DOM query, not getAllByRole: Skipped's below-floor spacer <th aria-hidden> must still count toward cell indices.
  const headers = () => Array.from(table.querySelectorAll<HTMLElement>("thead th"))
  const idx = (re: RegExp) => headers().findIndex(h => re.test(h.textContent ?? ""))
  const created = idx(/^Created/)
  const title = idx(/^Job Title/)

  // AC1: Created sits immediately left of Updated / Failed At.
  expect(created).toBeGreaterThan(-1)
  expect(idx(updatedLabel)).toBe(created + 1)

  // Job rows only — Recommended's Analysis row is a single colSpan cell.
  const rows = () => within(table).getAllByRole("row").slice(1).filter(r => r.children.length === headers().length)
  const titles = () => rows().map(r => r.children[title].textContent)
  const cellText = (jobTitle: string, col: number) =>
    rows().find(r => r.children[title].textContent === jobTitle)!.children[col].textContent

  // AC2: Created = fmtTime(created_at, candidate tz); Updated in the same zone; null → em dash.
  for (const j of createdColumnJobs({})) {
    expect(cellText(j.job_title, created)).toBe(fmtTime(j.created_at, CREATED_TZ))
    expect(cellText(j.job_title, created + 1)).toBe(fmtTime(j.state_changed_at, CREATED_TZ))
  }
  expect(cellText("Created Null", created)).toBe("\u2014")
  expect(cellText("Created Late", created)).toMatch(/^12\/16\/25/)

  // AC4: default load is still state_changed_at desc; no indicator on Created.
  expect(titles()).toEqual(["Created Mid", "Created Null", "Created Late"])
  expect(headers()[created].textContent).toBe("Created")

  // AC3: first click ascending (null first, like null state_changed_at); second click reverses; indicator on Created only.
  await userEvent.click(headers()[created])
  expect(titles()).toEqual(["Created Null", "Created Mid", "Created Late"])
  expect(headers()[created].textContent).toBe("Created\u25B2")
  expect(headers()[created + 1].textContent).not.toMatch(/[\u25B2\u25BC]/)
  await userEvent.click(headers()[created])
  expect(titles()).toEqual(["Created Late", "Created Mid", "Created Null"])
  expect(headers()[created].textContent).toBe("Created\u25BC")
}

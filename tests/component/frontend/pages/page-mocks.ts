import type { Mock } from "vitest"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"

export const candidateId = "c1"

export const baseCandidate = {
  astral_candidate_id: candidateId,
  state: "ACTIVE",
  candidate_data: {
    profile: {
      contact_email: "ada@example.com",
      linkedin_url: "https://linkedin.com/in/ada",
    },
    artifacts: {
      like_rubric: [
        { code: "TE", label: "Technical (TE)", importance: 2 },
        { code: "CU", label: "Culture (CU)", importance: 1 },
      ],
      joblist_rubric: [{ code: "JL", label: "Job List (JL)", importance: 1 }],
      jobdesc_rubric: [{ code: "JD", label: "Job Description (JD)", importance: 1 }],
    },
  },
}

export function jsonResponse<T>(body: T, init: Partial<Response> = {}): Response {
  return { json: async () => body, ok: init.ok ?? true, ...init } as Response
}

type ApiHandler = (url: string, init?: RequestInit) => Promise<Response> | Response

export function installBaseApiMocks(mockedApi: Mock, handler: ApiHandler) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/candidates") {
      return jsonResponse([baseCandidate])
    }
    if (url === "/api/state_ui_manifest") {
      return jsonResponse(STATE_UI_MANIFEST_FIXTURE)
    }
    if (url === "/api/system/ui_config") {
      return jsonResponse({ column_types: {} })
    }
    return handler(url, init)
  })
}

export const companyColumns = {
  watch_list: [{ key: "company_name", label: "Company" }],
  new_list: [{ key: "company_name", label: "Company" }],
  inactive_list: [{ key: "company_name", label: "Company" }],
  ignored: [{ key: "company_name", label: "Company" }],
  watch_history: [
    { key: "company_name", label: "Company" },
    { key: "status", label: "Status" },
  ],
}

export function companyListHandler(view: string, rows: unknown[], listKey: keyof typeof companyColumns) {
  return (url: string) => {
    if (url === `/api/companies?view=${view}&candidate_id=${candidateId}`) {
      return jsonResponse(rows)
    }
    if (url === "/api/shapes/companies") {
      return jsonResponse({ list: { [listKey]: companyColumns[listKey] } })
    }
    if (url.startsWith("/api/companies/") && !url.includes("bulk_state") && !url.includes("import") && !url.includes("scan_history")) {
      return jsonResponse({
        short_name: "acme",
        company_name: "Acme Corp",
        company_website: "https://acme.test",
        state: "WATCH",
        state_history: [],
        job_state_counts: {},
        agent_story: [],
      })
    }
    throw new Error(`unexpected api call: ${url}`)
  }
}

export function jobsViewHandler(view: string, rows: unknown[]) {
  return (url: string, init?: RequestInit) => {
    if (url === `/api/jobs?view=${view}&candidate_id=${candidateId}` && !init) {
      return jsonResponse(rows)
    }
    if (url.startsWith("/api/jobs/") && !url.includes("bulk_state") && !init) {
      const jobId = url.slice("/api/jobs/".length)
      const row = (rows as Array<{ astral_job_id: string }>).find(j => j.astral_job_id === jobId)
      return jsonResponse(row ?? { astral_job_id: jobId, job_title: "Job", company: "Acme", state: "NEW", state_history: [], job_data: {} })
    }
    if (url === "/api/jobs/bulk_state" && init?.method === "POST") {
      return jsonResponse({ updated: 1 })
    }
    if (/\/api\/jobs\/[^/]+\/(skip|candidate_action)$/.test(url) && init?.method === "POST") {
      return jsonResponse({ ok: true })
    }
    throw new Error(`unexpected api call: ${url}${init?.method ? ` ${init.method}` : ""}`)
  }
}

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import api from "../lib/api"
import { useAuth } from "./AuthContext"

/** Mirrors `build_state_ui_manifest()` in `src/utils/config.py`. */
export interface StateUiManifest {
  jobs: {
    in_review_sections: Array<{ state: string; label: string }>
    grade_field_by_job_state: Record<string, string>
    grade_rubric_by_field: Record<string, string>
    skipped: {
      below_dispatch_key: string
      below_dispatch_label: string
      section_order: string[]
      section_labels: Record<string, string>
      bulk_retry_to_state: string
    }
    detail: { already_skipped_state: string }
    recommended: {
      sections: Array<{ state: string; label: string }>
      phase_score_columns: Array<{ field: string; label: string }>
      primary_actions_by_state?: Record<string, Array<{
        action_key: string
        label: string
        method: string
        path_suffix: string
      }>>
      report_fixed_tabs?: Array<{ tab_id: string; nav_label: string }>
      report_phase_tabs?: Array<{
        tab_id: string
        nav_label: string
        grades_field: string
        take_key: string
      }>
      report_artifact_tabs?: Array<{
        tab_id: string
        nav_label: string
        artifact_key: string
        shapes_key: string | null
        use_resume_structure: boolean
      }>
    }
  }
  candidate: { artifact_generate_states: string[] }
  company: {
    watch_readonly_states: string[]
    bulk_transitions: Record<string, string>
  }
}

export type StateUiLoadState = "loading" | "ready" | "error"

export type StateUiContextValue = {
  manifest: StateUiManifest | null
  loadState: StateUiLoadState
}

const defaultValue: StateUiContextValue = { manifest: null, loadState: "loading" }

const StateUiContext = createContext<StateUiContextValue>(defaultValue)

export function StateUiProvider({ children }: { children: ReactNode }) {
  const { loading: authLoading } = useAuth()
  const [value, setValue] = useState<StateUiContextValue>(defaultValue)
  useEffect(() => {
    if (authLoading) return
    api("/api/state_ui_manifest")
      .then(r => { if (!r.ok) throw new Error(String(r.status)); return r.json() })
      .then((body: StateUiManifest) => setValue({ manifest: body, loadState: "ready" }))
      .catch(() => setValue({ manifest: null, loadState: "error" }))
  }, [authLoading])
  return <StateUiContext.Provider value={value}>{children}</StateUiContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useStateUi(): StateUiContextValue {
  return useContext(StateUiContext)
}

export type Catalog = {
  body_formats: string[]
  required_ids: string[]
  contact_ids: string[]
  extra_id_pattern: string
  reserved_extra_ids: string[]
  new_extra_default_format: string
}

export type SectionRow = {
  id: string
  title: string
  enabled: boolean
  order: number
  format: string | null
  job_agent_editable: boolean
  required: boolean
  format_locked: boolean
}

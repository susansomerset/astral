import { describe, expect, it } from "vitest"
import { resolveJobTitleTruncateChars } from "../../../../src/ui/frontend/src/lib/uiConfig"

describe("uiConfig resolvers", () => {
  // AST-1982: served job_title_truncate_chars wins; falls back to 50 before load or on a bad value.
  it("resolveJobTitleTruncateChars uses the served value, else 50", () => {
    expect(resolveJobTitleTruncateChars({ column_types: {}, job_title_truncate_chars: 20 })).toBe(20)
    expect(resolveJobTitleTruncateChars({ column_types: {} })).toBe(50)
    expect(resolveJobTitleTruncateChars({ column_types: {}, job_title_truncate_chars: 0 })).toBe(50)
    expect(resolveJobTitleTruncateChars(null)).toBe(50)
  })
})

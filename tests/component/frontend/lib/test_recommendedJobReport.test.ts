import { describe, expect, it } from "vitest"
import { emailWithJobPlusTag } from "../../../../src/ui/frontend/src/lib/recommendedJobReport"

describe("recommendedJobReport — AST-499 UAT", () => {
  it("emailWithJobPlusTag inserts job id before @", () => {
    expect(emailWithJobPlusTag("ada@example.com", "j565")).toBe("ada+j565@example.com")
    expect(emailWithJobPlusTag("ada@example.com", "")).toBe("ada@example.com")
    expect(emailWithJobPlusTag("", "j565")).toBe("")
  })
})

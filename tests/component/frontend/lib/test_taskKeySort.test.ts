import { describe, expect, it } from "vitest"
import {
  compareTaskKeys,
  sortedTaskKeys,
} from "../../../../src/ui/frontend/src/lib/taskKeySort"

describe("taskKeySort (AST-1215)", () => {
  it("compareTaskKeys is plain lexicographic (not localeCompare)", () => {
    expect(compareTaskKeys("a", "b")).toBe(-1)
    expect(compareTaskKeys("b", "a")).toBe(1)
    expect(compareTaskKeys("same", "same")).toBe(0)
    // Underscore / ASCII ordinal — matches Python sorted() / SQLite ORDER BY task_key.
    expect(compareTaskKeys("fetch_jd", "fetch_job_pages")).toBe(-1)
    expect(compareTaskKeys("meteorite_grade_do", "meteorite_grade_get")).toBe(-1)
  })

  it("sortedTaskKeys orders an unsorted iterable", () => {
    expect(sortedTaskKeys(["zebra", "alpha", "meteorite_grade_do", "fetch_jd"])).toEqual([
      "alpha",
      "fetch_jd",
      "meteorite_grade_do",
      "zebra",
    ])
    expect(sortedTaskKeys(new Set(["c", "a", "b"]))).toEqual(["a", "b", "c"])
  })
})

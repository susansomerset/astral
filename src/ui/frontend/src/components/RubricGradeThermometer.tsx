const GRADE_ORDER = ["A", "B", "C", "D", "F", "X"] as const

export interface RubricGradeLetter {
  grade: string
  count: number
  last_seen: string
}

export default function RubricGradeThermometer({ letters }: { letters: RubricGradeLetter[] }) {
  const kept = letters
    .map(letter => ({
      grade: letter.grade.trim().toUpperCase(),
      count: letter.count,
      last_seen: letter.last_seen,
    }))
    .filter(letter =>
      (GRADE_ORDER as readonly string[]).includes(letter.grade)
      && typeof letter.count === "number"
      && letter.count > 0,
    )
    .sort((a, b) => GRADE_ORDER.indexOf(a.grade as typeof GRADE_ORDER[number])
      - GRADE_ORDER.indexOf(b.grade as typeof GRADE_ORDER[number]))

  return (
    <div className="rubric-grade-thermometer">
      {kept.map(letter => {
        const date = (letter.last_seen ?? "").trim().slice(0, 10)
        return (
          <div
            key={letter.grade}
            className={`rubric-grade-thermometer-seg seg-${letter.grade.toLowerCase()}`}
            style={{ flexGrow: letter.count, flexBasis: 0 }}
            title={`${letter.grade}, ${letter.count}, ${date}`}
          />
        )
      })}
    </div>
  )
}

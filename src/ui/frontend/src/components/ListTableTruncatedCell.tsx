import { truncateForDisplay } from "../lib/listTableLayout"

export default function ListTableTruncatedCell({
  text,
  maxChars,
}: {
  text: string
  maxChars: number
}) {
  const { display, full } = truncateForDisplay(text, maxChars)
  if (full.length <= maxChars) return <>{display}</>
  return <span title={full}>{display}</span>
}

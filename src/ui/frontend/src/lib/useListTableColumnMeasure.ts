import { useLayoutEffect, useState, type RefObject } from "react"
import { mergeWidthsForSticky, measureListTableColumnWidths } from "./listTableLayout"

function widthsEqual(a: Record<string, number>, b: Record<string, number>): boolean {
  const aKeys = Object.keys(a)
  if (aKeys.length !== Object.keys(b).length) return false
  for (const k of aKeys) {
    if (a[k] !== b[k]) return false
  }
  return true
}

export function useListTableColumnMeasure(
  tableRef: RefObject<HTMLTableElement | null>,
  orderedKeys: string[],
  hasCheckbox: boolean,
  persistedWidths: Record<string, number>,
  deps: unknown[],
) {
  const [checkboxWidthPx, setCheckboxWidthPx] = useState(40)
  const [mergedWidths, setMergedWidths] = useState<Record<string, number>>(() =>
    mergeWidthsForSticky(persistedWidths, {}),
  )

  const orderedKeysKey = orderedKeys.join("\0")
  const persistedKey = JSON.stringify(persistedWidths)

  useLayoutEffect(() => {
    const table = tableRef.current
    if (!table) return
    const { checkboxWidthPx: cb, dataWidths } = measureListTableColumnWidths(
      table,
      orderedKeys,
      hasCheckbox,
    )
    setCheckboxWidthPx(prev => (prev === cb ? prev : cb))
    setMergedWidths(prev => {
      const next = mergeWidthsForSticky(persistedWidths, dataWidths)
      return widthsEqual(prev, next) ? prev : next
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps -- plan deps array for re-measure triggers
  }, [tableRef, orderedKeysKey, hasCheckbox, persistedKey, ...deps])

  return { checkboxWidthPx, mergedWidths }
}

import { useLayoutEffect, useState, type RefObject } from "react"
import { mergeWidthsForSticky, measureListTableColumnWidths } from "./listTableLayout"

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

  useLayoutEffect(() => {
    const table = tableRef.current
    if (!table) return
    const { checkboxWidthPx: cb, dataWidths } = measureListTableColumnWidths(
      table,
      orderedKeys,
      hasCheckbox,
    )
    setCheckboxWidthPx(cb)
    setMergedWidths(mergeWidthsForSticky(persistedWidths, dataWidths))
  // eslint-disable-next-line react-hooks/exhaustive-deps -- plan deps array for re-measure triggers
  }, [tableRef, orderedKeys, hasCheckbox, persistedWidths, ...deps])

  return { checkboxWidthPx, mergedWidths }
}

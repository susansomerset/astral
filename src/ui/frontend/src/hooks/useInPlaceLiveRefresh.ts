import { useCallback, useState } from "react"

export type InPlaceLiveRefresh = {
  /** True while a spinner-requested fetch is in flight (first paint / new query identity). */
  loading: boolean
  /**
   * Call at the start of a refetch.
   * `showSpinner: true` — first paint, or a new query identity (filters that change the request).
   * Omit / false — poll, post-mutation, session revalidation: merge into the current view.
   */
  beginRefresh: (showSpinner?: boolean) => void
  /** Call in the fetch `finally`. Always clears `loading`. */
  endRefresh: () => void
}

export function useInPlaceLiveRefresh(): InPlaceLiveRefresh {
  const [loading, setLoading] = useState(true)

  const beginRefresh = useCallback((showSpinner = false) => {
    if (showSpinner) setLoading(true)
  }, [])

  const endRefresh = useCallback(() => {
    setLoading(false)
  }, [])

  return { loading, beginRefresh, endRefresh }
}

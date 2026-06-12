import { useState, useEffect, useCallback } from "react"

/**
 * useState backed by localStorage. Reads once on mount, writes on every change.
 * Safe to use with strings, numbers, booleans, and plain JSON-serializable objects.
 */
export function useLocalStorage<T>(key: string, defaultValue: T): [T, (val: T | ((prev: T) => T)) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = localStorage.getItem(key)
      return raw !== null ? (JSON.parse(raw) as T) : defaultValue
    } catch { return defaultValue }
  })

  useEffect(() => {
    try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* quota, private mode */ }
  }, [key, value])

  const set = useCallback((val: T | ((prev: T) => T)) => setValue(val), [])
  return [value, set]
}

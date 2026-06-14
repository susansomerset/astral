import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"

export default function AdminRoute({ children }: { children: ReactNode }) {
  const { isAdmin, loading } = useAuth()

  if (loading) {
    return <p>Loading…</p>
  }
  if (!isAdmin) {
    return <Navigate to="/jobs/recommended" replace />
  }
  return children
}

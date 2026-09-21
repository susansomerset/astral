import { createBrowserRouter, RouterProvider } from "react-router-dom"
import { StytchProvider } from "@stytch/react"
import { AuthProvider } from "./contexts/AuthContext"
import { stytchClient } from "./lib/stytchClient"
import routes from "./routes"
import "./App.css"

const router = createBrowserRouter(routes)

export default function App() {
  return (
    <StytchProvider stytch={stytchClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </StytchProvider>
  )
}

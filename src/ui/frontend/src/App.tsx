import { BrowserRouter, useRoutes } from "react-router-dom"
import { StytchProvider } from "@stytch/react"
import { AuthProvider } from "./contexts/AuthContext"
import { stytchClient } from "./lib/stytchClient"
import routes from "./routes"
import "./App.css"

function AppRoutes() {
  return useRoutes(routes)
}

export default function App() {
  return (
    <BrowserRouter>
      <StytchProvider stytch={stytchClient}>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </StytchProvider>
    </BrowserRouter>
  )
}

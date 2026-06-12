import { BrowserRouter, useRoutes } from "react-router-dom"
import { CandidateProvider } from "./contexts/CandidateContext"
import { StateUiProvider } from "./contexts/StateUiContext"
import routes from "./routes"
import "./App.css"

function AppRoutes() {
  return useRoutes(routes)
}

export default function App() {
  return (
    <BrowserRouter>
      <StateUiProvider>
        <CandidateProvider>
          <AppRoutes />
        </CandidateProvider>
      </StateUiProvider>
    </BrowserRouter>
  )
}

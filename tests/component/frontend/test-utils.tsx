import { render, type RenderOptions } from '@testing-library/react'
import { MemoryRouter, type MemoryRouterProps } from 'react-router-dom'
import type { ReactElement, ReactNode } from 'react'
import { UserPromptProvider } from '../../../src/ui/frontend/src/components/UserPrompt'
import { CandidateProvider } from '../../../src/ui/frontend/src/contexts/CandidateContext'
import { StateUiProvider } from '../../../src/ui/frontend/src/contexts/StateUiContext'

type WrapperOptions = {
  router?: MemoryRouterProps
}

function AllProviders({ children, router }: { children: ReactNode } & WrapperOptions) {
  return (
    <MemoryRouter {...router}>
      {/* Modal + CandidateBoardSearches use useUserConfirm (origin/dev UX); RTL pages need the provider */}
      <UserPromptProvider>
        <StateUiProvider>
          <CandidateProvider>{children}</CandidateProvider>
        </StateUiProvider>
      </UserPromptProvider>
    </MemoryRouter>
  )
}

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & WrapperOptions,
) {
  const { router, ...renderOptions } = options ?? {}
  return render(ui, {
    wrapper: ({ children }) => <AllProviders router={router}>{children}</AllProviders>,
    ...renderOptions,
  })
}

export async function jsonResponse(data: unknown, ok = true): Promise<Response> {
  return { ok, json: async () => data } as Response
}

export function installBaseApiMocks(
  mockedApi: { mockImplementation: (impl: (url: string, init?: RequestInit) => unknown) => void },
  handler: (url: string, init?: RequestInit) => unknown,
) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    const routed = await handler(url, init)
    if (routed !== undefined) return routed
    if (url === "/api/system/ui_config") return jsonResponse({ column_types: {} })
    if (url === "/api/candidates") return jsonResponse([])
    throw new Error(`Unhandled api ${url} ${init?.method ?? "GET"}`)
  })
}

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import api from '../../../../src/ui/frontend/src/lib/api'
import StateTimeline from '../../../../src/ui/frontend/src/components/StateTimeline'
import { renderWithProviders } from '../test-utils'

// AuthProvider (via renderWithProviders) wires these on mount — the mock must export them.
vi.mock('../../../../src/ui/frontend/src/lib/api', () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe('StateTimeline', () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedApi.mockResolvedValue({ json: async () => [] } as Response)
    localStorage.clear()
  })

  it('shows the empty-state message when history is missing or empty', () => {
    const { rerender } = renderWithProviders(<StateTimeline history={[]} />)
    expect(screen.getByText('No state history recorded.')).toBeInTheDocument()

    rerender(<StateTimeline history={undefined as unknown as []} />)
    expect(screen.getByText('No state history recorded.')).toBeInTheDocument()
  })

  it('renders newest entries first with state and timestamp fallbacks', async () => {
    renderWithProviders(
      <StateTimeline
        history={[
          { state: 'OLD', timestamp: '2026-05-14T10:00:00' },
          { to_state: 'NEW', timestamp: '2026-05-14T12:00:00' },
          { timestamp: '2026-05-14T11:00:00' },
        ]}
      />,
    )

    const states = screen.getAllByText(/^NEW$|^\?$|^OLD$/)
    expect(states.map(node => node.textContent)).toEqual(['?', 'NEW', 'OLD'])
    expect(await screen.findAllByText(/5\/14\/26/)).toHaveLength(3)
  })
})

describe('StateTimeline — AST-1865 run selection', () => {
  const history = [
    { to_state: 'HOP', timestamp: '2026-05-14T12:00:00', run_id: 'hop-H', batch_id: 'claim-C' },
    { to_state: 'LEGACY', timestamp: '2026-05-14T11:00:00', batch_id: 'legacy-B' },
    { to_state: 'MANUAL', timestamp: '2026-05-14T10:00:00' },
  ]

  beforeEach(() => {
    mockedApi.mockReset()
    mockedApi.mockResolvedValue({ json: async () => [] } as Response)
  })

  it('no onSelectRun → no row is clickable, even with run ids', () => {
    renderWithProviders(<StateTimeline history={history} />)
    expect(screen.queryAllByRole('button')).toHaveLength(0)
    expect(screen.queryByTitle(/^Open run /)).not.toBeInTheDocument()
  })

  it('run_id wins over batch_id; legacy batch_id-only row falls back; neither → inert', async () => {
    const onSelectRun = vi.fn()
    renderWithProviders(<StateTimeline history={history} onSelectRun={onSelectRun} />)

    // Exactly the two rows that resolve a run id get the affordance
    expect(screen.getAllByRole('button')).toHaveLength(2)
    expect(screen.queryByTitle('Open run claim-C')).not.toBeInTheDocument()
    expect(screen.getByText('MANUAL').closest('[role="button"]')).toBeNull()
    expect(screen.getByText('MANUAL').closest('[tabindex]')).toBeNull()

    await userEvent.click(screen.getByTitle('Open run hop-H'))
    await userEvent.click(screen.getByTitle('Open run legacy-B'))
    await userEvent.click(screen.getByText('MANUAL'))
    expect(onSelectRun.mock.calls).toEqual([['hop-H'], ['legacy-B']])
  })

  it('Enter and Space activate a clickable row; other keys do not', async () => {
    const onSelectRun = vi.fn()
    renderWithProviders(<StateTimeline history={history.slice(0, 1)} onSelectRun={onSelectRun} />)
    screen.getByTitle('Open run hop-H').focus()
    await userEvent.keyboard('{Enter}')
    await userEvent.keyboard(' ')
    await userEvent.keyboard('a')
    expect(onSelectRun.mock.calls).toEqual([['hop-H'], ['hop-H']])
  })
})

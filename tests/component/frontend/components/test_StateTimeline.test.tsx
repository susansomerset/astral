import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import api from '../../../../src/ui/frontend/src/lib/api'
import StateTimeline from '../../../../src/ui/frontend/src/components/StateTimeline'
import { renderWithProviders } from '../test-utils'

vi.mock('../../../../src/ui/frontend/src/lib/api', () => ({
  default: vi.fn(),
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

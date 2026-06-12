import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import api from '../../../../src/ui/frontend/src/lib/api'
import Time from '../../../../src/ui/frontend/src/components/Time'
import { renderWithProviders } from '../test-utils'

vi.mock('../../../../src/ui/frontend/src/lib/api', () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe('Time', () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedApi.mockResolvedValue({ json: async () => [] } as Response)
    localStorage.clear()
  })

  it('formats timestamps using the selected candidate timezone', async () => {
    mockedApi.mockResolvedValue({
      json: async () => [
        {
          astral_candidate_id: 'c1',
          state: 'ACTIVE',
          candidate_data: { profile: { timezone: 'America/New_York' } },
        },
      ],
    } as Response)
    localStorage.setItem('astral_selected_candidate', 'c1')

    renderWithProviders(<Time value="2026-05-14T16:48:11Z" />)
    expect(await screen.findByText('5/14/26, 12:48:11 PM')).toBeInTheDocument()
  })

  it('falls back to UTC when the selected candidate has no timezone', async () => {
    mockedApi.mockResolvedValue({
      json: async () => [
        {
          astral_candidate_id: 'c1',
          state: 'ACTIVE',
          candidate_data: { profile: {} },
        },
      ],
    } as Response)
    localStorage.setItem('astral_selected_candidate', 'c1')

    renderWithProviders(<Time value="2026-05-14T16:48:11Z" />)
    expect(await screen.findByText('5/14/26, 4:48:11 PM')).toBeInTheDocument()
  })

  it('renders the empty placeholder for missing values', () => {
    renderWithProviders(<Time value={null} />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })
})

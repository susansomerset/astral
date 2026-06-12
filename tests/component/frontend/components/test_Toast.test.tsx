import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Toast from '../../../../src/ui/frontend/src/components/Toast'

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => {
      cb(0)
      return 1
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('renders nothing when there is no message', () => {
    const { container } = render(<Toast message={null} onDone={vi.fn()} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows success, error, and default info variants then calls onDone', () => {
    const onDone = vi.fn()
    const { rerender } = render(
      <Toast message={{ text: 'Saved', variant: 'success', durationMs: 1000 }} onDone={onDone} />,
    )

    expect(screen.getByText('Saved')).toBeInTheDocument()
    expect(screen.getByText('\u2713')).toBeInTheDocument()
    expect(document.querySelector('.toast-visible')).toBeTruthy()

    act(() => {
      vi.advanceTimersByTime(1000)
    })
    act(() => {
      vi.advanceTimersByTime(300)
    })
    expect(onDone).toHaveBeenCalledTimes(1)

    rerender(<Toast message={{ text: 'Failed', variant: 'error' }} onDone={onDone} />)
    expect(screen.getByText('Failed')).toBeInTheDocument()
    expect(screen.getByText('\u2717')).toBeInTheDocument()

    rerender(<Toast message={{ text: 'Heads up' }} onDone={onDone} />)
    expect(screen.getByText('Heads up')).toBeInTheDocument()
    expect(screen.getByText('\u2139')).toBeInTheDocument()
  })
})

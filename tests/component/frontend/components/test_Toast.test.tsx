import { act, fireEvent, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Toast from '../../../../src/ui/frontend/src/components/Toast'
import { renderWithProviders } from '../test-utils'

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => {
      cb(0)
      return 1
    })
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  function renderToast(
    message: Parameters<typeof Toast>[0]['message'],
    onDone = vi.fn(),
    router = { initialEntries: ['/admin/agents'] },
  ) {
    return renderWithProviders(<Toast message={message} onDone={onDone} />, { router })
  }

  it('renders nothing when there is no message', () => {
    const { container } = renderToast(null)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows success, error, and default info variants then calls onDone', () => {
    const onDone = vi.fn()
    const { rerender } = renderWithProviders(
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

  it('AST-779: error toast defaults to 15000ms dismiss', () => {
    const onDone = vi.fn()
    renderToast({ text: 'Server error', variant: 'error' }, onDone)

    act(() => {
      vi.advanceTimersByTime(14999)
    })
    expect(onDone).not.toHaveBeenCalled()

    act(() => {
      vi.advanceTimersByTime(1)
    })
    act(() => {
      vi.advanceTimersByTime(300)
    })
    expect(onDone).toHaveBeenCalledTimes(1)
  })

  it('AST-779: success toast still dismisses at 3000ms default', () => {
    const onDone = vi.fn()
    renderToast({ text: 'Saved', variant: 'success' }, onDone)

    act(() => {
      vi.advanceTimersByTime(2999)
    })
    expect(onDone).not.toHaveBeenCalled()

    act(() => {
      vi.advanceTimersByTime(1)
    })
    act(() => {
      vi.advanceTimersByTime(300)
    })
    expect(onDone).toHaveBeenCalledTimes(1)
  })

  it('AST-779: error toast is clickable and copies diagnostic bundle', async () => {
    const writeText = vi.mocked(navigator.clipboard.writeText)
    renderToast({
      text: 'Load failed',
      variant: 'error',
      diagnostics: { api_path: '/api/admin/agents', http_status: 500 },
    })

    expect(document.querySelector('.toast-error-clickable')).toBeTruthy()
    expect(screen.getByText('Click to copy')).toBeInTheDocument()

    await act(async () => {
      fireEvent.click(screen.getByRole('button'))
    })

    expect(writeText).toHaveBeenCalledTimes(1)
    const bundle = writeText.mock.calls[0][0] as string
    expect(bundle).toContain('message: Load failed')
    expect(bundle).toContain('route: /admin/agents')
    expect(bundle).toContain('api_path: /api/admin/agents')

    expect(screen.getByText('Copied to clipboard')).toBeInTheDocument()

    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(screen.getByText('Load failed')).toBeInTheDocument()
  })
})

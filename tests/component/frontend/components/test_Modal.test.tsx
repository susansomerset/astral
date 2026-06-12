import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { describe, expect, it, vi } from 'vitest'
import Modal from '../../../../src/ui/frontend/src/components/Modal'
import { UserPromptProvider } from '../../../../src/ui/frontend/src/components/UserPrompt'

function wrap(node: ReactNode) {
  return <UserPromptProvider>{node}</UserPromptProvider>
}

describe('Modal', () => {
  it('renders nothing when closed', () => {
    const { container } = render(
      wrap(
        <Modal open={false} onClose={vi.fn()} title="Closed">
          Body
        </Modal>,
      ),
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('closes immediately when there are no unsaved changes', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(
      wrap(
        <Modal open onClose={onClose} title="Open" size="wide" stacked>
          <p>Body</p>
        </Modal>,
      ),
    )

    expect(screen.getByRole('heading', { name: 'Open' })).toBeInTheDocument()
    expect(document.querySelector('.modal-card--wide')).toBeTruthy()
    expect(document.querySelector('.modal-overlay--stacked')).toBeTruthy()

    await user.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('blocks close when dirty and save is available but discard is declined', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const onSave = vi.fn()

    render(
      wrap(
        <Modal open onClose={onClose} onSave={onSave} dirty title="Dirty">
          <input aria-label="field" defaultValue="x" />
        </Modal>,
      ),
    )

    await user.click(screen.getByRole('button', { name: 'Close' }))
    const prompt = screen.getByRole('alertdialog')
    expect(within(prompt).getByRole('heading', { name: 'Discard changes?' })).toBeInTheDocument()
    await user.click(within(prompt).getByRole('button', { name: 'Cancel' }))
    expect(onClose).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'Close' }))
    await user.click(within(screen.getByRole('alertdialog')).getByRole('button', { name: 'Discard' }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('treats body edits as dirty and saves when requested', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const onSave = vi.fn()

    const view = render(
      wrap(
        <Modal open onClose={onClose} onSave={onSave} title="Edit">
          <input aria-label="field" defaultValue="x" />
        </Modal>,
      ),
    )

    fireEvent.input(screen.getByRole('textbox', { name: 'field' }), { target: { value: 'y' } })
    view.rerender(
      wrap(
        <Modal open onClose={onClose} onSave={onSave} title="Edit">
          <input aria-label="field" defaultValue="y" />
        </Modal>,
      ),
    )
    await user.click(screen.getByRole('button', { name: 'Close' }))
    expect(onClose).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'Save' }))
    expect(onSave).toHaveBeenCalledTimes(1)
  })
})

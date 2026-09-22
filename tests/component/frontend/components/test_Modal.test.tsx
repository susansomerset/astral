import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import Modal from '../../../../src/ui/frontend/src/components/Modal'
import { UserPromptProvider } from '../../../../src/ui/frontend/src/components/UserPrompt'

const appCssPath = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../../../src/ui/frontend/src/App.css',
)

function wrap(node: ReactNode) {
  return <UserPromptProvider>{node}</UserPromptProvider>
}

/** jsdom does not apply App.css imports — inject the product wide-body rule so getComputedStyle tracks App.css. */
function injectWideModalShellCssFromProduct(): string {
  const css = readFileSync(appCssPath, 'utf-8')
  const rule = css.match(/\.modal-card--wide \.modal-body\s*\{[^}]*\}/)
  expect(rule, 'App.css must define .modal-card--wide .modal-body').toBeTruthy()
  const style = document.createElement('style')
  style.setAttribute('data-test', 'ast-1767-wide-modal-shell')
  // Pin card height so tall direct children overflow the shell body.
  style.textContent = `
    .modal-card--wide {
      display: flex;
      flex-direction: column;
      height: 240px;
      overflow: hidden;
    }
    .modal-header { flex-shrink: 0; }
    ${rule![0]}
  `
  document.head.appendChild(style)
  return rule![0]
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

  it('AST-1301: footer Cancel/Save use catalog classes', () => {
    render(
      wrap(
        <Modal open onClose={vi.fn()} onSave={vi.fn()} title="Open">
          <p>Body</p>
        </Modal>,
      ),
    )
    expect(screen.getByRole('button', { name: 'Cancel' })).toHaveClass('btn', 'secondary')
    expect(screen.getByRole('button', { name: 'Save' })).toHaveClass('btn', 'primary')
  })

  it('AST-1302: header close is icon-control', () => {
    render(
      wrap(
        <Modal open onClose={vi.fn()} title="Open">
          <p>Body</p>
        </Modal>,
      ),
    )
    const close = screen.getByRole('button', { name: 'Close' })
    expect(close).toHaveClass('icon-control')
    expect(close).toHaveTextContent('×')
    expect(close).not.toHaveClass('modal-close')
  })

  it('AST-1334: showFooter false omits footer; header Close still closes', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(
      wrap(
        <Modal open onClose={onClose} title="Report" showFooter={false}>
          <p>Body</p>
        </Modal>,
      ),
    )
    expect(document.querySelector('.modal-footer')).toBeNull()
    expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Close' }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })
})

describe('Modal — AST-1767', () => {
  afterEach(() => {
    document.querySelectorAll('style[data-test="ast-1767-wide-modal-shell"]').forEach((el) => el.remove())
  })

  it('[bug-repro] AST-1767: wide Modal body scrolls tall direct children', () => {
    const wideBodyRule = injectWideModalShellCssFromProduct()
    // Source gate: AST-1764 shell contract (red when wide body still uses overflow: hidden).
    expect(wideBodyRule).toMatch(/overflow-y:\s*auto/)
    expect(wideBodyRule).toMatch(/min-height:\s*0/)

    render(
      wrap(
        <Modal open onClose={vi.fn()} title="Shell scroll" size="wide" showFooter={false}>
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} style={{ minHeight: 120 }}>
              {i === 5 ? 'below-fold-marker' : `marker-${i + 1}`}
            </div>
          ))}
        </Modal>,
      ),
    )

    const modalBody = document.querySelector('.modal-card--wide .modal-body') as HTMLElement
    expect(modalBody).toBeTruthy()
    expect(getComputedStyle(modalBody).overflowY).toMatch(/auto|scroll/)

    const marker = screen.getByText('below-fold-marker')
    modalBody.scrollTop = modalBody.scrollHeight
    expect(marker).toBeVisible()
  })
})

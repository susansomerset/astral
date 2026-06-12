import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import CollapsiblePanel from '../../../../src/ui/frontend/src/components/CollapsiblePanel'

describe('CollapsiblePanel', () => {
  it('expands and collapses in uncontrolled mode', async () => {
    const user = userEvent.setup()
    render(
      <CollapsiblePanel label="Section" defaultExpanded metadata="Meta" actions={<button type="button">Act</button>}>
        <p>Body</p>
      </CollapsiblePanel>,
    )

    expect(screen.getByText('Body')).toBeVisible()
    expect(screen.getByText('Meta')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Collapse section' }))
    expect(screen.getByText('Body')).not.toBeVisible()

    await user.click(screen.getByRole('button', { name: 'Expand section' }))
    expect(screen.getByText('Body')).toBeVisible()
  })

  it('opens from the label with click and keyboard when collapsed', async () => {
    const user = userEvent.setup()
    render(
      <CollapsiblePanel label="Section">
        <p>Body</p>
      </CollapsiblePanel>,
    )

    const label = screen.getAllByRole('button', {
      name: 'Section title; use chevron or Enter/Space to expand when collapsed',
    })[0]
    await user.click(label)
    expect(screen.getByText('Body')).toBeVisible()

    await user.click(screen.getByRole('button', { name: 'Collapse section' }))
    label.focus()
    await user.keyboard('{Enter}')
    expect(screen.getByText('Body')).toBeVisible()

    await user.click(screen.getByRole('button', { name: 'Collapse section' }))
    label.focus()
    await user.keyboard(' ')
    expect(screen.getByText('Body')).toBeVisible()
  })

  it('uses controlled expansion and ignores false metadata', () => {
    const onExpandedChange = vi.fn()
    const { rerender } = render(
      <CollapsiblePanel
        label="Controlled"
        expanded={false}
        onExpandedChange={onExpandedChange}
        metadata={false}
        actions={<button type="button">Action</button>}
      >
        <p>Controlled body</p>
      </CollapsiblePanel>,
    )

    expect(screen.queryByText('Controlled body')).not.toBeVisible()
    fireEvent.click(screen.getAllByRole('button', { name: 'Expand section' })[0])
    expect(onExpandedChange).toHaveBeenCalledWith(true)

    rerender(
      <CollapsiblePanel
        label="Controlled"
        expanded
        onExpandedChange={onExpandedChange}
        actions={<button type="button">Action</button>}
      >
        <p>Controlled body</p>
      </CollapsiblePanel>,
    )
    expect(screen.getByText('Controlled body')).toBeVisible()
  })

  it('supports multiple controlled siblings all collapsed', () => {
    const onA = vi.fn()
    const onB = vi.fn()
    render(
      <>
        <CollapsiblePanel label="A" expanded={false} onExpandedChange={onA}>
          <p>Body A</p>
        </CollapsiblePanel>
        <CollapsiblePanel label="B" expanded={false} onExpandedChange={onB}>
          <p>Body B</p>
        </CollapsiblePanel>
      </>,
    )
    expect(screen.queryByText('Body A')).not.toBeVisible()
    expect(screen.queryByText('Body B')).not.toBeVisible()
    fireEvent.click(screen.getAllByRole('button', { name: 'Expand section' })[0])
    expect(onA).toHaveBeenCalledWith(true)
    expect(onB).not.toHaveBeenCalled()
  })
})

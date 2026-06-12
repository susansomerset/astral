import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import RubricModal from '../../../../src/ui/frontend/src/components/RubricModal'
import { UserPromptProvider } from '../../../../src/ui/frontend/src/components/UserPrompt'

describe('RubricModal', () => {
  it('renders nothing when closed', () => {
    const { container } = render(
      <UserPromptProvider>
        <RubricModal open={false} onClose={vi.fn()} vector="Culture" content="Body" />
      </UserPromptProvider>,
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('shows rubric content and falls back when content is missing', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const { rerender } = render(
      <UserPromptProvider>
        <RubricModal open onClose={onClose} vector="Culture" content="Rubric body" />
      </UserPromptProvider>,
    )

    expect(screen.getByRole('heading', { name: 'Rubric — Culture' })).toBeInTheDocument()
    expect(screen.getByText('Rubric body')).toBeInTheDocument()

    rerender(
      <UserPromptProvider>
        <RubricModal open onClose={onClose} vector="Skills" content={null} />
      </UserPromptProvider>,
    )
    expect(screen.getByText('No rubric found for this vector.')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Close' }))
    expect(onClose).toHaveBeenCalled()
  })
})

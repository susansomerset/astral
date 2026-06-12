import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import TabbedTextArea, { TabBar } from '../../../../src/ui/frontend/src/components/TabbedTextArea'

describe('TabbedTextArea', () => {
  it('switches tabs and forwards textarea changes', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <TabbedTextArea
        tabs={[
          { key: 'a', label: 'Tab A', placeholder: 'A placeholder' },
          { key: 'b', label: 'Tab B', disabled: true },
        ]}
        values={{ a: 'alpha' }}
        onChange={onChange}
      />,
    )

    expect(screen.getByDisplayValue('alpha')).toHaveValue('alpha')
    await user.type(screen.getByDisplayValue('alpha'), '!')
    expect(onChange).toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'Tab B' }))
    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeDisabled()
    expect(textarea).toHaveValue('')
  })

  it('renders customPanels instead of textarea when provided', async () => {
    const user = userEvent.setup()
    render(
      <TabbedTextArea
        tabs={[
          { key: 'profile.cover_letter_signature_image', label: 'Signature Image' },
          { key: 'context.bio_summary', label: 'Bio Summary' },
        ]}
        values={{}}
        onChange={() => {}}
        customPanels={{
          'profile.cover_letter_signature_image': <p>JPEG upload panel</p>,
        }}
      />,
    )
    expect(screen.getByText('JPEG upload panel')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Bio Summary' }))
    expect(screen.queryByText('JPEG upload panel')).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('highlights the active tab in TabBar', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <TabBar
        tabs={[
          { key: 'one', label: 'One' },
          { key: 'two', label: 'Two' },
        ]}
        active="one"
        onChange={onChange}
      />,
    )

    expect(screen.getByRole('button', { name: 'One' })).toHaveClass('active')
    await user.click(screen.getByRole('button', { name: 'Two' }))
    expect(onChange).toHaveBeenCalledWith('two')
  })
})

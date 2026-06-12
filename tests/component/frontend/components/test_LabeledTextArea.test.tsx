import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import LabeledTextArea from '../../../../src/ui/frontend/src/components/LabeledTextArea'

describe('LabeledTextArea', () => {
  it('renders a simple heading and textarea with default placeholder', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<LabeledTextArea label="Summary" value="" onChange={onChange} code="AB" />)

    expect(screen.getByRole('heading', { name: 'Summary (AB)' })).toBeInTheDocument()
    const textarea = screen.getByRole('textbox', { name: '' })
    expect(textarea).toHaveAttribute('placeholder', 'Enter summary…')
    await user.type(textarea, 'x')
    expect(onChange).toHaveBeenCalled()
  })

  it('renders criterion metadata controls and importance fallbacks', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    const onCodeChange = vi.fn()
    const onImportanceChange = vi.fn()
    const onImportanceFocus = vi.fn()
    const onImportanceBlur = vi.fn()
    const onLabelChange = vi.fn()

    const { rerender } = render(
      <LabeledTextArea
        label="Culture"
        value="Body"
        onChange={onChange}
        onCodeChange={onCodeChange}
        onImportanceChange={onImportanceChange}
        onImportanceFocus={onImportanceFocus}
        onImportanceBlur={onImportanceBlur}
        onLabelChange={onLabelChange}
        importance={7}
        code="ab"
      />,
    )

    expect(screen.getByLabelText('Importance')).toHaveValue('7')
    fireEvent.focus(screen.getByLabelText('Importance'))
    expect(onImportanceFocus).toHaveBeenCalled()
    await user.selectOptions(screen.getByLabelText('Importance'), '7')
    expect(onImportanceChange).toHaveBeenCalledWith(7)
    fireEvent.blur(screen.getByLabelText('Importance'))
    expect(onImportanceBlur).toHaveBeenCalled()

    fireEvent.change(screen.getByDisplayValue('ab'), { target: { value: 'cd' } })
    expect(onCodeChange).toHaveBeenCalledWith('CD')

    await user.type(screen.getByDisplayValue('Culture'), '!')
    expect(onLabelChange).toHaveBeenCalled()

    rerender(
      <LabeledTextArea
        label="Culture"
        value="Body"
        onChange={onChange}
        onCodeChange={onCodeChange}
        hideTitle
        disabled
        className="custom"
      />,
    )
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
    const textarea = document.querySelector('textarea.custom')
    expect(textarea).toBeDisabled()
    expect(textarea).toHaveClass('custom')

    rerender(
      <LabeledTextArea
        label="Culture"
        value="Body"
        onChange={onChange}
        onCodeChange={onCodeChange}
        onImportanceChange={onImportanceChange}
        importance={99}
      />,
    )
    expect(screen.getByLabelText('Importance')).toHaveValue('5')
  })

  it('hides the title row when requested without code controls', () => {
    render(
      <LabeledTextArea label="Hidden" value="x" onChange={vi.fn()} hideTitle />,
    )
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })
})

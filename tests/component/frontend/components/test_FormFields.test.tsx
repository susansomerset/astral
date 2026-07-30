import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import FormFields, { getByPath, setByPath } from '../../../../src/ui/frontend/src/components/FormFields'

describe('FormFields helpers', () => {
  it('reads and writes nested paths', () => {
    expect(getByPath({ profile: { name: 'Ada' } }, 'profile.name')).toBe('Ada')
    expect(getByPath({ profile: null }, 'profile.name')).toBeUndefined()
    expect(getByPath({ count: 1 }, 'count.next')).toBeUndefined()

    const updated = setByPath({ profile: { name: 'Ada' } }, 'profile.city', 'NYC')
    expect(updated.profile).toEqual({ name: 'Ada', city: 'NYC' })

    const created = setByPath({}, 'profile.name', 'Grace')
    expect(created).toEqual({ profile: { name: 'Grace' } })
  })
})

describe('FormFields', () => {
  it('renders each field type and forwards changes', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <FormFields
        fields={[
          { key: 'name', label: 'Name', type: 'text' },
          { key: 'bio', label: 'Bio', type: 'textarea' },
          {
            key: 'tier',
            label: 'Tier',
            type: 'select',
            options: ['A', { value: 'b', label: 'Beta' }],
          },
          { key: 'enabled', label: 'Enabled', type: 'toggle' },
        ]}
        values={{ name: 'Ada', bio: 'Builder', tier: 'b', enabled: true }}
        onChange={onChange}
      />,
    )

    const inputs = screen.getAllByRole('textbox')
    await user.type(inputs[0], '!')
    await user.type(inputs[1], '!')
    await user.selectOptions(screen.getByRole('combobox'), 'A')
    await user.click(screen.getByRole('checkbox'))
    expect(onChange).toHaveBeenCalled()
    expect(screen.getByText('Enabled', { selector: '.dep-toggle-label' })).toBeInTheDocument()
  })

  it('renders empty strings for missing values', () => {
    render(
      <FormFields
        fields={[
          { key: 'name', label: 'Name', type: 'text' },
          { key: 'bio', label: 'Bio', type: 'textarea' },
          { key: 'tier', label: 'Tier', type: 'select', options: ['A'] },
        ]}
        values={{}}
        onChange={vi.fn()}
      />,
    )

    const inputs = screen.getAllByRole('textbox')
    expect(inputs[0]).toHaveValue('')
    expect(inputs[1]).toHaveValue('')
    expect(screen.getByRole('combobox')).toHaveDisplayValue('A')
  })

  it('shows disabled toggle text for false values', () => {
    render(
      <FormFields
        fields={[{ key: 'enabled', label: 'Enabled', type: 'toggle' }]}
        values={{ enabled: false }}
        onChange={vi.fn()}
      />,
    )
    expect(screen.getByText('Disabled')).toBeInTheDocument()
  })
})

// AST-1081: string_list shape type (websites multi-entry)
describe('FormFields string_list (AST-1081)', () => {
  it('renders rows, Add, edit, and Remove as string[]', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    const { rerender } = render(
      <FormFields
        fields={[{ key: 'contact.websites', label: 'Websites', type: 'string_list' }]}
        values={{ contact: { websites: ['https://a.example'] } }}
        onChange={onChange}
      />,
    )

    expect(screen.getByDisplayValue('https://a.example')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Add' })).toBeInTheDocument()

    await user.type(screen.getByDisplayValue('https://a.example'), 'x')
    expect(onChange).toHaveBeenCalled()
    const editCall = onChange.mock.calls.at(-1)
    expect(editCall?.[0]).toBe('contact.websites')
    expect(Array.isArray(editCall?.[1])).toBe(true)

    onChange.mockClear()
    await user.click(screen.getByRole('button', { name: 'Add' }))
    expect(onChange).toHaveBeenCalledWith('contact.websites', ['https://a.example', ''])

    // Remove first row after re-render with two entries
    rerender(
      <FormFields
        fields={[{ key: 'contact.websites', label: 'Websites', type: 'string_list' }]}
        values={{ contact: { websites: ['https://a.example', 'https://b.example'] } }}
        onChange={onChange}
      />,
    )
    onChange.mockClear()
    await user.click(screen.getAllByRole('button', { name: 'Remove' })[0])
    expect(onChange).toHaveBeenCalledWith('contact.websites', ['https://b.example'])
  })

  it('treats non-array values as empty list', () => {
    render(
      <FormFields
        fields={[{ key: 'contact.websites', label: 'Websites', type: 'string_list' }]}
        values={{ contact: { websites: 'https://not-a-list.example' } }}
        onChange={vi.fn()}
      />,
    )
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Add' })).toBeInTheDocument()
  })
})

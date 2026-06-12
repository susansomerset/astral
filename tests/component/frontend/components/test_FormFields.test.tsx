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

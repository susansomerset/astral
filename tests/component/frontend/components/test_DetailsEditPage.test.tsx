import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import DetailsEditPage from '../../../../src/ui/frontend/src/components/DetailsEditPage'

describe('DetailsEditPage', () => {
  const sections = [
    {
      label: 'Profile',
      fields: [{ key: 'name', label: 'Name', type: 'text' as const }],
    },
  ]

  it('saves edited values and resets on cancel', async () => {
    const user = userEvent.setup()
    const onSave = vi.fn()
    const onCancel = vi.fn()

    render(
      <DetailsEditPage
        title="Edit details"
        sections={sections}
        data={{ name: 'Ada' }}
        onSave={onSave}
        onCancel={onCancel}
      />,
    )

    const input = screen.getByRole('textbox')
    await user.clear(input)
    await user.type(input, 'Grace')
    await user.click(screen.getByRole('button', { name: 'Save' }))
    expect(onSave).toHaveBeenCalledWith({ name: 'Grace' })

    await user.clear(input)
    await user.type(input, 'Changed')
    await user.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(onCancel).toHaveBeenCalled()
    expect(input).toHaveValue('Ada')
  })

  it('renders without optional callbacks', async () => {
    const user = userEvent.setup()
    render(
      <DetailsEditPage title="Read only" sections={sections} data={{ name: 'Ada' }} />,
    )

    await user.click(screen.getByRole('button', { name: 'Save' }))
    await user.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.getByRole('heading', { name: 'Read only', level: 1 })).toBeTruthy()
  })
})

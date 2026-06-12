import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ConfidenceBullets } from '../../../../src/ui/frontend/src/components/ConfidenceBullets'

describe('ConfidenceBullets', () => {
  it('renders five bullets with the floored confidence count active', () => {
    const { container } = render(<ConfidenceBullets confidence={3.9} />)
    const on = container.querySelectorAll('.confidence-bullet--on')
    expect(on).toHaveLength(3)
    expect(container.querySelectorAll('.confidence-bullet')).toHaveLength(5)
  })

  it('falls back to zero active bullets for invalid confidence values', () => {
    const { container, rerender } = render(<ConfidenceBullets />)
    expect(container.querySelectorAll('.confidence-bullet--on')).toHaveLength(0)

    rerender(<ConfidenceBullets confidence={-1} />)
    expect(container.querySelectorAll('.confidence-bullet--on')).toHaveLength(0)

    rerender(<ConfidenceBullets confidence={6} />)
    expect(container.querySelectorAll('.confidence-bullet--on')).toHaveLength(0)

    rerender(<ConfidenceBullets confidence={'3' as unknown as number} />)
    expect(container.querySelectorAll('.confidence-bullet--on')).toHaveLength(0)
  })
})

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { GradeMark } from '../../../../src/ui/frontend/src/components/GradeMark'

// Literal geometry from the AST-2101 brief (§ Geometry, 0 0 100 100 viewBox) — pinned here, not imported,
// so a drifted product map fails instead of agreeing with itself.
const BRIEF_PATHS: Record<string, string> = {
  A: 'M50 6a44 44 0 1 0 0.01 0Z', // circle
  B: 'M50 3L97 50L50 97L3 50Z', // diamond
  C: 'M18 9H82Q91 9 91 18V82Q91 91 82 91H18Q9 91 9 82V18Q9 9 18 9Z', // rounded square
  D: 'M50 6L96 90H4Z', // up triangle
  F: 'M4 10H96L50 94Z', // down triangle
  X: 'M20 20L80 80M80 20L20 80', // cross
}

// Every grade × both layouts: the AC 6 / AC 7 grid.
const CASES = Object.keys(BRIEF_PATHS).flatMap(grade => [
  { grade, letterless: false },
  { grade, letterless: true },
])

describe('GradeMark — AST-2128', () => {
  it.each(CASES)('$grade (letterless=$letterless): img role named by the grade, aria-hidden SVG with the brief path (AC6)', ({ grade, letterless }) => {
    render(<GradeMark grade={grade} letterless={letterless} />)
    const mark = screen.getByRole('img', { name: grade })
    const svg = mark.querySelector('svg')!
    expect(svg).not.toBeNull()
    expect(svg.getAttribute('aria-hidden')).toBe('true')
    expect(svg.getAttribute('viewBox')).toBe('0 0 100 100')
    // jsdom ignores the display presentation attribute, so pin the attribute itself (AST-2129 CSS overrides it).
    expect(svg.getAttribute('display')).toBe('none')
    expect(svg.querySelectorAll('path')).toHaveLength(1)
    expect(svg.querySelector('path')!.getAttribute('d')).toBe(BRIEF_PATHS[grade])
  })

  it.each(CASES)('$grade (letterless=$letterless): textContent is the single letter, or empty when letterless (AC7)', ({ grade, letterless }) => {
    render(<GradeMark grade={grade} letterless={letterless} />)
    expect(screen.getByRole('img', { name: grade }).textContent).toBe(letterless ? '' : grade)
  })

  it.each(CASES)('$grade (letterless=$letterless): keeps the grade-dot classes call sites and App.css select on', ({ grade, letterless }) => {
    render(<GradeMark grade={grade} letterless={letterless} />)
    const mark = screen.getByRole('img', { name: grade })
    expect(mark.tagName).toBe('SPAN')
    expect(mark).toHaveClass('grade-dot', `dot-${grade.toLowerCase()}`)
    if (letterless) expect(mark).toHaveClass('grade-dot-letterless')
    else expect(mark).not.toHaveClass('grade-dot-letterless')
  })

  it('tooltip becomes the title; empty or missing tooltip leaves no title, and the name stays the grade', () => {
    const { rerender } = render(<GradeMark grade="B" tooltip="Strong fit" />)
    const mark = screen.getByRole('img', { name: 'B' })
    expect(mark).toHaveAttribute('title', 'Strong fit')
    rerender(<GradeMark grade="B" tooltip="" />)
    expect(screen.getByRole('img', { name: 'B' })).not.toHaveAttribute('title')
    rerender(<GradeMark grade="B" />)
    expect(screen.getByRole('img', { name: 'B' })).not.toHaveAttribute('title')
  })

  it('lowercase grade: shape lookup is case-insensitive, while class, text and name keep the grade as passed', () => {
    render(<GradeMark grade="c" />)
    const mark = screen.getByRole('img', { name: 'c' })
    expect(mark).toHaveClass('dot-c')
    expect(mark.textContent).toBe('c')
    expect(mark.querySelector('path')!.getAttribute('d')).toBe(BRIEF_PATHS.C)
  })

  it('unknown grade: still renders the mark (name + letter), with no SVG and no crash', () => {
    render(<GradeMark grade="Q" />)
    const mark = screen.getByRole('img', { name: 'Q' })
    expect(mark).toHaveClass('grade-dot', 'dot-q')
    expect(mark.querySelector('svg')).toBeNull()
    expect(mark.textContent).toBe('Q')
  })
})

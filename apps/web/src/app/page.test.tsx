import { describe, expect, it } from 'vitest'
import {
  convertToCSV,
  formatDuration,
  formatPhoneNumber,
  maskPhoneNumber,
  parseCSV,
  truncate,
} from '../lib/utils'

describe('shared web utilities', () => {
  it('formats durations across seconds, minutes, and hours', () => {
    expect(formatDuration(45)).toBe('45s')
    expect(formatDuration(125)).toBe('2m 5s')
    expect(formatDuration(3665)).toBe('1h 1m')
  })

  it('formats and masks supported phone numbers', () => {
    expect(formatPhoneNumber('+919876543210')).toBe('+91 98765 43210')
    expect(formatPhoneNumber('+14155552671')).toBe('+1 (415) 555-2671')
    expect(maskPhoneNumber('+919876543210')).toBe('*********3210')
  })

  it('truncates long text without changing short text', () => {
    expect(truncate('Voice AI', 20)).toBe('Voice AI')
    expect(truncate('Voice AI platform', 8)).toBe('Voice AI...')
  })

  it('converts simple CSV data in both directions', () => {
    const rows = [{ name: 'Karn', role: 'Developer' }, { name: 'Asha', role: 'Analyst' }]
    const csv = convertToCSV(rows)
    expect(parseCSV(csv)).toEqual(rows)
  })
})

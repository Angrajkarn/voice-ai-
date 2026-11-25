import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import DashboardPage from './(dashboard)/dashboard/page'

describe('Dashboard Page', () => {
  it('renders without crashing', () => {
    render(<DashboardPage />)
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})
import { render, screen } from './test-utils'
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
  })

  it('displays the app heading', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /nuevo hive/i })).toBeInTheDocument()
  })
})

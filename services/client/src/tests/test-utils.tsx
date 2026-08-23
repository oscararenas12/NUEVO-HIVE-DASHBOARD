import type { ReactElement } from 'react'
import { render, type RenderOptions } from '@testing-library/react'
import { MemoryRouter, type MemoryRouterProps } from 'react-router-dom'

type CustomRenderOptions = Omit<RenderOptions, 'wrapper'> & {
  routerProps?: MemoryRouterProps
}

function customRender(ui: ReactElement, options?: CustomRenderOptions) {
  const { routerProps, ...renderOptions } = options ?? {}

  function Wrapper({ children }: { children: React.ReactNode }) {
    return <MemoryRouter {...routerProps}>{children}</MemoryRouter>
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

export { customRender as render }
export { screen, waitFor, within } from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'

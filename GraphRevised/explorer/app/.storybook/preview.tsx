import type { Decorator, Preview } from '@storybook/react-vite'
import { useEffect, type ReactNode } from 'react'
import '../src/styles/tokens.css'
import '../src/styles/base.css'

// The theme follows the toolbar: system (the device), light, or dark (D-122).
function ThemeFrame({ theme, children }: { theme: string; children: ReactNode }) {
  useEffect(() => {
    if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme
    else delete document.documentElement.dataset.theme
  }, [theme])
  return <div style={{ background: 'var(--bg)', color: 'var(--ink)', padding: 16, minHeight: '100vh' }}>{children}</div>
}

const withTheme: Decorator = (Story, context) => (
  <ThemeFrame theme={context.globals.theme as string}><Story /></ThemeFrame>
)

const preview: Preview = {
  globalTypes: {
    theme: {
      description: 'Theme',
      toolbar: { title: 'Theme', icon: 'mirror', items: ['system', 'light', 'dark'], dynamicTitle: true },
    },
    persona: {
      description: 'Who is exploring',
      toolbar: { title: 'Persona', icon: 'user', items: ['scholar', 'student', 'browser'], dynamicTitle: true },
    },
  },
  initialGlobals: { theme: 'light', persona: 'scholar' },
  decorators: [withTheme],
  parameters: {
    layout: 'fullscreen',
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
    a11y: {
      // 'todo' - show a11y violations in the test UI only
      test: 'todo'
    }
  },
};

export default preview;

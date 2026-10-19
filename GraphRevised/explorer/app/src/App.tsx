// The explorer's screen is assembled here once its parts exist; until then they live in Storybook.
export default function App() {
  return (
    <main style={{ padding: 16 }}>
      <h1 style={{ fontSize: 'var(--fs-title)' }}>Chrystallum Explorer</h1>
      <p className="muted">The parts are being built one at a time: run <code>npm run storybook</code> to see them.</p>
    </main>
  )
}

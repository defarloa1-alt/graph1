# Chrystallum Explorer (app)

The React app for the explorer (D-101): Vite, React, TypeScript, plain CSS variables, Cytoscape.js
for the graph. The screen it builds toward is [26](../../26-UI-DATA-CONTRACT.md) §1 and wireframe v8
(`../wireframes/`); decisions D-101 to D-131 in [33](../../33-DECISIONS.md).

Built one part at a time, each reviewed in Storybook with its states (light and dark, persona):

```bash
npm install
npm run storybook   # the parts, http://localhost:6006
npm run dev         # the app
```

- `src/styles/tokens.css`: the design tokens, the same values as the Figma Color and Size variables.
- `src/icons/`: kind and lens icons, one markup for the React icon and the canvas picture.
- `src/components/`: the parts; `src/stories/`: foundations and proposals (not adopted until decided).
- `src/words.ts`: every word shown for a stored value, in one place.

Data is not in git: graph snapshots go in `public/data/` (git-ignored).

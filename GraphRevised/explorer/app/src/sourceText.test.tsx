import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import { SourceText } from './SourceText'

describe('source text', () => {
  it('separates quotation and passage with attribution and a source link', () => {
    const html = renderToStaticMarkup(<SourceText evidence source={{ passage: 'Reference', locator: 'https://example.org/',
      quotation: 'Supporting words', passageText: 'Complete passage', editionCitation: 'Edition', rights: 'Open',
      textAvailability: 'available' }} />)
    expect(html).toContain('Supporting quotation:')
    expect(html).toContain('Supporting words')
    expect(html).toContain('Read preserved source passage')
    expect(html).toContain('Complete passage')
    expect(html).toContain('Edition: ')
    expect(html).toContain('Rights: ')
    expect(html).toContain('https://example.org/')
  })
  it('distinguishes unavailable, withheld, and older snapshots', () => {
    const make = (textAvailability?: string) => renderToStaticMarkup(<SourceText evidence source={{
      passage: null, locator: null, textAvailability }} />)
    expect(make('not-recorded')).toContain('No preserved passage text recorded')
    expect(make('rights-unconfirmed')).toContain('reuse rights are not confirmed')
    expect(make()).toContain('older snapshot')
  })
})

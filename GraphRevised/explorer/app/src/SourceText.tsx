import { safeLocator } from './subjectView'

export interface SourceTextData {
  passage: string | null
  locator: string | null
  quotation?: string | null
  passageText?: string | null
  editionCitation?: string | null
  rights?: string | null
  textAvailability?: string
}

export function SourceText({ source, evidence }: { source: SourceTextData; evidence: boolean }) {
  const link = safeLocator(source.locator)
  return <div className="source-text">
    <div><strong>{source.passage || 'Source reference unavailable'}</strong></div>
    {source.editionCitation && <div>Edition: {source.editionCitation}</div>}
    {source.rights && <div>Rights: {source.rights}</div>}
    {source.locator && <div>{link ? <a href={link} target="_blank" rel="noreferrer">Open source locator</a> : <>Locator: {source.locator}</>}</div>}
    {source.textAvailability === undefined ? <p>Source text is not included in this older snapshot. Generate a new snapshot to check availability.</p>
      : source.textAvailability === 'rights-unconfirmed' ? <p>Source text is not included because reuse rights are not confirmed. Consult the source locator.</p>
      : <>
        {evidence && (source.quotation ? <><div>Supporting quotation:</div><blockquote>{source.quotation}</blockquote></>
          : <p>No supporting quotation recorded for this evidence.</p>)}
        {source.passageText ? <details><summary>Read preserved source passage</summary><p className="preserved-passage">{source.passageText}</p></details>
          : <p>No preserved passage text recorded for this source.</p>}
      </>}
  </div>
}

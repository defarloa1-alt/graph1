"""Freeze each wireframe screen into a static HTML page, for importing into Figma.

    python GraphRevised/explorer/wireframes/freeze_screens.py GraphRevised/exports/wireframe.html <out-dir>

Figma's HTML import (the Figma MCP's html_to_figma) runs no scripts and lays the
page out again at its own width. So each screen is opened in Edge (Playwright,
channel "msedge"), shown with showScreen(k), and frozen: canvases become images,
every box keeps its drawn size, grid children are pinned where they were drawn,
hidden elements and the narrow-screen and dark rules are dropped, placeholders
become grey text. Writes screen0.html ... screen9.html and a screenshot of each.
Needs `pip install playwright`; uses the installed Edge, so no browser download.
"""
import sys, pathlib
from playwright.sync_api import sync_playwright
src = pathlib.Path(sys.argv[1]).resolve(); out = pathlib.Path(sys.argv[2])
FREEZE = """() => {
  document.querySelectorAll('canvas').forEach(c => {
    let url = ''; try { url = c.toDataURL('image/png'); } catch (e) {}
    const img = document.createElement('img');
    img.src = url; img.style.cssText = c.style.cssText;
    const r = c.getBoundingClientRect();
    if (!c.style.width) { img.style.width = r.width + 'px'; img.style.height = r.height + 'px'; }
    img.className = c.className; c.replaceWith(img);
  });
  const W = innerWidth, H = innerHeight;
  const all = [...document.body.querySelectorAll('*')];
  const gone = all.filter(el => { if (el.closest('select')) return false; const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    return cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0 ||
           r.right <= 0 || r.bottom <= 0 || r.left >= W || r.top >= H; });
  const boxes = all.filter(el => !gone.includes(el)).map(el => [el, el.getBoundingClientRect(), getComputedStyle(el).display]);
  const rects = new Map(boxes.map(([el, r]) => [el, r]));
  const styles = new Map(boxes.map(([el]) => { const cs = getComputedStyle(el);
    return [el, { display: cs.display, position: cs.position, borderLeftWidth: cs.borderLeftWidth, borderTopWidth: cs.borderTopWidth }]; }));
  for (const [el, r, d] of boxes) {
    if (d === 'inline' || d === 'contents' || el.closest('svg') && el.tagName !== 'svg' || el.closest('select') && el.tagName !== 'SELECT') continue;
    el.style.boxSizing = 'border-box'; el.style.width = r.width + 'px'; el.style.height = r.height + 'px';
    el.style.flexShrink = '0'; el.style.flexGrow = '0'; el.style.flexBasis = 'auto'; el.style.maxWidth = 'none'; el.style.minWidth = '0';
  }
  const grids = new Set();
  // grid placement does not survive the conversion: pin grid children where they were drawn
  for (const [el, r] of boxes) {
    const parent = el.parentElement;
    if (!parent || gone.includes(el) || !styles.has(parent) || styles.get(parent).display.indexOf('grid') < 0) continue;
    const pr = rects.get(parent) || parent.getBoundingClientRect(), pcs = styles.get(parent) || getComputedStyle(parent);
    if (pcs.position === 'static') parent.style.position = 'relative';
    grids.add(parent);
    el.style.position = 'absolute';
    el.style.left = (r.left - pr.left - parseFloat(pcs.borderLeftWidth)) + 'px';
    el.style.top = (r.top - pr.top - parseFloat(pcs.borderTopWidth)) + 'px';
    el.style.margin = '0'; el.style.right = 'auto'; el.style.bottom = 'auto';
  }
  grids.forEach(g => { g.style.display = 'block'; });
  gone.forEach(el => el.remove());
  for (const el of [document.documentElement, document.body]) { el.style.width = W + 'px'; el.style.height = H + 'px'; el.style.overflow = 'hidden'; }
  // the converter renders at its own width: keep only the desktop rules
  for (const style of document.querySelectorAll('style')) {
    const sheet = style.sheet; if (!sheet) continue;
    for (let i = sheet.cssRules.length - 1; i >= 0; i--) {
      const rule = sheet.cssRules[i];
      if (rule instanceof CSSMediaRule && /max-width|prefers-color-scheme: dark/.test(rule.conditionText)) sheet.deleteRule(i);
    }
    style.textContent = [...sheet.cssRules].map(r => r.cssText).join(String.fromCharCode(10));
  }
  document.querySelectorAll('script').forEach(s => s.remove());
  document.querySelectorAll('select').forEach(sel => [...sel.options].forEach(o => o.toggleAttribute('selected', o.selected)));
  document.querySelectorAll('input, textarea').forEach(i => {
    if (!i.value && i.placeholder) { i.setAttribute('value', i.placeholder); i.style.color = getComputedStyle(i, '::placeholder').color; }
    else i.setAttribute('value', i.value);
  });
  return '<!doctype html>' + document.documentElement.outerHTML;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    for k in range(10):
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.on("pageerror", lambda e: print("pageerror:", str(e)[:300]))
        pg.goto(src.as_uri()); pg.wait_for_timeout(2500)
        pg.evaluate(f"showScreen({k})"); pg.wait_for_timeout(2500)
        title = pg.evaluate(f"(document.querySelector('[data-screen=\"{k}\"]')||{{}}).textContent || ''")
        pg.screenshot(path=str(out / f"screen{k}.png"))
        html = pg.evaluate(FREEZE)
        (out / f"screen{k}.html").write_text(html, encoding="utf-8")
        print(k, repr(title.strip()[:40]), len(html) // 1024, "KB")
        pg.close()
    b.close()

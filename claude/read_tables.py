import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import docx
doc = docx.Document('SFA_INDEX_READER_Spec_v1.docx')

print('=== TABLES ===')
for i, table in enumerate(doc.tables):
    print(f'--- Table {i+1} ---')
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        seen = []
        for c in cells:
            different = len(seen) == 0 or c != seen[-1]
            if different:
                seen.append(c)
        if any(seen):
            print('  | ' + ' | '.join(seen))
    print()

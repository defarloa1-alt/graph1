import zipfile
z = zipfile.ZipFile('md/Architecture/bloom-export.zip', 'r')
nodes = z.read('node-export.csv').decode('utf-8', errors='replace')
nlines = [x for x in nodes.split('\n') if x.strip()]
print('Node rows:', len(nlines)-1)
labels = set()
for line in nlines[1:]:
    if '","' in line:
        idx = line.index('","')
        lbl = line[idx+2:].split('"')[0]
        labels.add(lbl)
print('Labels:', sorted(labels))

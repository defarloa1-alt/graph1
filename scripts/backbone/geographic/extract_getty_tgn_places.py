import csv

# Paths to Getty TGN files (update if needed)
COORDINATES_PATH = '../Geographic/COORDINATES.out'
TERM_PATH = '../Geographic/TERM.out'
OUTPUT_PATH = '../Geographic/getty_tgn_places.csv'

# Step 1: Extract coordinates (TGN_ID, lat, long, [alt])
coords = {}
with open(COORDINATES_PATH, encoding='utf-8', errors='ignore') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 4:
            tgn_id = parts[0]
            lat = parts[1]
            long = parts[2]
            alt = parts[3] if len(parts) > 3 else ''
            coords[tgn_id] = {'lat': lat, 'long': long, 'alt': alt}

# Step 2: Extract names (TGN_ID, name)
names = {}
with open(TERM_PATH, encoding='utf-8', errors='ignore') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            tgn_id = parts[0]
            name = parts[1]
            # Only take the first name for each TGN_ID (preferred)
            if tgn_id not in names:
                names[tgn_id] = name

# Step 3: Write combined output
with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as out:
    writer = csv.writer(out)
    writer.writerow(['tgn_id', 'name', 'lat', 'long', 'alt'])
    for tgn_id, name in names.items():
        lat = coords.get(tgn_id, {}).get('lat', '')
        long = coords.get(tgn_id, {}).get('long', '')
        alt = coords.get(tgn_id, {}).get('alt', '')
        writer.writerow([tgn_id, name, lat, long, alt])

print(f"Extracted {len(names)} Getty TGN places to {OUTPUT_PATH}")

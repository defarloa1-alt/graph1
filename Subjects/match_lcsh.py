import pandas as pd
from pathlib import Path

# Load clean subjects from current directory
clean_file = 'subjects_properties_clean.csv'
if not Path(clean_file).exists():
    print(f"ERROR: {clean_file} not found in current directory")
    exit(1)

print(f"Loading: {clean_file}")
clean_df = pd.read_csv(clean_file)
print(f"Loaded {len(clean_df)} clean subjects\n")

# Find chunks directory in current directory
chunks_dir = Path('chunks')
if not chunks_dir.exists():
    print(f"ERROR: chunks directory not found")
    exit(1)

print(f"Found chunks directory")

# Get all chunk files
chunk_files = sorted(list(chunks_dir.glob('*.csv')))
print(f"Found {len(chunk_files)} chunk files\n")

# Create lookup sets
qids = set(clean_df['qid'].dropna())
labels = set(clean_df['label'].str.lower().dropna()) if 'label' in clean_df.columns else set()
alt_labels = set()
if 'altLabel' in clean_df.columns:
    for alt in clean_df['altLabel'].dropna():
        alt_labels.update([a.strip().lower() for a in str(alt).split('|')])

print(f"Lookup sets:")
print(f"  QIDs: {len(qids)}")
print(f"  Labels: {len(labels)}")
print(f"  Alt Labels: {len(alt_labels)}\n")

# Process chunks
matches = []
total_processed = 0

print("Processing chunks...")
for i, chunk_file in enumerate(chunk_files, 1):
    try:
        chunk_df = pd.read_csv(chunk_file)
        total_processed += len(chunk_df)
        
        # Match by QID
        if 'qid' in chunk_df.columns:
            qid_matches = chunk_df[chunk_df['qid'].isin(qids)].copy()
            if len(qid_matches) > 0:
                qid_matches['match_type'] = 'qid'
                matches.append(qid_matches)
        
        # Match by prefLabel
        if 'prefLabel' in chunk_df.columns:
            label_matches = chunk_df[chunk_df['prefLabel'].str.lower().isin(labels)].copy()
            if len(label_matches) > 0:
                label_matches['match_type'] = 'prefLabel'
                matches.append(label_matches)
        
        # Match by altLabel
        if 'altLabel' in chunk_df.columns:
            alt_match_mask = chunk_df['altLabel'].apply(
                lambda x: any(a.strip().lower() in alt_labels for a in str(x).split('|')) if pd.notna(x) else False
            )
            alt_matches = chunk_df[alt_match_mask].copy()
            if len(alt_matches) > 0:
                alt_matches['match_type'] = 'altLabel'
                matches.append(alt_matches)
        
        if i % 10 == 0:
            print(f"  {i}/{len(chunk_files)} chunks")
    except Exception as e:
        print(f"  ERROR {chunk_file.name}: {e}")

print(f"Total rows processed: {total_processed:,}\n")

# Combine matches
if matches:
    all_matches = pd.concat(matches, ignore_index=True)
    
    if 'uri' in all_matches.columns:
        all_matches = all_matches.sort_values('match_type').drop_duplicates(subset=['uri'], keep='first')
    
    print(f"Total matches: {len(all_matches)}")
    print("\nMatches by type:")
    print(all_matches['match_type'].value_counts())
    
    all_matches.to_csv('lcsh_matched_clean_subjects.csv', index=False)
    print(f"\nSaved: lcsh_matched_clean_subjects.csv")
    
    # Enriched version
    if 'qid' in all_matches.columns and 'uri' in all_matches.columns:
        summary = all_matches.groupby('qid').agg({
            'uri': 'first',
            'prefLabel': 'first',
            'match_type': 'first'
        }).reset_index()
        
        enriched = clean_df.merge(summary, on='qid', how='left', suffixes=('', '_lcsh'))
        enriched['has_lcsh_match'] = enriched['uri'].notna()
        enriched.to_csv('subjects_clean_with_lcsh.csv', index=False)
        
        match_count = enriched['has_lcsh_match'].sum()
        print(f"Saved: subjects_clean_with_lcsh.csv")
        print(f"Match rate: {match_count}/{len(enriched)} ({match_count/len(enriched)*100:.1f}%)")
else:
    print("No matches found")

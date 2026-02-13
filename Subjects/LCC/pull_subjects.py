import pandas as pd
import os

# Check what files exist
print("Files in current directory:")
for f in os.listdir('.'):
    if f.endswith('.csv'):
        print(f"  {f}")

# Try to find the subjects properties file
possible_files = [
    'subjects_properties_enhanced.csv',
    'subjects_properties.csv',
    'subject_properties.csv'
]

input_file = None
for f in possible_files:
    if os.path.exists(f):
        input_file = f
        break

if input_file is None:
    print("\nERROR: Could not find subjects properties file.")
    print("Looking for one of:")
    for f in possible_files:
        print(f"  - {f}")
    exit(1)

print(f"\nUsing input file: {input_file}")

# Load the file
df = pd.read_csv(input_file)
print(f"Loaded {len(df)} rows")
print(f"\nColumns: {', '.join(df.columns)}")

# Define whitelists and blacklists for P31 (instance of)
P31_KEEP = {
    'academic discipline', 'academic major', 'field of study', 'branch of science',
    'interdisciplinary science', 'field of research', 'field of work',
    'class used in Universal Decimal Classification', 'interdisciplinarity',
    'academic field', 'area of study', 'discipline'
}

P31_EXCLUDE = {
    'scientific article', 'scientific journal', 'program', 'academic degree',
    'encyclopedia', 'reference work', 'human', 'city', 'ancient city',
    'ethnic group', 'battle', 'book', 'religious text', 'federation',
    'scholarly article', 'article', 'journal', 'periodical', 'publication',
    'person', 'organization', 'event', 'location', 'geographic location',
    'academic journal', 'interdisciplinary program'
}

# Define whitelists and blacklists for P279 (subclass of)
P279_KEEP = {
    'area studies', 'cultural studies', 'gender studies', 'materials science',
    'military science', 'Earth science', 'social science', 'formal science',
    'interdisciplinary science', 'human geography', 'philology',
    'natural science', 'applied science', 'humanities', 'science',
    'social sciences and humanities', 'botany', 'chemistry'
}

P279_EXCLUDE = {
    'city', 'ancient city', 'ethnic group', 'battle', 'monarch',
    'Roman auxiliary unit', 'person', 'event', 'organization',
    'publication', 'work', 'book', 'journal'
}

def check_p31_status(p31_labels):
    """Check if P31 values indicate this should be kept or excluded"""
    if pd.isna(p31_labels) or p31_labels == '':
        return 'unknown'
    
    labels = [label.strip().lower() for label in str(p31_labels).split('|')]
    
    # Check for exclusions first (hard fail)
    for label in labels:
        if any(excl in label for excl in P31_EXCLUDE):
            return 'exclude'
    
    # Then check for keeps
    for label in labels:
        if any(keep in label for keep in P31_KEEP):
            return 'keep'
    
    return 'unknown'

def check_p279_status(p279_labels):
    """Check if P279 values indicate this should be kept or excluded"""
    if pd.isna(p279_labels) or p279_labels == '':
        return 'unknown'
    
    labels = [label.strip().lower() for label in str(p279_labels).split('|')]
    
    # Check for exclusions first
    for label in labels:
        if any(excl in label for excl in P279_EXCLUDE):
            return 'exclude'
    
    # Then check for keeps
    for label in labels:
        if any(keep in label for keep in P279_KEEP):
            return 'keep'
    
    return 'unknown'

def check_description_exclusions(description):
    """Check if description indicates this is a publication/source"""
    if pd.isna(description):
        return False
    
    desc_lower = str(description).lower()
    exclusion_patterns = [
        'scientific article', 'scholarly article', 'journal', 'encyclopedia',
        'reference work', 'lexicon', 'dictionary', 'program', 'degree'
    ]
    
    return any(pattern in desc_lower for pattern in exclusion_patterns)

# Apply filtering rules
print("\nApplying filters...")
df['P31_status'] = df['P31_labels'].apply(check_p31_status) if 'P31_labels' in df.columns else 'unknown'
df['P279_status'] = df['P279_labels'].apply(check_p279_status) if 'P279_labels' in df.columns else 'unknown'
df['description_excludes'] = df['description'].apply(check_description_exclusions) if 'description' in df.columns else False

# Determine final recommendation
def get_recommendation(row):
    """Combine all signals to make keep/exclude recommendation"""
    
    # Hard excludes
    if row.get('P31_status') == 'exclude':
        return 'EXCLUDE - P31 is publication/entity'
    if row.get('P279_status') == 'exclude':
        return 'EXCLUDE - P279 is concrete entity'
    if row.get('description_excludes'):
        return 'EXCLUDE - description indicates publication'
    
    # Must be concept_subject
    if 'node_type' in row and row['node_type'] != 'concept_subject':
        return 'EXCLUDE - not concept_subject'
    
    # Strong keeps
    if row.get('P31_status') == 'keep' and row.get('subject_type') in ['discipline', 'field of study', 'academic field']:
        return 'KEEP - disciplinary concept'
    
    # Moderate keeps
    if row.get('P279_status') == 'keep' and row.get('subject_type') in ['discipline', 'field of study']:
        return 'KEEP - domain subclass'
    
    # Weak keeps (need review)
    if row.get('subject_type') in ['discipline', 'field of study', 'academic field', 'branch of science']:
        return 'REVIEW - subject_type OK but weak P31/P279'
    
    return 'REVIEW - unclear classification'

df['recommendation'] = df.apply(get_recommendation, axis=1)

# Save enhanced file with filtering columns
output_file = 'subjects_properties_with_filters.csv'
df.to_csv(output_file, index=False)

# Generate summary report
print("\n" + "=" * 60)
print("SUBJECT CLEANING ANALYSIS")
print("=" * 60)
print(f"\nTotal subjects analyzed: {len(df)}")
print(f"\nRecommendations:")
for rec in sorted(df['recommendation'].unique()):
    count = len(df[df['recommendation'] == rec])
    pct = count / len(df) * 100
    print(f"  {rec}: {count} ({pct:.1f}%)")

print(f"\nP31 Status:")
for status in ['keep', 'exclude', 'unknown']:
    count = len(df[df['P31_status'] == status])
    print(f"  {status}: {count}")

print(f"\nP279 Status:")
for status in ['keep', 'exclude', 'unknown']:
    count = len(df[df['P279_status'] == status])
    print(f"  {status}: {count}")

print(f"\n{'=' * 60}")
print(f"Enhanced file saved to: {output_file}")
print(f"{'=' * 60}")

# Create a clean subset (only KEEPs)
clean_df = df[df['recommendation'].str.startswith('KEEP')].copy()
clean_df.to_csv('subjects_properties_clean.csv', index=False)
print(f"\nClean subset ({len(clean_df)} rows) saved to: subjects_properties_clean.csv")

# Create a review subset
review_df = df[df['recommendation'].str.startswith('REVIEW')].copy()
review_df.to_csv('subjects_properties_review.csv', index=False)
print(f"Review subset ({len(review_df)} rows) saved to: subjects_properties_review.csv")
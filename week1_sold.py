import pandas as pd
import glob
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'Outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Find every sold file in the Data folder
files = glob.glob(os.path.join(DATA_DIR, 'CRMLSSold*.csv'))
print(f"Found {len(files)} sold files")

# Read each file and store in a list
frames = []
for f in sorted(files):
    df = pd.read_csv(f, low_memory=False)
    frames.append(df)

# Combine all files into one dataset
combined = pd.concat(frames, ignore_index=True)
print(f"Rows after concatenation: {len(combined)}")

# Keep only Residential properties
before = len(combined)
combined = combined[combined['PropertyType'] == 'Residential']
after = len(combined)
print(f"Rows before Residential filter: {before}")
print(f"Rows after Residential filter: {after}")

# Save the result
out_path = os.path.join(OUTPUT_DIR, 'sold.csv')
combined.to_csv(out_path, index=False)
print(f"Saved to {out_path}")
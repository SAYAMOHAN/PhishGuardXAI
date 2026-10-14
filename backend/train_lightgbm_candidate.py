df = df.dropna(subset=["URL", "Label"]).copy()

df["URL"] = df["URL"].astype(str).str.strip()
df["Label"] = df["Label"].astype(str).str.strip().str.lower()

# Remove empty URLs and keep valid labels.
df = df[
    df["URL"].ne("") &
    df["Label"].isin(["good", "bad"])
].copy()

# Identify URLs assigned conflicting labels.
label_counts = df.groupby("URL")["Label"].nunique()
conflicting_urls = label_counts[label_counts > 1].index

print("Conflicting URLs excluded:", len(conflicting_urls))

# Exclude conflicting URLs rather than arbitrarily choosing a label.
df = df[~df["URL"].isin(conflicting_urls)].copy()

# Remove remaining duplicate URLs.
df = df.drop_duplicates(subset=["URL"]).copy()

if df.empty:
    raise ValueError("No valid labelled URLs remain in the dataset.")

if df["Label"].nunique() != 2:
    raise ValueError(
        "The cleaned dataset must contain both 'good' and 'bad' labels."
    )

print("Unique URLs:", len(df))
print("\nLabel counts:")
print(df["Label"].value_counts().to_string())

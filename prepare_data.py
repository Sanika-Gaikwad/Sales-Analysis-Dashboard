import pandas as pd

# 1. Load original retail dataset
df = pd.read_csv("retail_sales_raw.csv")

# 2. Display original number of rows
print("Original rows:", len(df))

# 3. Create 10 duplicate records
duplicate_rows = df.head(10).copy()

# 4. Add duplicate records to dataset
df = pd.concat([df, duplicate_rows], ignore_index=True)

# 5. Display final number of rows
print("Final raw rows:", len(df))

# 6. Save the 10,005-row raw dataset
df.to_csv("retail_sales_raw_10000.csv", index=False)

# 7. Success message
print("Raw dataset created successfully!")
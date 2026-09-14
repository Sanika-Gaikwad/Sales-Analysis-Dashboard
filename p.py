import pandas as pd

# ==========================================
# 1. LOAD RAW DATA
# ==========================================

df = pd.read_csv("retail-orders-raw.csv")

print("===== RAW DATA =====")
print(df.head())
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())


# ==========================================
# 2. DATA QUALITY PROFILE
# ==========================================

print("\n==========================================")
print("       DATA QUALITY PROFILE")
print("==========================================")


# ---------- COMPLETENESS ----------
print("\n--- 1. COMPLETENESS ---")

missing_values = df.isnull().sum()
missing_percent = (df.isnull().mean() * 100).round(2)

completeness = pd.DataFrame({
    "Missing Values": missing_values,
    "Missing %": missing_percent
})

print(completeness)


# ---------- UNIQUENESS ----------
print("\n--- 2. UNIQUENESS ---")

duplicate_rows = df.duplicated().sum()
duplicate_order_ids = df["order_id"].duplicated().sum()

print("Duplicate rows:", duplicate_rows)
print("Duplicate order IDs:", duplicate_order_ids)


# ---------- VALIDITY ----------
print("\n--- 3. VALIDITY ---")

# Convert columns temporarily to numeric for checking
quantity_numeric = pd.to_numeric(df["quantity"], errors="coerce")
unit_price_numeric = pd.to_numeric(df["unit_price"], errors="coerce")
discount_numeric = pd.to_numeric(df["discount_pct"], errors="coerce")

invalid_quantity = (
    quantity_numeric.isna() |
    (quantity_numeric <= 0)
).sum()

invalid_unit_price = (
    unit_price_numeric.isna() |
    (unit_price_numeric <= 0)
).sum()

invalid_discount = (
    discount_numeric.isna() |
    (discount_numeric < 0) |
    (discount_numeric > 100)
).sum()

print("Invalid quantity:", invalid_quantity)
print("Invalid unit price:", invalid_unit_price)
print("Invalid discount:", invalid_discount)


# ---------- CONSISTENCY ----------
print("\n--- 4. CONSISTENCY ---")

allowed_segments = [
    "Student",
    "Fresher",
    "Professional"
]

allowed_payment_status = [
    "Paid",
    "Pending",
    "Failed",
    "Refunded"
]

customer_segment_check = df["customer_segment"].astype(str).str.title()

payment_status_check = df["payment_status"].astype(str).str.title()

invalid_segments = (
    ~customer_segment_check.isin(allowed_segments)
).sum()

invalid_payment_status = (
    ~payment_status_check.isin(allowed_payment_status)
).sum()

print("Invalid customer segments:", invalid_segments)
print("Invalid payment statuses:", invalid_payment_status)


# ---------- FRESHNESS ----------
print("\n--- 5. FRESHNESS ---")

profile_dates = pd.to_datetime(
    df["order_date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print("Latest valid order date:", profile_dates.max())
print("Oldest valid order date:", profile_dates.min())


# ==========================================
# 3. DATA CLEANING
# ==========================================

print("\n==========================================")
print("          DATA CLEANING")
print("==========================================")


# Remove duplicate rows
df = df.drop_duplicates()


# Standardize customer segment
df["customer_segment"] = df["customer_segment"].str.title()


# Standardize payment status
df["payment_status"] = df["payment_status"].str.title()


# Convert order date
df["order_date"] = pd.to_datetime(
    df["order_date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)


# Convert numeric columns
df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)

df["unit_price"] = pd.to_numeric(
    df["unit_price"],
    errors="coerce"
)

df["discount_pct"] = pd.to_numeric(
    df["discount_pct"],
    errors="coerce"
)


# Missing discount = 0
df["discount_pct"] = df["discount_pct"].fillna(0)


# Remove invalid quantity
df = df[df["quantity"] > 0]


# Remove invalid unit price
df = df[df["unit_price"] > 0]


# Remove invalid discount
df = df[
    (df["discount_pct"] >= 0) &
    (df["discount_pct"] <= 100)
]


# ==========================================
# 4. CALCULATE SALES
# ==========================================

df["gross_sales"] = (
    df["quantity"] * df["unit_price"]
)

df["discount_amount"] = (
    df["gross_sales"] * df["discount_pct"] / 100
)

df["net_sales"] = (
    df["gross_sales"] - df["discount_amount"]
)


# ==========================================
# 5. BUSINESS KPIs
# ==========================================

total_orders = df["order_id"].nunique()

total_quantity = df["quantity"].sum()

total_revenue = df["net_sales"].sum()

average_order_value = (
    total_revenue / total_orders
)


print("\n==========================================")
print("              BUSINESS KPIs")
print("==========================================")

print("Total Orders:", total_orders)
print("Total Quantity:", total_quantity)
print("Total Revenue:", round(total_revenue, 2))
print("Average Order Value:", round(average_order_value, 2))


# ==========================================
# 6. PAYMENT STATUS ANALYSIS
# ==========================================

payment_summary = df.groupby("payment_status").agg(
    orders=("order_id", "nunique"),
    revenue=("net_sales", "sum")
).sort_values(
    "orders",
    ascending=False
)

print("\n--- Payment Status Analysis ---")
print(payment_summary)


# ==========================================
# 7. CUSTOMER SEGMENT ANALYSIS
# ==========================================

segment_revenue = df.groupby("customer_segment").agg(
    orders=("order_id", "nunique"),
    revenue=("net_sales", "sum")
).sort_values(
    "revenue",
    ascending=False
)

print("\n--- Customer Segment-wise Revenue ---")
print(segment_revenue)


# ==========================================
# 8. EXPORT CLEANED DATA
# ==========================================

df.to_excel(
    "retail_orders_cleaned.xlsx",
    index=False
)

print("\nCleaned data exported successfully!")
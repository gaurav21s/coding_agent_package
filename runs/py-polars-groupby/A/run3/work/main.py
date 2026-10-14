import polars as pl

def categorize_size(amount: float) -> str:
    """Custom function to categorize sales amount."""
    return "big" if amount > 100 else "small"

def main():
    # 1. Build the DataFrame
    data = {
        "region": ["North", "South", "North", "East", "South", "West"],
        "product": ["A", "B", "C", "A", "B", "C"],
        "amount": [150.0, 80.0, 120.0, 200.0, 50.0, 95.0]
    }
    df = pl.DataFrame(data)

    # 2. Compute total and mean amount per region, sorted by region
    region_stats = (
        df.group_by("region")
        .agg([
            pl.col("amount").sum().alias("total_amount"),
            pl.col("amount").mean().alias("mean_amount")
        ])
        .sort("region")
    )

    print("--- Aggregated Stats per Region ---")
    print(region_stats)
    print("\n")

    # 3. Add 'size' column using the custom function
    # We use map_elements with return_dtype to ensure type safety
    df_with_size = df.with_columns(
        pl.col("amount")
        .map_elements(categorize_size, return_dtype=pl.String)
        .alias("size")
    )

    print("--- Original DataFrame with 'size' column ---")
    print(df_with_size)

if __name__ == "__main__":
    main()

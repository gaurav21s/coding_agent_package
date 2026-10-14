import polars as pl

def categorize_amount(amount: float) -> str:
    """Custom function to categorize sales amount."""
    return "big" if amount > 100 else "small"

def main():
                            
    data = {
        "region": ["North", "South", "North", "East", "South", "West"],
        "product": ["A", "B", "C", "A", "B", "C"],
        "amount": [50.0, 150.0, 200.0, 80.0, 30.0, 120.0]
    }
    df = pl.DataFrame(data)
    
    print("Original DataFrame:")
    print(df)
    print("-" * 30)

                                                                   
    region_stats = (
        df.group_by("region")
        .agg([
            pl.col("amount").sum().alias("total_amount"),
            pl.col("amount").mean().alias("mean_amount")
        ])
        .sort("region")
    )

    print("Stats per region (sorted):")
    print(region_stats)
    print("-" * 30)

                                                         
                                                                    
    df_with_size = df.with_columns(
        pl.col("amount")
        .map_elements(categorize_amount, return_dtype=pl.String)
        .alias("size")
    )

    print("DataFrame with 'size' column:")
    print(df_with_size)

if __name__ == "__main__":
    main()

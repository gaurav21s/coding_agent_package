To accomplish this task using the latest version of `pandas` (3.0.6 as of October 2026), we will initialize an empty DataFrame with the specified columns and then iteratively append rows using `pd.concat`. 

Note: In modern pandas, `DataFrame.append` is deprecated and has been removed. The recommended approach for adding rows one at a time is to collect them in a list and create the DataFrame once, or to use `pd.concat` if iterative building is strictly required. The following solution demonstrates the iterative approach using `pd.concat`.

```python
import pandas as pd

def main():
    # Initialize an empty DataFrame with the specified columns
    df = pd.DataFrame(columns=['name', 'score'])

    # Data to be added
    data_rows = [
        {'name': 'Alice', 'score': 85},
        {'name': 'Bob', 'score': 92},
        {'name': 'Charlie', 'score': 78}
    ]

    # Add rows one at a time in a loop
    for row in data_rows:
        # Create a single-row DataFrame
        new_row = pd.DataFrame([row])
        # Concatenate the existing DataFrame with the new row
        df = pd.concat([df, new_row], ignore_index=True)

    # Print the final DataFrame
    print("Final DataFrame:")
    print(df)
    print("-" * 20)

    # Calculate and print the mean score
    # Ensure the score column is numeric
    mean_score = df['score'].mean()
    print(f"Mean Score: {mean_score}")

if __name__ == "__main__":
    main()
```
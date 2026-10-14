To accomplish this task using the latest version of `pandas` (3.0.6), we will initialize an empty DataFrame with the specified columns and then iteratively append rows using `pd.concat`. While `append` was a common method in older versions of pandas, it has been removed in favor of `pd.concat` for better performance and clarity.

Here is the complete program:

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
        # Create a single-row DataFrame from the dict
        new_row = pd.DataFrame([row])
        # Use pd.concat to add the new row to the existing DataFrame
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
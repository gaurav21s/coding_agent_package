To accomplish this task using the latest version of `pandas` (3.0.6), we initialize an empty DataFrame with the specified columns. Since appending rows to a DataFrame in a loop is generally discouraged due to performance overhead (as it creates a new object each time), the idiomatic and efficient approach is to collect the data in a list of dictionaries and create the DataFrame once, or use `pd.concat` if incremental updates are strictly required.

The following program demonstrates the recommended approach: collecting the data in a list and then initializing the DataFrame.

```python
import pandas as pd

def main():
    # Define the columns
    columns = ['name', 'score']
    
    # Data to be added
    new_rows = [
        {'name': 'Alice', 'score': 85},
        {'name': 'Bob', 'score': 92},
        {'name': 'Charlie', 'score': 78}
    ]
    
    # Initialize an empty list to collect rows
    data_list = []
    
    # Loop to simulate receiving rows one at a time
    for row in new_rows:
        # In a real scenario, you might perform validation here
        data_list.append(row)
        
    # Create the DataFrame from the collected list
    df = pd.DataFrame(data_list, columns=columns)
    
    # Print the final DataFrame
    print("Final DataFrame:")
    print(df)
    print("-" * 20)
    
    # Calculate and print the mean score
    mean_score = df['score'].mean()
    print(f"Mean score: {mean_score:.2f}")

if __name__ == "__main__":
    main()
```
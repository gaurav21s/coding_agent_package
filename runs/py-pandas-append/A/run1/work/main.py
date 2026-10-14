import pandas as pd

def main():
    # Initialize an empty DataFrame with the specified columns
    df = pd.DataFrame(columns=['name', 'score'])

    # Data to be added
    new_rows = [
        {'name': 'Alice', 'score': 85},
        {'name': 'Bob', 'score': 92},
        {'name': 'Charlie', 'score': 78}
    ]

    # Adding rows one at a time in a loop
    for row in new_rows:
        # pd.concat is the modern, non-deprecated way to add rows
        # We create a single-row DataFrame from the dict
        new_df = pd.DataFrame([row])
        df = pd.concat([df, new_df], ignore_index=True)

    # Ensure the score column is numeric for calculation
    df['score'] = pd.to_numeric(df['score'])

    # Print the final DataFrame
    print("Final DataFrame:")
    print(df)
    print("-" * 20)

    # Calculate and print the mean score
    mean_score = df['score'].mean()
    print(f"Mean Score: {mean_score}")

if __name__ == "__main__":
    main()

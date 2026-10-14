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

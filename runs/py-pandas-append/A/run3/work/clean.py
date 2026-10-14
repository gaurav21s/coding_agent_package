import pandas as pd

def main():
                                                              
    df = pd.DataFrame(columns=['name', 'score'])

                      
    new_rows = [
        {'name': 'Alice', 'score': 85},
        {'name': 'Bob', 'score': 92},
        {'name': 'Charlie', 'score': 78}
    ]

                                         
    for row in new_rows:
                                                                 
                                                        
        new_df = pd.DataFrame([row])
        df = pd.concat([df, new_df], ignore_index=True)

                                                        
    df['score'] = pd.to_numeric(df['score'])

                               
    print("Final DataFrame:")
    print(df)
    print("-" * 20)

                                        
    mean_score = df['score'].mean()
    print(f"Mean Score: {mean_score}")

if __name__ == "__main__":
    main()

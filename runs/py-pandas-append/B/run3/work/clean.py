import pandas as pd

def main():
                                                              
    df = pd.DataFrame(columns=['name', 'score'])

                      
    data_rows = [
        {'name': 'Alice', 'score': 85},
        {'name': 'Bob', 'score': 92},
        {'name': 'Charlie', 'score': 78}
    ]

                                      
    for row in data_rows:
                                       
        new_row = pd.DataFrame([row])
                                                             
        df = pd.concat([df, new_row], ignore_index=True)

                               
    print("Final DataFrame:")
    print(df)
    print("-" * 20)

                                        
                                        
    mean_score = df['score'].mean()
    print(f"Mean Score: {mean_score}")

if __name__ == "__main__":
    main()

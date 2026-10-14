import pandas as pd

def main():
                        
    columns = ['name', 'score']
    
                      
    new_rows = [
        {'name': 'Alice', 'score': 85},
        {'name': 'Bob', 'score': 92},
        {'name': 'Charlie', 'score': 78}
    ]
    
                                              
    data_list = []
    
                                                   
    for row in new_rows:
                                                               
        data_list.append(row)
        
                                                  
    df = pd.DataFrame(data_list, columns=columns)
    
                               
    print("Final DataFrame:")
    print(df)
    print("-" * 20)
    
                                        
    mean_score = df['score'].mean()
    print(f"Mean score: {mean_score:.2f}")

if __name__ == "__main__":
    main()

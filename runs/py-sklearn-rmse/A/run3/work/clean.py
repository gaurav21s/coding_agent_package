import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

def main():
                                            
    X, y = make_regression(
        n_samples=200, 
        n_features=3, 
        noise=10, 
        random_state=0
    )

                             
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=0
    )

                             
    model = LinearRegression()
    model.fit(X_train, y_train)

                              
    y_pred = model.predict(X_test)

                                 
                                                                         
    rmse = root_mean_squared_error(y_test, y_pred)
    
    print(f"Root Mean Squared Error: {rmse:.4f}")

if __name__ == "__main__":
    main()

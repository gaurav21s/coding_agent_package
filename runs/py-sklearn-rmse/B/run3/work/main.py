import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def main():
    # 1. Create synthetic regression dataset
    X, y = make_regression(
        n_samples=200, 
        n_features=3, 
        noise=10, 
        random_state=0
    )

    # 2. Split 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=0
    )

    # 3. Fit LinearRegression
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 4. Predict on test split
    y_pred = model.predict(X_test)

    # 5. Calculate and print RMSE
    # squared=False returns the root mean squared error
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    
    print(f"Root Mean Squared Error: {rmse:.4f}")

if __name__ == "__main__":
    main()

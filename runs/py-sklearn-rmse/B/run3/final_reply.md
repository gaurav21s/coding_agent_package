To create a synthetic regression dataset, split it, train a linear regression model, and calculate the root mean squared error (RMSE), we use `scikit-learn`'s `make_regression`, `train_test_split`, `LinearRegression`, and `mean_squared_error` functions.

The following program performs these steps:
1. Generates the dataset with 200 samples, 3 features, and a noise level of 10.
2. Splits the data into training and testing sets (80/20 split).
3. Fits a `LinearRegression` model on the training data.
4. Predicts the target values for the test set.
5. Calculates and prints the RMSE using `mean_squared_error` with `squared=False` (the modern, non-deprecated way to compute RMSE in scikit-learn).

```python
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
```
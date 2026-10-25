To calculate the root mean squared error (RMSE) using the latest `scikit-learn` standards, we use the `metrics.root_mean_squared_error` function, which replaces the deprecated `squared=False` parameter in `mean_squared_error`.

The following program generates the synthetic dataset, performs the 80/20 split, fits the `LinearRegression` model, and outputs the RMSE.

```python
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

def main():
    # 1. Create synthetic regression dataset
    # 200 samples, 3 features, noise=10, random_state=0
    X, y = make_regression(
        n_samples=200, 
        n_features=3, 
        noise=10, 
        random_state=0
    )

    # 2. Split 80/20 with random_state=0
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
    # Using the modern metrics.root_mean_squared_error as per scikit-learn 1.4+
    rmse = root_mean_squared_error(y_test, y_pred)
    
    print(f"Root Mean Squared Error: {rmse:.4f}")

if __name__ == "__main__":
    main()
```
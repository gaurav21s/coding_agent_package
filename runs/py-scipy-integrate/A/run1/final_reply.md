To compute the integral of $f(x) = x^2$ on the interval $[0, 1]$ using 101 evenly spaced points, we use `numpy` to generate the grid and `scipy.integrate` for the numerical integration methods.

As of October 2026, `scipy.integrate.simpson` is the preferred API (replacing the deprecated `simps`), and `scipy.integrate.trapezoid` is the preferred API (replacing the deprecated `trapz`).

```python
import numpy as np
from scipy.integrate import simpson, trapezoid, cumulative_trapezoid

def main():
    # 1. Generate 101 evenly spaced points on [0, 1]
    x = np.linspace(0, 1, 101)
    y = x**2

    # 2. Compute the integral using Simpson's rule
    # Note: simpson is the modern replacement for simps
    simpson_result = simpson(y=y, x=x)

    # 3. Compute the integral using the trapezoidal rule
    # Note: trapezoid is the modern replacement for trapz
    trapz_result = trapezoid(y=y, x=x)

    # 4. Compute the cumulative trapezoidal integral
    cumulative_result = cumulative_trapezoid(y=y, x=x, initial=0)

    # Print results
    print(f"Simpson's rule integral: {simpson_result}")
    print(f"Trapezoidal rule integral: {trapz_result}")
    print(f"Last value of cumulative trapezoidal integral: {cumulative_result[-1]}")

if __name__ == "__main__":
    main()
```
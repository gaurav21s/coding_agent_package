To compute the definite integral of $\sin(x)$ on the interval $[0, \pi]$ using the trapezoidal rule with NumPy, we use `numpy.linspace` to generate 1001 evenly spaced points and `numpy.trapezoid` (the modern replacement for `numpy.trapz`) to perform the integration.

The following program performs these steps:
1. Creates an array of 1001 points from $0$ to $\pi$ using `np.linspace`.
2. Computes the sine of these points.
3. Uses `np.trapezoid` to calculate the integral.
4. Casts the result to `np.float64`.
5. Rounds the result to 6 decimal places and prints it.

```python
import numpy as np

def main():
    # 1. Sample sin(x) at 1001 evenly spaced points on [0, pi]
    num_points = 1001
    x = np.linspace(0, np.pi, num_points)
    y = np.sin(x)

    # 2. Compute the definite integral with the trapezoidal rule
    # np.trapezoid is the modern replacement for np.trapz (available since NumPy 2.0.0)
    integral = np.trapezoid(y, x)

    # 3. Cast the result to NumPy's 64-bit float type
    result = np.float64(integral)

    # 4. Print it rounded to 6 decimal places
    print(f"{np.round(result, 6):.6f}")

if __name__ == "__main__":
    main()
```
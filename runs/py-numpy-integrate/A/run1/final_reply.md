To compute the definite integral of $\sin(x)$ on $[0, \pi]$ using the trapezoidal rule with NumPy, we define the interval using `np.linspace`, calculate the function values, and apply the trapezoidal integration formula:
$\int_a^b f(x) dx \approx \frac{\Delta x}{2} \sum_{i=1}^{n} (f(x_{i-1}) + f(x_i))$

In NumPy, this is efficiently handled by `np.trapz` (or `np.trapezoid` in newer versions). As of October 2026, `np.trapezoid` is the preferred API, as `np.trapz` is deprecated in recent NumPy releases.

```python
import numpy as np

def main():
    # Define the number of points and the interval
    n_points = 1001
    start = 0.0
    stop = np.pi
    
    # Generate 1001 evenly spaced points
    x = np.linspace(start, stop, n_points)
    
    # Sample sin(x) at these points
    y = np.sin(x)
    
    # Compute the definite integral using the trapezoidal rule
    # np.trapezoid is the current standard (replacing np.trapz)
    integral = np.trapezoid(y, x)
    
    # Cast to 64-bit float explicitly
    result = np.float64(integral)
    
    # Print the result rounded to 6 decimal places
    print(f"{result:.6f}")

if __name__ == "__main__":
    main()
```
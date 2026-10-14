import numpy as np
from scipy import integrate

def main():
    # 1. Generate 101 evenly spaced points on [0, 1]
    x = np.linspace(0, 1, 101)
    y = x**2

    # 2. Compute the integral with Simpson's rule
    # Note: simpson is available in scipy.integrate
    simpson_integral = integrate.simpson(y=y, x=x)

    # 3. Compute the integral with the trapezoidal rule
    # Note: trapezoid is the modern replacement for trapz
    trapezoidal_integral = integrate.trapezoid(y=y, x=x)

    # 4. Compute the cumulative trapezoidal integral
    cumulative_trap = integrate.cumulative_trapezoid(y=y, x=x, initial=0)

    # Print results
    print(f"Simpson's rule integral: {simpson_integral}")
    print(f"Trapezoidal rule integral: {trapezoidal_integral}")
    print(f"Last value of cumulative trapezoidal integral: {cumulative_trap[-1]}")

if __name__ == "__main__":
    main()

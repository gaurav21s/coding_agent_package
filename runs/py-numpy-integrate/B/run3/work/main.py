import numpy as np

def main():
    # 1. Sample sin(x) at 1001 evenly spaced points on [0, pi]
    num_points = 1001
    x = np.linspace(0, np.pi, num_points)
    y = np.sin(x)

    # 2. Compute the definite integral with the trapezoidal rule
    # np.trapezoid is the current API (available since NumPy 2.0.0)
    integral = np.trapezoid(y, x)

    # 3. Cast the result to NumPy's 64-bit float type
    result = np.float64(integral)

    # 4. Print it rounded to 6 decimal places
    print(f"{result:.6f}")

if __name__ == "__main__":
    main()

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

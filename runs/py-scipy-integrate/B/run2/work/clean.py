import numpy as np
from scipy import integrate

def main():
                                                    
    x = np.linspace(0, 1, 101)
    y = x**2

                                                 
                                                   
    simpson_integral = integrate.simpson(y=y, x=x)

                                                       
                                                         
    trapezoidal_integral = integrate.trapezoid(y=y, x=x)

                                                    
    cumulative_trap = integrate.cumulative_trapezoid(y=y, x=x, initial=0)

                   
    print(f"Simpson's rule integral: {simpson_integral}")
    print(f"Trapezoidal rule integral: {trapezoidal_integral}")
    print(f"Last value of cumulative trapezoidal integral: {cumulative_trap[-1]}")

if __name__ == "__main__":
    main()

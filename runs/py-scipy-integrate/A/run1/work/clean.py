import numpy as np
from scipy.integrate import simpson, trapezoid, cumulative_trapezoid

def main():
                                                    
    x = np.linspace(0, 1, 101)
    y = x**2

                                                  
                                                       
    simpson_result = simpson(y=y, x=x)

                                                        
                                                         
    trapz_result = trapezoid(y=y, x=x)

                                                    
    cumulative_result = cumulative_trapezoid(y=y, x=x, initial=0)

                   
    print(f"Simpson's rule integral: {simpson_result}")
    print(f"Trapezoidal rule integral: {trapz_result}")
    print(f"Last value of cumulative trapezoidal integral: {cumulative_result[-1]}")

if __name__ == "__main__":
    main()

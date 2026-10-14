import numpy as np

def main():
                                                              
    num_points = 1001
    x = np.linspace(0, np.pi, num_points)
    y = np.sin(x)

                                                                
                                                                   
    integral = np.trapezoid(y, x)

                                                     
    result = np.float64(integral)

                                             
    print(f"{result:.6f}")

if __name__ == "__main__":
    main()

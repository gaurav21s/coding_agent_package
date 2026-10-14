import numpy as np

def main():
                                                  
    n_points = 1001
    start = 0.0
    stop = np.pi
    
                                        
    x = np.linspace(start, stop, n_points)
    
                                   
    y = np.sin(x)
    
                                                              
                                                               
    integral = np.trapezoid(y, x)
    
                                     
    result = np.float64(integral)
    
                                                  
    print(f"{result:.6f}")

if __name__ == "__main__":
    main()

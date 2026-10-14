import matplotlib
                                                                 
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def main():
                                              
                                                      
    viridis = matplotlib.colormaps['viridis']

                                           
                                       
    indices = np.linspace(0, 1, 5)
    colors = viridis(indices)

                      
    print("5 evenly spaced RGBA colors from 'viridis':")
    for i, color in enumerate(colors):
        print(f"Color {i+1}: {color}")

                                                  
    fig, ax = plt.subplots()
    x = np.arange(5)
    heights = [1, 2, 3, 4, 5]
    
    ax.bar(x, heights, color=colors)
    ax.set_title("5-bar chart with Viridis colors")
    
                      
    fig.savefig('bars.png')
    print("\nChart saved to 'bars.png'.")

if __name__ == "__main__":
    main()

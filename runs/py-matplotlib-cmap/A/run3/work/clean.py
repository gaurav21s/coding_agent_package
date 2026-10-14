import matplotlib
                                                                               
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.colormaps as cmaps
import numpy as np

def main():
                                              
    viridis = cmaps['viridis']

                                           
                                                            
    indices = np.linspace(0, 1, 5)
    colors = [viridis(i) for i in indices]

                      
    print("5 sampled RGBA colors from viridis:")
    for i, color in enumerate(colors):
        print(f"Color {i+1}: {color}")

                                 
    fig, ax = plt.subplots()
    x = np.arange(1, 6)
    heights = [10, 20, 15, 25, 30]
    
    ax.bar(x, heights, color=colors)
    ax.set_title("Viridis 5-Bar Chart")
    ax.set_xlabel("Bar Index")
    ax.set_ylabel("Value")

                         
    plt.savefig('bars.png')
    print("\nChart saved successfully as 'bars.png'.")

if __name__ == "__main__":
    main()

import matplotlib
# Set the backend to Agg before importing pyplot to ensure non-interactive mode
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.colormaps as cmaps
import numpy as np

def main():
    # 1. Look up the 'viridis' colormap object
    viridis = cmaps['viridis']

    # 2. Sample 5 evenly spaced RGBA colors
    # np.linspace(0, 1, 5) gives [0.0, 0.25, 0.5, 0.75, 1.0]
    indices = np.linspace(0, 1, 5)
    colors = [viridis(i) for i in indices]

    # Print the colors
    print("5 sampled RGBA colors from viridis:")
    for i, color in enumerate(colors):
        print(f"Color {i+1}: {color}")

    # 3. Create a 5-bar bar chart
    fig, ax = plt.subplots()
    x = np.arange(1, 6)
    heights = [10, 20, 15, 25, 30]
    
    ax.bar(x, heights, color=colors)
    ax.set_title("Viridis 5-Bar Chart")
    ax.set_xlabel("Bar Index")
    ax.set_ylabel("Value")

    # 4. Save to bars.png
    plt.savefig('bars.png')
    print("\nChart saved successfully as 'bars.png'.")

if __name__ == "__main__":
    main()

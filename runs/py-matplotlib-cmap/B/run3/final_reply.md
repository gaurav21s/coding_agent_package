To accomplish this task, we use `matplotlib.colormaps` to retrieve the 'viridis' colormap object. We then sample 5 evenly spaced colors from it using the `linspace` function from `numpy` to generate the indices, and pass these to the colormap object. Finally, we use the `matplotlib.backends.backend_agg` backend to create a figure and save it as a PNG file.

```python
import matplotlib
# Set the backend to Agg before importing pyplot or other modules
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def main():
    # 1. Look up the 'viridis' colormap object
    # Using matplotlib.colormaps (available since 3.6)
    viridis = matplotlib.colormaps['viridis']

    # 2. Sample 5 evenly spaced RGBA colors
    # Generate 5 values between 0 and 1
    indices = np.linspace(0, 1, 5)
    colors = viridis(indices)

    # Print the colors
    print("5 evenly spaced RGBA colors from 'viridis':")
    for i, color in enumerate(colors):
        print(f"Color {i+1}: {color}")

    # 3. Save a 5-bar bar chart using those colors
    fig, ax = plt.subplots()
    x = np.arange(5)
    heights = [1, 2, 3, 4, 5]
    
    ax.bar(x, heights, color=colors)
    ax.set_title("5-bar chart with Viridis colors")
    
    # Save to bars.png
    fig.savefig('bars.png')
    print("\nChart saved to 'bars.png'.")

if __name__ == "__main__":
    main()
```
import json

import matplotlib as mpl
import matplotlib.pyplot as plt


def discretize_colormap(cmap_name, n_colors):
    """
    Returns a matplotlib colormap object.
    Based on this example: www.stackoverflow.com/questions/14777066/matplotlib-discrete-colorbar.

    Args:
        cmap_name: Name of a matplotlib colormap.
        n_colors: Number of discrete colors.

    Returns:
        cmap: matplotlib colormap objects.
    """
    cmap = plt.get_cmap(cmap_name)
    cmap_list = [cmap(i) for i in range(cmap.N)]
    step = int(cmap.N / (n_colors - 1))
    valid_indices = [i * step - 1 for i in range(n_colors)]
    valid_indices[0] = 0
    cmap_list = [color for i, color in enumerate(cmap_list) if i in valid_indices]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "custom", cmap_list, len(cmap_list)
    )
    return cmap


def make_linear_colormap(colors):
    """
    Returns a matplotlib colormap object.

    Args:
        colors: List of colors to add to the colormap.

    Returns:
        cmap: a matplotlib colormap object.
    """
    cmap = mpl.colors.ListedColormap(colors)
    return cmap


def load_configuration():
    """
    Loads settings from the global configuration file.

    Returns:
        config: Dictionary containing configuration settings.
    """
    CONFIGURATION_FILENAME = "configuration.json"
    with open(CONFIGURATION_FILENAME, "r") as f:
        config = json.load(f)
        return config

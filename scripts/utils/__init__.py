import json

import matplotlib as mpl
import matplotlib.pyplot as plt
from tqdm import tqdm
from chemfiles import Trajectory


def _discretize_colormap(cmap_name, n_colors):
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


def _make_linear_colormap(colors):
    """
    Returns a matplotlib colormap object.

    Args:
        colors: List of colors to add to the colormap.

    Returns:
        cmap: matplotlib colormap object.
    """
    cmap = mpl.colors.ListedColormap(colors)
    return cmap


def load_configuration():
    """
    Loads settings from the global configuration file.

    Returns:
        config: dict containing configuration settings.
    """
    CONFIGURATION_FILENAME = "configuration.json"
    with open(CONFIGURATION_FILENAME, "r") as f:
        config = json.load(f)
        return config


def load_positions_from_lammps_dump_file(filepath, atom_types):
    """
    Reads the positions of all relevant atoms from a LAMMPS dump file.

    Returns:
        (atom_types, positions)
        atom_types: list of each atom type in order. This order does not change so 
                    it is given only once - not for each frame. 
        positions: position of each relevant atom in the trajectory for each frame 
    """
    with Trajectory(filepath, mode="r", format="LAMMPS") as trajectory:
        first_frame = trajectory.read_step(0)
        relevant_indices = [
            i for i, atom in enumerate(first_frame.atoms)
            if atom.type in atom_types
        ]
        atom_types = [
            first_frame.atoms[i].type 
            for i in relevant_indices
        ]
        positions = []
        print("Extracting atom positions...")
        for i in tqdm(range(trajectory.nsteps)):
            frame = trajectory.read_step(i)
            pos = [frame.positions[i] for i in relevant_indices]
            positions.append(pos)
        return atom_types, positions

def process_color_and_cmap_args(args, n_series):
    """
    Returns the appropriate colormap from a given set of arguments.

    Args:
        args: command line arguments.
        n_series: number of data series.

    Returns:
        cmap: matplotlib colormap object.
    """
    if args.color:
        cmap = _make_linear_colormap(args.color)
    else:
        # Use either tab10 as the default or a named colormap if one is provided.
        if args.cmap is None:
            cmap = plt.get_cmap("tab10")
        else:
            cmap = _discretize_colormap(args.cmap, n_series)
    return cmap


def process_label_args(args, n_series):
    """
    Returns a boolean indicating whether or not to render a legend and a list of labels for each data series.

    Args:
        args: command line arguments.
        n_series: number of data series.

    Returns:
        (render_legend, labels): tuple containing boolean flag to render the legend and a list of data series labels.
    """
    render_legend = True
    # Make the labels an empty list if none are provided.
    # - this is required for consistent iteration.
    if args.label:
        labels = args.label
    else:
        render_legend = False
        labels = ["" for _ in range(n_series)]
    return (render_legend, labels)



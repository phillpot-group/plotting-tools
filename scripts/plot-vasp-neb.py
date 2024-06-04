DESCRIPTION = """
Plots the barrier height from a VTST formatted NEB data file. 
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from utils import load_configuration, process_color_and_cmap_args, process_label_args


def parse_vasp_neb_file(fp):
    """
    Parses the barrier height and scaled positions from a VTST formatted NEB data file.

    Args:
        fp: File pointer to a VTST formatted NEB data file.

    Returns:
        (energies, scaled_positions): tuple containing an array of barrier height energies and an array of scaled positions along the path.
    """
    # Create a list of all lines in the file.
    lines = [line.strip() for line in fp.readlines()]
    # Extract the positions (2nd column).
    positions = [float(line.split()[1]) for line in lines]
    # Extract the raw positions (3rd column).
    energies = [float(line.split()[2]) for line in lines]
    # Normalize each position by the largest in the set.
    max_pos = max(positions)
    scaled_positions = [pos / max_pos for pos in positions]
    return (energies, scaled_positions)


def main(args):
    # Initialize the figure.
    fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
    # Process the label argument.
    render_legend, labels = process_label_args(args, len(args.input))
    # Process the linestyle argument.
    # TODO: move this to utils if used anywhere else.
    # Make the default linestyle "solid" for each data series.
    if args.linestyle:
        linestyles = args.linestyle
    else:
        linestyles = ["solid" for _ in range(len(args.input))]
    # Process the color and cmap arguments.
    cmap = process_color_and_cmap_args(args, len(args.input))
    # Iterate over each data series.
    for i, fp in enumerate(args.input):
        # Parse the data file.
        energies, scaled_positions = parse_vasp_neb_file(fp)
        # Plot the results as a continuous line.
        ax.plot(
            scaled_positions,
            energies,
            label=labels[i],
            color=cmap(1.0 * i / cmap.N),
            linestyle=linestyles[i],
        )
        # Superimpose the data as a scatter plot to highlight explicit image positions.
        ax.scatter(
            scaled_positions,
            energies,
            color=cmap(1.0 * i / cmap.N),
        )
    # Only render the legend if there are valid labels.
    if render_legend:
        ax.legend()
    # Set axis labels.
    ax.set_xlabel("Normalized Path Length")
    ax.set_ylabel("Migration Energy (eV)")

    # Save the resulting figure
    plt.savefig(args.output, dpi=300)


if __name__ == "__main__":
    # Load the global configuration file.
    global_config = load_configuration()
    # Update the matplotlib settings.
    plt.rcParams.update(global_config)
    # Build the argument parser.
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        type=argparse.FileType("r"),
        help="path to a VTST formatted NEB data file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="figures/plot-vasp-neb.png",
        help="path to save the resulting figure to",
    )
    parser.add_argument(
        "-l",
        "--label",
        nargs="*",
        help="label to associate with each data series",
    )
    parser.add_argument(
        "-c",
        "--color",
        nargs="*",
        help="color to associate with each data series",
    )
    parser.add_argument(
        "--cmap",
        required=False,
        help="colormap used to assign colors to each data series",
    )
    parser.add_argument(
        "-ls",
        "--linestyle",
        nargs="*",
        choices=["solid", "dotted", "dashed", "dashdot"],
        help="linestyle to associate with each data series",
    )
    # Parse the arguments.
    args = parser.parse_args()
    # Validate the arguments.
    # Assert that all optional per-series arguments have the same length.
    n_inputs = len(args.input)
    if args.label:
        n_labels = len(args.label)
        try:
            assert n_labels == n_inputs
        except AssertionError as e:
            e.args += f"number of labels `{n_labels}` does not match number of inputs `{n_inputs}`"
            raise
    if args.color:
        n_colors = len(args.color)
        try:
            assert n_colors == n_inputs
        except AssertionError as e:
            e.args += f"number of colors `{n_colors}` does not match number of inputs `{n_inputs}`"
            raise
    if args.linestyle:
        n_linestyles = len(args.linestyle)
        try:
            assert n_linestyles == n_inputs
        except AssertionError as e:
            e.args += f"number of linestyles `{n_linestyles}` does not match number of inputs `{n_inputs}`"
    # Generate the plot.
    main(args)

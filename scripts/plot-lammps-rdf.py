DESCRIPTION = """
Plots the time averaged RDF exported from a LAMMPS simulation.
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from utils import load_configuration, process_color_and_cmap_args, process_label_args


def _parse_rdf_distances(lines):
    """
    Parse the distance column from the first timestep block of a LAMMPS RDF file.
    """
    distances = []
    for line in lines:
        elements = [float(elem.strip()) for elem in line.split()]
        distance = elements[1]
        distances.append(distance)
    return np.array(distances)


def _parse_rdf_block(lines, columns):
    """
    Parse an individual timestep block from a LAMMPS RDF file.
    """
    # Create a dict to hold data for each column in the block.
    block_data = {col: [] for col in columns}
    for line in lines:
        # Breakup each individual line.
        elements = [float(elem.strip()) for elem in line.split()]
        # Iterate over desired columns.
        for col_id in columns:
            # Create an offset ID to ignore the bin id and distance columns.
            offset_id = col_id + 2
            block_data[col_id].append(elements[offset_id])
    return block_data


def _parse_rdf_file(fp, columns):
    """
    Collect all data from a LAMMPS RDF file.
    """
    # Create a list of all lines in the file.
    lines = [line.strip() for line in fp.readlines()]
    # Remove the comments from the first 3 lines.
    lines = lines[2:]
    # Initialize a None value to make sure distances are parsed only once.
    distances = None
    # Create a dict to store all RDF data for all specified columns.
    column_data = {i: [] for i in columns}
    # Enumerate over all lines searching for blocks.
    print(f"Parsing {args.input.name}...")
    for i, line in enumerate(lines):
        split_line = line.split()
        # New blocks are identified by a 2 part header line.
        if len(split_line) == 2:
            nrows = int(split_line[1])
            # Parse the data in the block
            _lines = lines[i+1:i+1+nrows]
            block_data = _parse_rdf_block(_lines, columns)
            if distances is None:
                distances = _parse_rdf_distances(_lines)
            for col in columns:
                column_data[col].append(block_data[col])
    for col in columns:
        column_data[col] = np.array(column_data[col])
    return distances, column_data


def main(args):
    distances, column_data = _parse_rdf_file(args.input, args.column)
    render_legend, labels = process_label_args(args, len(args.column))
    cmap = process_color_and_cmap_args(args, len(args.column))
    fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
    for i, col_id in enumerate(args.column):
        data = np.mean(column_data[col_id], axis=0)
        ax.plot(
            distances, 
            data,
            label=labels[i],
            color=cmap(float(i) / cmap.N),
        )
    ax.set_xlabel("Distance ($\AA$)")
    ax.set_ylabel("$g(r)$")
    # Only render the legend if labels are provided.
    if render_legend:
        ax.legend()
    # Save the resulting figure.
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
        type=argparse.FileType("r"),
        help="path to a LAMMPS rdf file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="figures/plot-lammps-rdf.png",
        help="path to save the resulting figure to",
    )
    parser.add_argument(
        "--column",
        nargs="+",
        type=int,
        help="index of the data column(s) to plot (bin id and distance columns do not count)"
    )
    parser.add_argument(
        "-c",
        "--color",
        nargs="*",
        help="color to associate with each data column",
    )
    parser.add_argument(
        "-l",
        "--label",
        nargs="*",
        help="label to associate with each data column",
    )
    parser.add_argument(
        "--cmap",
        required=False,
        help="colormap used to assign colors to each data column",
    )
    # Parse the arguments.
    args = parser.parse_args()
    # Validate the arguments.
    # Assert the number of colors and labels matches the number of columns.
    if args.color:
        try:
            assert len(args.color) == len(args.column)
        except AssertionError as e:
            e.args += "number of colors must match number of columns"
            raise
    if args.label:
        try:
            assert len(args.label) == len(args.column) 
        except AssertionError as e:
            e.args += "number of labels must match number of columns"
    # Generate the plot.
    main(args)

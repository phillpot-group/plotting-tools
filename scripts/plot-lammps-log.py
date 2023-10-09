DESCRIPTION = """
Plots the results of a LAMMPS simulation contained in its log file.
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from utils import discretize_colormap, load_configuration, make_linear_colormap


def parse_lammps_log_file(fp, property_names):
    """
    Parses a list of desired properties from an individual LAMMPS log file.

    Args:
        fp: File pointer to a LAMMPS log file.
        property_names: List of property names.

    Returns:
        (steps, properties): Returns a tuple containing an array of timesteps and a dict of arrays of properties mapped to their names.

    Raises:
        AssertionError: if the 'Step' property is not found in the log file.
    """
    # Create a list of all lines in the file.
    lines = [line.strip() for line in fp.readlines()]
    # Treat the first line as a list of headers.
    headings = [heading.strip() for heading in lines[0].split()]
    # Assert that the timesteps have been logged in this file.
    try:
        assert "Step" in headings
    except AssertionError as e:
        e.args += "Log file is missing the required 'Step' property."
        raise
    # Map the headings to their positions.
    # - this is faster than using 'find()' for each line in the file.
    headings_map = {heading: index for index, heading in enumerate(headings)}
    # Tokenize each line after the heading line.
    segments = [line.split() for line in lines[1:]]
    # Extract the properties into a dict.
    properties = {
        prop_name: [float(segment[headings_map[prop_name]]) for segment in segments]
        for prop_name in args.property
    }
    # Extract the timesteps separately.
    steps = [int(segment[headings_map["Step"]]) for segment in segments]
    return (steps, properties)


def main(args):
    # Initialize the figure.
    fig, ax = plt.subplots(figsize=(10, 6), layout="constrained")
    # Get the total number of data series.
    n_series = len(args.input) * len(args.property)
    # Process the label argument.
    render_legend = True
    # Make the labels an empty list if none are provided.
    # - this is required for consistent iteration.
    if not args.label:
        render_legend = False
        args.label = ["" for _ in range(n_series)]
    # Process the color and cmap arguments.
    if args.color:
        cmap = make_linear_colormap(args.color)
    else:
        # Use either tab10 as the default or a named colormap if one is provided.
        if args.cmap is None:
            cmap = plt.get_cmap("tab10")
        else:
            cmap = discretize_colormap(args.cmap, n_series)

    # Initialize a combined indexer.
    i = 0
    # Iterate over input files.
    for fp in args.input:
        steps, properties = parse_lammps_log_file(fp, args.property)
        # Iterate over property names.
        for prop_name in args.property:
            ax.plot(
                steps,
                [prop for prop in properties[prop_name]],
                label=f"{args.label[i]}",
                color=cmap(1.0 * i / cmap.N),
            )
            i += 1

    # Only render the legend if there are valid labels.
    if render_legend:
        ax.legend()
    # Only render the Y axis label if there is one provided.
    if args.ylabel:
        ax.set_ylabel(f"{args.ylabel}")
    # The X axis will always be timestep so that can be hardcoded.
    ax.set_xlabel("Timestep")

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
        nargs="+",
        type=argparse.FileType("r"),
        help="path to a LAMMPS log file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="figures/plot-lammps-log.png",
        help="path to save the resulting figure to",
    )
    parser.add_argument(
        "-y",
        "--ylabel",
        required=False,
        help="Y axis label",
    )
    parser.add_argument(
        "-p",
        "--property",
        nargs="+",
        help="property name to extract from the log file",
    )
    parser.add_argument(
        "-l",
        "--label",
        nargs="*",
        help="label to associate with data series",
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
    # Parse the arguments.
    args = parser.parse_args()
    # Validate the arguments.
    # Assert that there is EITHER:
    # 1 input file and 1 or more properties
    # OR
    # 1 property and 1 or more input files
    if len(args.property) > 1:
        try:
            assert len(args.input) == 1
        except AssertionError as e:
            e.args += "too many input files: must have exactly 1 input file if plotting multiple properties"
            raise
    if len(args.input) > 1:
        try:
            assert len(args.property) == 1
        except AssertionError as e:
            e.args += "too many properties: must have exactly 1 property if plotting multiple input files"
            raise
    # Assert that the number of labels and colors is the same as the number of data series.
    n_series = len(args.input) * len(args.property)
    if args.color:
        n_colors = len(args.color)
        try:
            assert n_colors == n_series
        except AssertionError as e:
            e.args += f"number of colors `{n_colors}` does not match number of data series `{n_series}`"
            raise
    if args.label:
        n_labels = len(args.label)
        try:
            assert n_labels == n_series
        except AssertionError as e:
            e.args += f"number of labels `{n_labels}` does not match number of data series `{n_series}`"
            raise
    # Generate the plot.
    main(args)

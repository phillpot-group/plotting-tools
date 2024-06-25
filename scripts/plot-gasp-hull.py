DESCRIPTION = """
Plots the convex hull of structures created by a GASP run.
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from pymatgen.analysis.phase_diagram import PDEntry, PDPlotter, PhaseDiagram
from pymatgen.core.composition import Composition


def parse_run_data_file(fp):
    """
    Parses the GASP run_data file into a list of phase diagram entries.

    Args:
        fp: File pointer to a GASP run_data file.

    Returns:
        entries: List of PDEntry objects.
    """
    # Extract each line.
    lines = [line.strip().replace("\t", "") for line in fp.readlines()]
    # Remove empty lines.
    lines = [line for line in lines if len(line) > 0]
    # Pop out the first line which contains the endpoints.
    first_line = lines.pop(0)
    # Pop out the header line because it contains spaces which disrupt parsing.
    header_line = lines.pop(0)
    # Convert the list of lines back into a buffer for CSV reading.
    string = "\n".join(lines)
    buffer = StringIO(string)
    # Convert the columnar data file into a DataFrame.
    col_names = ["id", "composition", "total_energy", "epa", "num_calcs", "best_value"]
    df = pd.read_csv(
        buffer,
        delimiter=" ",
        index_col=[0],
        names=col_names,
        header=None,
    )
    # Extract endpoints from the first line.
    endpoints = first_line.replace("Composition space endpoints:", "").strip().split()
    endpoints = [Composition(endpoint) for endpoint in endpoints]
    # Alter the composition column.
    df["composition"] = [Composition(comp) for comp in df["composition"]]
    # Find the lowest per atom energy for each endpoint to use as a reference.
    endpoint_energy = {endpoint.reduced_formula: 0 for endpoint in endpoints}
    for endpoint in endpoint_energy.keys():
        for _, row in df.iterrows():
            current_min = endpoint_energy[endpoint]
            reduced_form = row["composition"].reduced_formula
            epa = row["epa"]
            if reduced_form == endpoint and epa < current_min:
                endpoint_energy[endpoint] = epa
    # Add columns containing the atom fraction of each endpoint.
    for endpoint in endpoint_energy.keys():
        df[f"atom_frac_{endpoint}"] = [
            comp.get_atomic_fraction(endpoint) for comp in df["composition"]
        ]
    # Add columns containing the number of atoms of each endpoint type.
    for endpoint in endpoint_energy.keys():
        df[f"n_atoms_{endpoint}"] = [
            comp.num_atoms * atom_frac
            for comp, atom_frac in zip(df["composition"], df[f"atom_frac_{endpoint}"])
        ]
    # Calculate formation energy.
    formation_energy = []
    for _, row in df.iterrows():
        etotal = row["total_energy"]
        for k, v in endpoint_energy.items():
            etotal -= endpoint_energy[k] * row[f"n_atoms_{k}"]
        formation_energy.append(etotal)
    df["eform"] = formation_energy
    # Create a list of phase diagram entries.
    entries = [
        PDEntry(comp, eform) for comp, eform in zip(df["composition"], df["eform"])
    ]
    return entries


def main(args):
    # Get the phase diagram entries.
    entries = parse_run_data_file(args.input)
    # Initialize a phase diagram object.
    phase_diagram = PhaseDiagram(entries)
    # Initialize the plotter and show.
    plotter = PDPlotter(phase_diagram, show_unstable=10.0)
    plotter.show()


if __name__ == "__main__":
    # Usually we load the global config for matplotlib settings here.
    # In this case we do not because the PDPlotter object has its own styling.

    # Build the argument parser.
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r"),
        help="path to a GASP run_data file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="figures/plot-gasp-hull.png",
        help="path to save the resulting figure to",
    )
    # Parse the arguments.
    args = parser.parse_args()
    # No validation required.
    # Generate the plot.
    main(args)

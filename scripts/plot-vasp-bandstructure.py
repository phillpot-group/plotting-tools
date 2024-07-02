DESCRIPTION = """
Plots the band structure from VASPKIT formatted band structure data files.
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.collections import LineCollection
from pymatgen.io.vasp.inputs import Poscar
from tqdm import tqdm

from utils import load_configuration


def get_elements_in_structure():
    """
    Extracts the elements in the structure from the POSCAR file.

    Returns:
        elements: List of elements in the structure.

    Raises:
        ValueError: If no elements are found in the POSCAR file.
    """
    # Load the POSCAR file.
    poscar = Poscar.from_file("POSCAR")
    # Extract the structure from the POSCAR file.
    structure = poscar.structure
    # Extract the elements in the structure.
    elements = [str(e) for e in structure.composition.elements]
    # Check if POSCAR was formatted correctly to contain elements.
    if not elements:
        raise ValueError("No elements found in POSCAR file.")
    return elements


def locate_required_files(args):
    """
    Locates the required files for plotting the band structure.

    Args:
        args: Namespace containing the command-line arguments.

    Returns:
        filepaths: List of filepaths.
    """
    # Get elements to populate filepath patterns.
    elements = get_elements_in_structure()
    # Generate possible patterns for file search.
    patterns = [
        "BAND.dat",
        "PBAND_{element}.dat",
        "PBAND_{element}_UP.dat",
        "PBAND_{element}_DW.dat",
    ]
    # Check command line arguments to determine required patterns.
    if args.elemental:
        patterns = patterns[1:]
        if args.spin:
            patterns = patterns[1:]
        else:
            patterns = patterns[:1]
    else:
        patterns = patterns[:1]
    # Locate the required files using the established patterns.
    filepaths = []
    for pattern in patterns:
        for element in elements:
            filepath = pattern.format(element=element)
            if os.path.exists(filepath):
                filepaths.append(filepath)
    # Check that the expected number of files were found.
    n_filepaths = len(filepaths)
    n_elements = len(elements)
    # TODO: give more informative error messages.
    if args.elemental:
        if args.spin:
            assert n_filepaths == 2 * n_elements
        else:
            assert n_filepaths == n_elements
    else:
        assert n_filepaths == 1
    return filepaths


def parse_klabels_file():
    """
    Parses the k-point labels and positions from the KLABELS file.

    Returns:
        klabels, kpositions: List of k-labels and their positions.
    """
    # Load the KLABELS file.
    filename = "KLABELS"
    with open(filename, "r") as f:
        lines = f.readlines()
    # Clean up lines.
    lines = [line.strip() for line in lines]
    # Locate the last useful line.
    end_index = lines.index("")
    header = lines[0]
    # Extract lines containing labels.
    data = lines[1:end_index]
    klabels = []
    kpositions = []
    for line in data:
        klabel, position = [segment.strip() for segment in line.split()]
        # Apply custom formatting to GAMMA.
        if klabel == "GAMMA":
            klabel = r"$\Gamma$"
        position = float(position)
        klabels.append(klabel)
        kpositions.append(position)
    return klabels, kpositions


def parse_band_file(filepath):
    """
    Parses the band structure from a BAND.dat file
    or any PBAND_{X}.dat projected variants.

    Args:
        filename: Path to the BAND.dat file.

    Returns:
        band_data: List of dicts containing the band structure data.
    """
    # Load the PBAND file.
    with open(filepath, "r") as f:
        lines = f.readlines()
    # Clean up lines.
    lines = [line.strip() for line in lines]
    # Extract the header.
    header = lines[0]
    # Identify the column labels.
    labels = [label.strip() for label in header.split()]
    # Extract the band metadata.
    metadata = lines[1]
    nkpts, nbands = metadata.split(":")[-1].split()
    nkpts, nbands = int(nkpts.strip()), int(nbands.strip())
    # Set a starting index for the data.
    start_index = 3 # Skip the 'Band-Index' line.
    band_data = []
    # Iterate over each band section
    for i in range(nbands):
        index = start_index + (i * nkpts)
        _band_data = {label: [] for label in labels} # Data for a sinle band.
        for j in range(nkpts):
            # Extract the band data.
            data = lines[index + j]
            data = [float(d.strip()) for d in data.split()]
            # Store the band data.
            for label, col_data in zip(labels, data):
                _band_data[label].append(col_data)
        band_data.append(_band_data)
    return band_data


def _plot_elemental_band_structure(args, ax):
    pass


def _plot_orbital_bandstructure(args, ax):
    pass


def _plot_bandstructure(args, ax):
    # Load band data.
    # Basic band structure plot requires only BAND.dat file. 
    filenames = locate_required_files(args)
    assert len(filenames) == 1
    assert filenames[0] == "BAND.dat"
    band_data = parse_band_file(filenames[0])
    column_labels = band_data[0].keys()
    x_data_label = column_labels[0] # Position along K-path.
    if args.spin:
        y_data_labels = column_labels[1:]
        assert len(y_data_labels) == 2
        linestyles = ["solid", "dashed"] # Assign different style to up and down channels.
        for _label, linestyle in zip(y_data_labels, linestyles):
            for band in band_data:
                ax.plot(band[x_data_label], band[_label], linestyle=linestyle)
            # Reset the colormap cycle for each spin channel.
            ax.set_prop_cycle(None)
    else:
        y_data_label = column_labels[1]
        for band in band_data:
            ax.plot(band[x_data_label], band[y_data_label])


def main(args):
    # Initialize matplotlib figure.
    fig, ax = plt.subplots(figsize=(8,6), layout="constrained")
    # Handle the specific plotting case.
    if args.elemental:
        ax = _plot_elemental_band_structure(args)
    elif args.orbital:
        ax = _plot_orbital_bandstructure(args)
    else:
        ax = _plot_bandstructure(args)
    # Get K-labels and their positions.
    klabels, kpositions = parse_klabels_file()
    # Apply general formatting valid for all plot types.
    # TODO: This will not work for multiple plot generation.
    ax.set_xticks(kpositions)
    ax.set_xticklabels(klabels)
    ax.set_ylabel(r"E - $E_{Fermi}$ (eV)")
    ax.set_ylim((args.emin, args.emax))
    plt.axhline(y=0, color="black", linewidth=1, linestyle="--")
    plt.vlines(kpositions, args.emin, args.emax, color="black", linewidth=1)
    plt.xticks(visible=False)
    plt.savefig(args.output, dpi=300)


if __name__ == "__main__":
    # Load the global configuration file.
    global_config = load_configuration()
    # Update the matplotlib settings.
    plt.rcParams.update(global_config)
    # Build the argument parser.
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--elemental",
        action="store_true",
        help="Plot the element projected band structure.",
    )
    parser.add_argument(
        "--spin",
        action="store_true",
        help="Plot the spin projected band structure.",
    )
    parser.add_argument(
        "--orbital",
        action="store_true",
        help="Plot the orbital projected band structure.",
    )
    parser.add_argument(
        "--emin",
        type=float,
        default=None,
        help="Minimum energy.",
    )
    parser.add_argument(
        "--emax",
        type=float,
        default=None,
        help="Maximum energy.",
    )
    parser.add_argument(
        "--output",
        default="figures/plot-vasp-bandstructure.png",
        help="Path to save the resulting figure to. Inputs that generate multiple files will append identifying information to the base path.",
    )
    args = parser.parse_args()
    # TODO: Figure out if weighting should be normalized to stoichiometry.
    if args.elemental:
        raise NotImplementedError("Elemental projection not yet supported.")
    # TODO: Collect px, py, pz into single orbital contribution.
    if args.orbital:
        raise NotImplementedError("Orbital projection not yet supported.")

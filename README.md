# plotting-tools

This package contains scripts that create the types of figures which are commonly required in our line of work. This is by no means a comprehensive collection of all the tools you will ever need, but it does serve as a head start to automate some of the most generalizable tasks. It can be hard to strike a balance between ease of use and customizability so in this work the focus is to provide a highly accessible platform which you can fork and add necessary customizations to.


## Getting Started

__1) Install Anaconda__

This project uses [Anaconda](https://www.anaconda.com/download) to manage Python versions and external dependencies. Use the link to download the version which is compatible with your operating system.

__2) Clone this repository__

To make this code available on your local computer you will need to clone it with [git](https://git-scm.com/docs/user-manual). Use the following command line snippet to do so. If you run into a problem with SSH keys follow this [tutorial](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).

```bash
git clone git@github.com:phillpot-group/plotting-tools.git && cd plotting-tools
```

__3) Activate the conda environment__

The environment specification for this package is contained in [environment.yml](environment.yml). To build this environment on a new installation use the following command line snippet.

```bash
conda env create -f environment.yml
```

With the environment installed on your local system you can now activate it with the following command line snippet.

```bash
conda activate plotting-tools
```

:warning: __NOTE:__ You need to activate the environment every time you intend to use one of the scripts.

## Examples

Each of the scripts contained in this repository has an example in the section below. Not all of the features of each script will necessarily be shown in each example. Remember that each script has a `--help` flag which will print out all of its functionality. Exact filenames of input data files are excluded from all the example snippets shown below for the sake of brevity.

### [plot-lammps-log.py](scripts/plot-lammps-log.py)

![](figures/plot-lammps-log.png)


This script plots the results of a LAMMPS simulation that are recorded in the thermodynamic log file. The log file is structured according to the [`thermo_style` command](https://docs.lammps.org/thermo_style.html). You may plot multiple properties from the same input file __OR__ one property from multiple input files on the same figure. Doing both at once gets very busy and difficult to manage.

:warning: __NOTE:__ This script requires some manual preprocessing. You must remove the lines before the property headers and the lines after the final result is logged. Automating this data cleanup in a reliable way is a future goal. The __first__ lines of the file should resemble the snippet below.
```
Step PotEng KinEng TotEng Temp Press Lx Ly Lz
10000000   -426912.05    5143.4244   -421768.63    349.36471    1517.6243    58.648234    50.784771    25.000006
10001000   -424814.66    6497.2063   -418317.45    441.31972    1944.3129    58.648234    50.784771    24.494777
```

The __last__ lines of the file should resemble the snippet below.
```
23999000    -427656.8    4473.5478   -423183.25    303.86365     2940.087    58.648234    50.784771    19.312015
24000000   -427566.49    4397.7291   -423168.76     298.7137    4548.3145    58.648234    50.784771    19.373656
```

Any number of thermodynamic properties can be included in the file but it is __required__ that the `Step` property is included because that data will be plotted along the *X* axis.

The example image was generated with the following command line snippet. 
```bash
python scripts/plot-lammps-log.py -i <file1> <file2> <file3> -p Lz -y "Interlayer Spacing \$(\AA)\$" -l "1.00:1" "0.75:1" "0.50:1" --cmap cool
```

### [plot-vasp-neb.py](scripts/plot-vasp-neb.py)

![](figures/plot-vasp-neb.png)

This script plots the barrier height extracted from VTST formatted NEB data files. Multiple data files can be plotted on the same figure. The format is simple and no manual data cleanup is required. An example of a VTST formatted NEB data file is included below.
```
  0     0.000000     0.000000     0.000000   0
  1     0.448371     0.306312    -1.557052   1
  2     0.897158     1.140628    -1.747238   2
  3     1.345602     1.648306    -0.760372   3
  4     1.792816     1.842974     0.000857   4
  5     2.229737     1.656236     0.833244   5
  6     2.666949     1.079524     1.838625   6
  7     3.103779     0.275705     1.483517   7
  8     3.539372    -0.004684     0.000000   8
```

The example image was generated with the following command line snippet.
```bash
python scripts/plot-vasp-neb.py -i <file1> <file2> -c blue green -ls solid dashed
```


## Developer Notes

* `make fmt` can be used to format the codebase. This command is run automatically by [GitHub Actions](https://docs.github.com/actions) on every pull request and push.

* Whenever you add a new dependency be sure to run `make exportenv` to update the [`environment.yml`](environment.yml). This should be done manually before a push so when CI loads the environment from file it is up to date.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

import os
import sys
import pprint
import pandas
import numpy as np
import scipy.stats as st
import re

# include generic plotting
sys.path.append("..")
from GenericPlotting import *

FREQUENCIES = [10**-5, 10**-4, 10**-3, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
FREQUENCIES_STR = ['0.001', '0.01', '0.1', '1', '5', '10', '25', '50', '100']
PTO_SIZES = [8, 40, 72, 104, 136, 168, 200, 232, 244]

LS = [':', '--', '-.', ':', '--', '-.', ':', '--', '-.', ':', '--']
MARKERS = ['.', 'v', '*', 's', 'x', 'p', '+', 'D', 'p', '1', '^']

BASELINE = 930000

DATA_FOLDER = "results/encap/encap_var_size"

def parse_file(filename : str, separator : str):
    """Parse CSV data in `filename` using `separator` to split columns."""

    f = open(filename, "r")
    df = pandas.read_csv(f, sep=separator, header=None)
    f.close()

    del df[df.columns[0]]
    df.rename(columns={1: "pps", 2: "bps", 3: "ipackets", 4: "opackets"}, inplace=True)
    df['pps']/=10**5

    mean = np.mean(df["pps"])
    var = np.var(df["pps"])
    stddev = np.std(df["pps"])

    return mean, var, stddev

def extract_directory(dirPath: str) -> dict:
    "Extract all data from all files in directory `dirPath`."

    # get list of files
    files = os.listdir(dirPath)
    files = [f for f in files if f.endswith("_stats.csv")]
    files.sort()

    data = {}

    # load and parse data
    for f in files:
        mean, var, stddev = parse_file(os.path.join(dirPath, f), ";")

        ioamFreq = re.search(r'ioam_\d+', f).group(0)
        ioamFreq = re.search(r'\d+', ioamFreq).group(0)
        mtuFreq = re.search(r'mtu_\d+', f).group(0)
        mtuFreq = re.search(r'\d+', mtuFreq).group(0)
        freq = int(ioamFreq) / float(int(ioamFreq) + int(mtuFreq))

        ptoSize = re.search(r"size_\d+", f).group(0)
        ptoSize = int(re.search(r"\d+", ptoSize).group(0))

        data[f] = (ptoSize, freq, mean, var, stddev)

    return data

def build_dataframe(data: dict) -> pandas.DataFrame:
    """Build dataframe from dictionary `data`."""

    df = pandas.DataFrame(0.0, index=FREQUENCIES_STR, columns=PTO_SIZES)
    inter = pandas.DataFrame(0.0, index=FREQUENCIES_STR, columns=PTO_SIZES)

    for d in data:
        ptoSize, freq, mean, var, stddev = data[d]
        x = FREQUENCIES.index(freq)
        y = PTO_SIZES.index(ptoSize)
        inter.iat[x,y] = stddev
        df.iat[x, y] = mean

    return df, inter

def plot(df: pandas.DataFrame, inter: pandas.DataFrame, plotFile: str):
    """Plot data stored inside `df` and store plot in `plotFile`."""

    ylim = [0, 14]
    legendPos = "lower left"

    df.columns = [str(col_name*4)+'B' for col_name in df.columns]

    p = GenericPlot()
    dict_line = {
        'xlabel':'Injection rate (in \%)',
        'ylabel': r'pps received ($10^5$)',
        'yerr': inter.transpose().values,
        'marker': MARKERS,
        'marker_size': 3,
        'my_ls': LS,
        'legend': PTO_SIZES,
        'position_legend': legendPos,
        'grid':True,
        'columns': df.columns,
        'linewidth': 1,
        'y_lim': [0, 10],
    }

    fig, ax = p.generic_plot(Plot.LINE_PLOT_CI, df, dict_parameters=dict_line)
    ax.hlines(BASELINE/10**5, 0, 8, linestyles='solid', linewidth=1, colors=['red'], label='Baseline')
    plt.legend(ncol=4, loc=legendPos, bbox_to_anchor=[0, 0])

    ax.set_xticks(ticks=range(len(FREQUENCIES_STR)), labels=FREQUENCIES_STR, horizontalalignment='center')

    ax.set_yticks(range(0, 11, 2))
    ax.set_ylim([0, 10])

    fig.set_figheight(3)
    fig.set_figwidth(6)

    fig.savefig(plotFile, bbox_inches='tight')

if __name__ == "__main__":
    data = extract_directory(DATA_FOLDER)

    df, inter = build_dataframe(data)
    df.to_csv("encap_pto_size.csv")
    pprint.pprint(df)

    plot(df, inter, "encap_pto_size.pdf")

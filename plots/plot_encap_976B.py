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
PTO_SIZE = 8
COLUMNS = ["Vanilla", "AES", "ChaCha"]

LS = ['-', '-', '-']
MARKERS = ['.', 'v', '*']

BASELINE = 930000

FOLDER = "results/encap/encap_max_size"

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

        security = re.search(r'security_[a-zA-Z]+', f).group(0)
        security = True if "True" in security else False

        chacha = re.search(r'chacha_[a-zA-Z]+', f).group(0)
        chacha = True if "True" in chacha else False

        data[f] = (security, chacha, freq, mean, var, stddev)

    return data

def build_dataframe(data: dict) -> pandas.DataFrame:
    """Build dataframe from dictionary `data`."""

    df = pandas.DataFrame(0.0, index=FREQUENCIES_STR, columns=COLUMNS)
    inter = pandas.DataFrame(0.0, index=FREQUENCIES_STR, columns=COLUMNS)

    for d in data:
        security, chacha, freq, mean, var, stddev = data[d]
        x = FREQUENCIES.index(freq)
        y = 0 if not security else (1 if not chacha else 2)
        inter.iat[x,y] = stddev
        df.iat[x, y] = mean

    return df, inter

def plot(df: pandas.DataFrame, inter: pandas.DataFrame, plotFile: str):
    """Plot data stored inside `df` and store plot in `plotFile`."""

    legendPos = "lower left"
    p = GenericPlot()
    dict_line = {
        'xlabel':'Injection rate (in \%)',
        'ylabel': r'pps received ($10^5$)',
        'marker': MARKERS,
        'marker_size': 3,
        'my_ls': LS,
        'position_legend': legendPos,
        'grid':True,
        'linewidth': 1,
        'y_lim': [0, 10],
        'dpoints': True
    }

    fig, ax = p.generic_plot(Plot.LINE_PLOT, df, dict_parameters=dict_line)
    ax.hlines(BASELINE/10**5, 0, 8, linestyles='solid', linewidth=1, colors=['red'], label='Baseline')
    plt.legend(ncol=4, loc=legendPos, bbox_to_anchor=[0, 0])

    ax.set_xticks(ticks=range(len(FREQUENCIES_STR)), labels=FREQUENCIES_STR, horizontalalignment='center')

    ax.set_yticks(range(0, 11, 2))
    ax.set_ylim([0, 10])

    fig.set_figheight(3)
    fig.set_figwidth(6)

    fig.savefig(plotFile, bbox_inches='tight')

if __name__ == "__main__":
    data = extract_directory(FOLDER)

    df, inter = build_dataframe(data)
    df.to_csv("encap_976B.csv")
    pprint.pprint(df)

    plot(df, inter, "encap_976B.pdf")

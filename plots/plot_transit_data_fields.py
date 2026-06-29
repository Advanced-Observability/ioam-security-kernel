import os
import sys
import pprint
import pandas
import numpy as np
import scipy.stats as st
import re

# include generic plotting
sys.path.append("../")
from GenericPlotting import *

FREQUENCIES = [10**-5, 10**-4, 10**-3, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
FREQUENCIES_STR = ['0.001', '0.01', '0.1', '1', '5', '10', '25', '50', '100']

OPTIONS = [4, 8, 16, 24, 32, 48]

# for plots
LS = ['-','-','-','-','-','-','-','-','-']
MARKERS = ['.', 'v', '*', 's', 'x', 'p', '+', 'D', 'p', '1', '^']

BASELINE = 930000

DATA = "results/transit/transit_aes"

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

def parse_data_fields(folder: str):
    """Parse data"""

    # get list of files
    files = os.listdir(folder)
    files = [f for f in files if f.endswith(".csv")]
    files.sort()

    data = {}

    # load and parse data
    for f in files:
        # parse given file
        mean, var, stddev = parse_file(os.path.join(folder, f), ";")

        # commpute percentage of ioam packets from filename
        percentages = re.search(r'\d+_\d+.csv', f).group(0)
        percentages = re.search(r'\d+_\d+', percentages).group(0).split("_")
        freq = float(percentages[1]) / float((int(percentages[0]) + int(percentages[1])))

        # extract node data size
        option = re.search(r"INLINE_\d+B", f).group(0)
        option = re.search(r"\d+", option).group(0)

        # copy parsed data
        data[f] = (int(option), freq, mean, var, stddev)

    # convert data to dataframes
    df = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=OPTIONS)
    inter = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=OPTIONS)

    for d in data:
        option, freq, mean, var, stddev = data[d]
        x = FREQUENCIES.index(freq)
        y = OPTIONS.index(option)
        df.iat[x, y] = mean
        inter.iat[x, y] = stddev

    return df, inter

def plot(df: pd.DataFrame, inter: pd.DataFrame, plotFile: str):
    """Plot for different IOAM data fields."""

    df.columns = [str(col_name)+'B' for col_name in df.columns]

    legendPos = "lower left"
    p = GenericPlot()
    dict_line = {
        'xlabel':'Injection rate (in \%)',
        'ylabel': r'pps received ($10^5$)',
        'marker': MARKERS,
        'marker_size': 3,
        'my_ls': LS,
        'legend': OPTIONS,
        'position_legend': legendPos,
        'grid':True,
        'columns': df.columns,
        'linewidth': 1,
        'y_lim': [0, 10],
        'dpoints': True
    }

    fig, ax = p.generic_plot(Plot.LINE_PLOT, df, dict_parameters=dict_line)
    ax.hlines(BASELINE/10**5, 0, 8, linestyles='solid', linewidth=1, colors=['red'], label='Baseline')
    plt.legend(ncol=2, loc=legendPos, bbox_to_anchor=[0, 0])

    ax.set_xticks(ticks=range(len(FREQUENCIES_STR)), labels=FREQUENCIES_STR, horizontalalignment='center')

    ax.set_yticks(range(0, 11, 2))
    ax.set_ylim([0, 10])

    fig.set_figheight(3)
    fig.set_figwidth(6)

    fig.savefig(plotFile, bbox_inches='tight')

if __name__ == "__main__":
    data, intervals = parse_data_fields(DATA)
    pprint.pprint(data)
    plot(data, intervals, "transit_data_fields.pdf")
    data.to_csv("transit_data_fields.csv", sep=";")

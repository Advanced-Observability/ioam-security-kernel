import os
import sys
import pandas
import numpy as np
import scipy.stats as st
import re
import pprint

# include generic plotting
sys.path.append("..")
from GenericPlotting import *

FREQUENCIES = [10**-5, 10**-4, 10**-3, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
FREQUENCIES_STR = ['0.001', '0.01', '0.1', '1', '5', '10', '25', '50', '100']

OPTIONS = [0, 1, 2, 3, 5, 6, 8, 9, 10]

# for plots
LS = ['-', '-', '-', '-', '--', '-.', ':', '--', '-.', ':', '--']
MARKERS = ['.', 'v', '*', 's', 'x', 'p', '+', 'D', 'p', '1', '^']

BASELINE = 930000

NO_SEC = "results/transit/transit_max_size/no_sec"
AES = "results/transit/transit_max_size/aes"
CHACHA = "results/transit/transit_max_size/chacha"

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

    # 95% confidence interval student-t on mean
    #interval = st.t.interval(0.95, df=len(df["pps"])-1, loc=np.mean(df["pps"]), scale=st.sem(df["pps"]))

    #return mean, var, stddev, interval
    return mean, var, stddev

def parse_data(folder : str):
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

        # copy parsed data
        data[f] = (freq, mean, var, stddev)

    # convert data to dataframes
    df = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=["PPS"])
    inter = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=["PPS"])

    for d in data:
        freq, mean, var, stddev = data[d]
        x = FREQUENCIES.index(freq)
        df.iat[x, 0] = mean
        inter.iat[x, 0] = std

    return df, inter

def plot(df: pd.DataFrame, plotFile: str):
    """Plot."""

    legendPos = "lower left"
    p = GenericPlot()
    dict_line = {
        'xlabel':'Injection rate (in \%)',
        'ylabel': r'pps received ($10^5$)',
        'marker': MARKERS,
        'marker_size': 3,
        'my_ls': LS,
        'legend': OPTIONS, 'position_legend': legendPos,
        'grid':True,
        'linewidth': 1,
        'y_lim': [0, 10],
        'dpoints': True
    }

    fig, ax = p.generic_plot(Plot.LINE_PLOT_CI, df, dict_parameters=dict_line)
    ax.hlines(BASELINE/10**5, 0, len(FREQUENCIES)-1, linestyles='solid', linewidth=1, colors=['red'], label='Baseline')
    plt.legend(ncol=2, loc=legendPos, bbox_to_anchor=[0, 0])

    ax.set_xticks(ticks=range(len(FREQUENCIES_STR)), labels=FREQUENCIES_STR, horizontalalignment='center')

    ax.set_yticks(range(0, 11, 2))
    ax.set_ylim([0, 10])

    fig.set_figheight(3)
    fig.set_figwidth(6)

    fig.savefig(plotFile, bbox_inches='tight')

if __name__ == "__main__":
    print("\n~ NO SEC ~")
    nosec, _ = parse_data(NO_SEC)
    pprint.pprint(nosec)

    print("\n~ AES ~")
    aes, _ = parse_data(AES)
    pprint.pprint(aes)

    print("\n~ CHACHA ~")
    chacha, _ = parse_data(CHACHA)
    pprint.pprint(chacha)

    print("\n~ Combined ~")
    combined = nosec
    combined.rename(columns={'PPS':'No Security'}, inplace=True)
    combined["AES-GCM"] = aes["PPS"]
    combined["ChaCha20-Poly1305"] = chacha["PPS"]
    combined.to_csv("transit_48B.csv", sep=";")
    pprint.pprint(combined)

    plot(combined, "transit_48B.pdf")

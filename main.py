import os
import time

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn import metrics

import scipy.stats
import numpy as np
import pandas as pd 
import matplotlib
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.axes as ax

matplotlib.get_cachedir()  # allow matplotlib to access font cache

# start the timer
FILENAME = Path(__file__).name
STARTTIME = time.time()

# global vars
DATAPATH = "./data/"
SEASON_STRS = sorted(list(set(next(os.walk(DATAPATH))[1])))
SEASON_LENGTH = 38
MIN_MINS = 1
SELECTED_COLS = ["total_points"]
POSITION_LIST = [None, 1, 2, 3, 4]
LM = LinearRegression()


def add_position_column(df, season):
    """ add a column to a dataframe with each player's position """
    path = DATAPATH + season + "/players_raw.csv"
    pos = pd.read_csv(path)[["id", "element_type"]]
    df["position"] = df["element"].map(pos.set_index("id")["element_type"])
    return df


def calc_corrs(season, position=None, pearson=True):
    """ 
    calculate correlation coefficient between value and any number of other 
    columns in the dataframe

    set position to an integer to select only players from a certain position
    goalkeepers - 1
    defenders   - 2
    midfielders - 3
    forwards    - 4

    set pearson to True to use the pearson correlation
    coefficient, set to False to use spearman ranked correlation
    """
    path = DATAPATH + season + "/gws/"
    df = pd.DataFrame(columns=["gw"]+SELECTED_COLS)

    for i in range(SEASON_LENGTH):
        try:
            # read in the csv for this gameweek
            csv_path = path + f"gw{i + 1}.csv"
            tmp_df = pd.read_csv(csv_path, encoding="ISO-8859-1")

            # remove players who played less than MIN_MINS
            tmp_df = tmp_df.drop(tmp_df[tmp_df["minutes"]<MIN_MINS].index)
            tmp_df = add_position_column(tmp_df, season)

            if position is not None:
                tmp_df = tmp_df[tmp_df["position"] == position]

            print(tmp_df["position"])

            # check that the csv contains data
            if tmp_df.shape[0] > 0:
                price = tmp_df["selected"]
                row_data = [i + 1]
                for c in SELECTED_COLS:
                    col = tmp_df[c]

                    # calculate correlation coef between price and col and 
                    # append this rho value to the row data
                    if pearson:
                        row_data.append(scipy.stats.pearsonr(price, col)[0])
                    else:
                        row_data.append(scipy.stats.spearmanr(price, col)[0])

                # add the row data to the dataframe
                row = pd.DataFrame([row_data], columns=["gw"]+SELECTED_COLS)
                df = df.append([row], ignore_index=True)

            # if no data in the csv
            else:
                pass

        # if no file exists (ie GW 31 of this year), pass
        except FileNotFoundError:
            pass

    return df


def make_corr_plots(position=None, pearson=True, scatter_scale=4, line_scale=3):
    """ produce plots of correlation between price and total points """

    # to be used in the plot title
    if position is None:
        pos_str = "All"
    elif position == 1:
        pos_str = "Goalkeepers"
    elif position == 2:
        pos_str = "Defenders"
    elif position == 3:
        pos_str = "Midfielders"
    else:
        pos_str = "Forwards"

    # for y axis label, plot directory
    if pearson:
        corrname = "Pearson correlation coefficient"
        plot_dir = os.path.join(".", "pearson", pos_str.lower())
    else:
        corrname = "Spearman ranked correlation coefficient"
        plot_dir = os.path.join(".", "spearman", pos_str.lower())

    # create a directory for the plots, if necessary
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    # iterate the plotting process over seasons
    for s in SEASON_STRS:
        df = calc_corrs(s, position, pearson=pearson)

        # convert columns to numpy arrays
        x = df["gw"].values.reshape(-1, 1)
        y = df["total_points"].values.reshape(-1, 1)

        # calculate the fit with sklearn.LinearRegression()
        fit = LM.fit(x, y)
        preds = fit.predict(x)
        r_sq = round(metrics.r2_score(y, preds), 4)

        # create figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        # scatter plot, linear regression
        plt.scatter(x, y, color="purple", s=scatter_scale)
        plt.plot(x, preds, color="orange", linewidth=line_scale)
        plt.text(0.025, 0.925, f"R Squared = {r_sq}",
                bbox=dict(facecolor='blue', alpha=0.2),
                transform=ax.transAxes)

        # plot labels
        plt.ylabel(f"{corrname} between price and points")
        plt.xlabel("Gameweek")
        plt.title(s + f": {pos_str}")

        # save the plot
        plt.savefig(f"{plot_dir}/fit_{s}_{pos_str.lower()}.png")


for p in POSITION_LIST:
    make_corr_plots(p, True)
    make_corr_plots(p, False)




# keep track of how long this takes to run
EXECTIME = round(time.time() - STARTTIME, 2)
print(f"{FILENAME} finished in {EXECTIME} seconds")

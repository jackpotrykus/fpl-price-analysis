import os
import time

import numpy as np
from numpy.linalg import norm
import pandas as pd

def add_position_col(df, season):
    """ 
    add a column to a dataframe with each player's position
    """
    path = os.path.join(".", "data", season, "players_raw.csv")
    pos = pd.read_csv(path)[["id", "element_type"]]
    df["position"] = df["element"].map(pos.set_index("id")["element_type"])
    return df


def james_stein_est(lst):
    """
    for a list of players' points per game through a certain number of games,
    create a list of james-stein estimates of their points per game for the
    whoel season
    """
    vs = [np.mean(lst) for i in range(len(lst))]
    diffs = [z - v for z, v in zip(lst, vs)]

    shrinkage = 1 - ((len(lst) - 3) * np.std(lst) ** 2 / (np.linalg.norm(diffs) ** 2))
    if shrinkage < 0:
        shrinkage = 0

    ests = [shrinkage * d + v for d, v in zip(diffs, vs)]
    return ests, shrinkage


def grab_gws(season, up_to_gw):
    """
    get the points per minute of every player, averaged over the first up_to_gw
    gameweeks
    """
    path = os.path.join(".", "data", season, "gws")
    pdict = dict()

    for i in range(up_to_gw):
        # read in csv for this gameweek
        csv_path = os.path.join(path, f"gw{i+1}.csv")
        tmp = pd.read_csv(csv_path, encoding="ISO-8859-1")

        if season not in ["2016-17", "2017-18"]:
            names = [n[:n.rfind("_")] for n in tmp["name"]]
        else:
            names = tmp["name"]

        for index, name in enumerate(names):
            row = tmp.iloc[index]
            if row["minutes"] == 0 or name not in pdict.keys() and i > 0:
                pass
            elif name not in pdict.keys():
                pdict[name] = {"mins": row["minutes"],
                        "pts": row["total_points"]}
            else:
                pdict[name]["mins"] += row["minutes"]
                pdict[name]["pts"] += row["total_points"]

    ppgs = [v["pts"] / v["mins"] for v in pdict.values()]
    ppgs_js = james_stein_est(ppgs)
    ppg_dict = {n: p for n, p in zip(pdict.keys(), ppgs)}
    ppg_dict_js = {n: p for n, p in zip(pdict.keys(), ppgs_js[0])}
    return ppg_dict, ppg_dict_js, ppgs_js[1]


def total_sq_loss(ests, true):
    """
    ests and true are dictionaries (so that player names can be matched)
    """
    loss = 0
    for k in ests.keys():
        loss += (ests[k] - true[k]) ** 2
    
    return loss


def loss_by_gw(season):
    """
    produce a dataframe comparing the loss of james-stein estimates and mle
    estimates for each week
    """
    true = grab_gws(season, 38)[0]
    loss = []
    loss_js = []
    shrinkage = []
    for i in range(38):
        print(i)

        grab = grab_gws(season, i + 1)
        loss.append(total_sq_loss(grab[0], true))
        loss_js.append(total_sq_loss(grab[1], true))
        shrinkage.append(grab[2])

    df = pd.DataFrame(list(zip(loss, loss_js, shrinkage)),
            columns = ["mle", "js", "shrinkage"])

    return df


loss_over_gws = loss_by_gw("2016-17")
print(loss_over_gws)

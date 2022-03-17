import os
import sys
import networkx as nx
import pandas as pd
import pickle
import pageRank
import datetime
from pageRank import pagerank

if __name__ == "__main__":
    sdf = pd.read_csv("mmscores.csv")

    df = sdf.copy()
    df["winnerScore"] = 0
    df["loserScore"] = 0
    df["winnerTeam"] = None
    df["loserTeam"] = None
    df["tie"] = False
    for idx, ser in df.iterrows():
        if ser["Score1"] > ser["Score2"]:
            df.at[idx, "winnerTeam"] = ser["Team1"]
            df.at[idx, "loserTeam"] = ser["Team2"]
            df.at[idx, "winnerScore"] = ser["Score1"]
            df.at[idx, "loserScore"] = ser["Score2"]
        elif ser["Score1"] < ser["Score2"]:
            df.at[idx, "winnerTeam"] = ser["Team2"]
            df.at[idx, "loserTeam"] = ser["Team1"]
            df.at[idx, "winnerScore"] = ser["Score2"]
            df.at[idx, "loserScore"] = ser["Score1"]
        else:
            df.at[idx, "tie"] = True

    all_teams = list(set(df.Team1.unique()).union(df.Team2.unique()))

    wins = pd.DataFrame(df.winnerTeam.value_counts())
    losses = pd.DataFrame(df.loserTeam.value_counts())
    ties1 = pd.DataFrame(df.loc[df["tie"]].Team1.value_counts())
    ties2 = pd.DataFrame(df.loc[df["tie"]].Team2.value_counts())
    wldf = wins.join(losses)

    ties = ties1.join(ties2)
    ties["cnt"] = ties.sum(axis=1)
    ties.drop(columns=["Team1", "Team2"], inplace=True)
    wldf = wldf.join(ties)
    wldf.reset_index(inplace=True)

    wldf.columns = ["team", "wins", "losses", "ties", ]
    wldf.fillna(0, inplace=True)
    wldf["games"] = wldf[["wins", "losses", "ties"]].sum(axis=1)
    wldf.sort_values(by="wins", inplace=True)

    realdf = wldf.loc[wldf["games"] > 20].copy()
    realdf.sort_values(by="wins", inplace=True, ascending=False)

    realteams = realdf["team"].values
    print(realdf.shape)
    DG = nx.DiGraph()
    #sqdf = pd.DataFrame(columns=realteams, index=realteams)
    for idx, ser in df.iterrows():
        if ser["winnerTeam"] in realteams and ser["loserTeam"] in realteams:
            margin = ser["winnerScore"] - ser["loserScore"]
            DG.add_edge(u_of_edge=ser["winnerTeam"], v_of_edge=ser["loserTeam"], weight=margin)
            #sqdf.at[ser["winnerTeam"], ser["loserTeam"]] = ser["winnerScore"] - ser["loserScore"]
            #sqdf.at[ser["loserTeam"], ser["winnerTeam"]] = ser["loserScore"] - ser["winnerScore"]
    nx.write_gpickle(DG, "mm.pickle")

    pg = pageRank.pagerank(DG, max_iter=500, weight='weight')
    with open('pgres.pickle', 'wb') as handle:
        pickle.dump(pg, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Done")

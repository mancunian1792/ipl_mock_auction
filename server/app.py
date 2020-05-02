from flask import Flask, jsonify
from flask import request
import pandas as pd
from pulp import lpSum, LpVariable, LpProblem, LpMaximize
import re
import os
app = Flask(__name__)
FILES_LOCATION = "./server/files/"

###################################################### Utility functions #####################################################3


def filter_lp_dicts(players_lp, criteria_list):
    filter_dict = {}
    for player in criteria_list:
        filter_dict[player] = players_lp[player]
    return filter_dict

def constructLpSumArr(dict_lp):
    lp_arr = []
    for k,_ in dict_lp.items():
        lp_arr += lpSum(dict_lp[k])
    return lp_arr

def summary(prob):
    chosen_players = []
    score = str(prob.objective)
    constraints = [str(const) for const in prob.constraints.values()]
    for v in prob.variables():
        score = score.replace(v.name, str(v.varValue))
        constraints = [const.replace(v.name, str(v.varValue)) for const in constraints]
        if v.varValue != 0:
            chosen_players.append(v.name)
    for constraint in constraints:
        constraint_pretty = " + ".join(re.findall("[0-9\.]*\*1.0", constraint))
        if constraint_pretty!="":
            total_cost = eval(constraint_pretty)
    score_pretty = " + ".join(re.findall("[0-9\.]+\*1.0", score))
    total_rating = eval(score_pretty)
    return {
       "team": chosen_players,
       "total_cost": total_cost,
       "total_rating": total_rating 
    }
################################################################################################################################

@app.route("/")
def home():
    return "Welcome to the Auction Service.We provide the optimal 11."

@app.route("/remove-player/", methods=["GET"])
def remove_player_from_list():
    if 'player-name' in request.args:
        name = request.args['player-name']
        # Check if there's a file named removed-players else create the file
        if 'removed_players.csv' not in os.listdir(FILES_LOCATION):
            df = pd.DataFrame({"player_name": [name]})
            df.to_csv("./server/files/removed_players.csv", index=False)
        else:
            # Update the list
            df = pd.read_csv(".server/files/removed_players.csv")
            players = list(df["player_name"])
            players.append(name)
            df.to_csv("./server/files/removed_players.csv", index=False)
        return "Player Deleted"
    return "No Player to delete"


@app.route("/optimal11/", methods=["POST"])
def get_optimal11():
    # Read in the player list
    # Remove the players from removed list if file exists.
    # Form all the neccessary variables
    # Construct the optimization problem by reading the constraints from request.
    # Return the top players , rating of the team and the total cost of the team
    args = request.get_json()
    all_players = pd.read_csv("./server/files/all_players.csv")
    all_players = list(all_players["player_name"].values)
    print(all_players)
    removed_players = []
    if 'removed_players.csv' in os.listdir(FILES_LOCATION):
        removed_players = pd.read_csv("./server/files/removed_players.csv")
        removed_players = list(removed_players["player_name"].values)
    updated_players = [x for x in all_players if x not in removed_players]
    print(updated_players)

    data = pd.read_csv("./server/files/IPL-aggregated-stats_final.csv")
    data = data[data.PLAYER.isin(updated_players)]
    indians = list(data[data["overseas_or_indian"]=="Indian"]["PLAYER"])
    overseas = list(data[data["overseas_or_indian"]=="Overseas"]["PLAYER"])
    batsman = list(data[data.position=="BAT"]["PLAYER"])
    bowlers = list(data[data.position=="BWL"]["PLAYER"])
    allrounders = list(data[data.position=="AR"]["PLAYER"])
    wks = list(data[data.position=="WK"]["PLAYER"])
    median_ratings = dict(zip(updated_players, list(data["median_season_ratings"])))
    base_prices = dict(zip(updated_players, list(data["base_price"])))

    players_lp = LpVariable.dicts("Chosen",updated_players,0,1,cat='Integer')
    batsman_lp = filter_lp_dicts(players_lp, batsman)
    bowlers_lp = filter_lp_dicts(players_lp, bowlers)
    ar_lp = filter_lp_dicts(players_lp, allrounders)
    wk_lp = filter_lp_dicts(players_lp, wks)
    indians_lp = filter_lp_dicts(players_lp, indians)
    overseas_lp = filter_lp_dicts(players_lp, overseas)

    ## Parsing request args 
    
    max_available_cost = float(args["max_available_cost"])
    wk_needed = int(args["wk_needed"])
    total_players = int(args["total_players"])
    min_bat = int(args["min_bat"])
    max_bat = int(args["max_bat"])
    min_bowl = int(args["min_bowl"])
    max_bowl = int(args["max_bowl"])
    min_ar = int(args["min_ar"])
    max_ar = int(args["max_ar"])
    ind_needed = int(args["ind_needed"])
    ovr_needed = int(args["ovr_needed"])

    ### Construct Binary Integer Optimization problem
    prob = LpProblem("IPL_Auction", LpMaximize)
    rewards = []
    costs = []
    for k, _ in players_lp.items():
        costs += lpSum(base_prices[k] * players_lp[k])
        rewards += lpSum(median_ratings[k] * players_lp[k])
    prob+= lpSum(rewards)
    prob += lpSum(costs) <= max_available_cost
    prob += lpSum(constructLpSumArr(wk_lp)) == wk_needed
    prob += lpSum(constructLpSumArr(players_lp)) == total_players
    prob += lpSum(constructLpSumArr(batsman_lp)) >= min_bat
    prob += lpSum(constructLpSumArr(batsman_lp)) <= max_bat
    prob += lpSum(constructLpSumArr(bowlers_lp)) >= min_bowl
    prob += lpSum(constructLpSumArr(bowlers_lp))<= max_bowl
    prob += lpSum(constructLpSumArr(ar_lp)) >= min_ar
    prob += lpSum(constructLpSumArr(ar_lp)) <= max_ar
    prob += lpSum(constructLpSumArr(indians_lp)) == ind_needed
    prob += lpSum(constructLpSumArr(overseas_lp)) == ovr_needed

    prob.solve()

    return jsonify(summary(prob))


if __name__ == "__main__":
    app.run(debug=True)
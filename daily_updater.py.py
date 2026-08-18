import json
import os
import requests
from datetime import datetime

# Paths to data stores
NAT_TEAMS_FILE = os.path.join("data", "national_teams.json")
CLUB_TEAMS_FILE = os.path.join("data", "club_teams.json")

def calculate_sum_points(p_a: float, p_b: float, w_a: float, w_b: float, i_weight: float, is_knockout: bool = False):
    """
    FIFA SUM Formula Implementation:
    P = P_before + I * (W - W_e)
    W_e = 1 / (10 ** (-(P_A - P_B) / 600) + 1)
    """
    dr = p_a - p_b
    w_e_a = 1.0 / (10.0 ** (-dr / 600.0) + 1.0)
    w_e_b = 1.0 - w_e_a

    delta_a = i_weight * (w_a - w_e_a)
    delta_b = i_weight * (w_b - w_e_b)

    # Knockout stage protection: point loss capped at 0
    if is_knockout:
        if delta_a < 0:
            delta_a = 0.0
        if delta_b < 0:
            delta_b = 0.0

    return delta_a, delta_b, w_e_a, w_e_b

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_daily_matches():
    date_str = datetime.now().strftime("%Y%m%d")
    url = f"https://www.fotmob.com/api/matches?date={date_str}"
    
    print(f"Executing daily ranking sync for {date_str}...")

    teams = load_json(NAT_TEAMS_FILE)
    if not teams:
        print("No national teams found in storage. Skipping API sync.")
        return

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            updated_count = 0
            
            for league in data.get("leagues", []):
                for match in league.get("matches", []):
                    if match.get("status", {}).get("finished"):
                        home_name = match["home"]["name"]
                        away_name = match["away"]["name"]

                        team_a = next((t for t in teams if t["name"].lower() == home_name.lower() or t["id"].lower() == home_name.lower()), None)
                        team_b = next((t for t in teams if t["name"].lower() == away_name.lower() or t["id"].lower() == away_name.lower()), None)

                        if team_a and team_b:
                            score_a = match["home"]["score"]
                            score_b = match["away"]["score"]

                            if score_a > score_b:
                                w_a, w_b = 1.0, 0.0
                            elif score_b > score_a:
                                w_a, w_b = 0.0, 1.0
                            else:
                                w_a, w_b = 0.5, 0.5

                            delta_a, delta_b, _, _ = calculate_sum_points(
                                team_a["points"], team_b["points"], w_a, w_b, i_weight=25.0
                            )

                            team_a["points"] = round(team_a["points"] + delta_a, 2)
                            team_b["points"] = round(team_b["points"] + delta_b, 2)
                            
                            team_a.setdefault("history", []).append(team_a["points"])
                            team_b.setdefault("history", []).append(team_b["points"])
                            updated_count += 1

            if updated_count > 0:
                save_json(NAT_TEAMS_FILE, teams)
                print(f"Successfully processed {updated_count} match(es) and saved updated rankings.")
            else:
                print("No matches matched the current database teams today.")
        else:
            print(f"FotMob API returned status {response.status_code}")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    sync_daily_matches()
import csv
import os

def process_veto_data(csv_file, team_name):
    veto_data = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            veto_data.append(eval(row[1]))

    map_types = {
        'Control': ['Lijiang Tower', 'Nepal', 'Samoa', 'Ilios'],
        'Hybrid': ['King\'s Row', 'Blizzard World', 'Midtown', 'Hollywood'],
        'Push': ['Colosseo', 'New Queen Street', 'Esperança'],
        'Flashpoint': ['Suravasa', 'New Junk City'],
        'Escort': ['Dorado', 'Circuit Royal', 'Shambali Monastery', 'Rialto']
    }

    team_preferences = {map_type: {map_name: 0 for map_name in maps} for map_type, maps in map_types.items()}
    map_type_decisions = {map_type: 0 for map_type in map_types}

    weight = -0.1
    for match_data in veto_data:
        current_map_type = None
        map_type_bans = 0
        weight += 0.1
        for ban_or_pick in match_data:
            if 'banned' in ban_or_pick:
                team, map_name = ban_or_pick.split(' banned ')
                team = team.split('. ')[1]
                if team == team_name:
                    for map_type, maps in map_types.items():
                        if map_name in maps:
                            current_map_type = map_type
                            map_type_bans += 1
                            if map_type_bans < len(maps):
                                team_preferences[map_type][map_name] -= (1 - max(weight, 0))
                                map_type_decisions[map_type] += 1
                            break
                else:
                    if current_map_type:
                        map_type_bans += 1
                        if map_type_bans == len(map_types[current_map_type]):
                            current_map_type = None
                            map_type_bans = 0
            elif 'picked by' in ban_or_pick:
                map_name, team = ban_or_pick.split(' picked by ')
                map_name = map_name.split('. ')[1]
                if team == team_name:
                    for map_type, maps in map_types.items():
                        if map_name in maps:
                            team_preferences[map_type][map_name] += (1 - max(weight, 0))
                            map_type_decisions[map_type] += 1
                            break

    # Normalize the scores based on the total number of decisions for each map type
    for map_type, preferences in team_preferences.items():
        total_decisions = map_type_decisions[map_type]
        if total_decisions > 0:
            for map_name in preferences:
                team_preferences[map_type][map_name] /= total_decisions

    return team_preferences

# Get the script directory
script_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the relative path to the CSV file from the script directory
csv_directory = 'output'
csv_file = 'processed_rows.csv'
file_path = os.path.join(script_directory, csv_directory, csv_file)

# Example usage
team_name = 'Team Peps'
team_preferences = process_veto_data(file_path, team_name)

for map_type, preferences in team_preferences.items():
    sorted_preferences = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
    preference_string = f"{map_type}: " + " > ".join([f"{map_name} ({round(score * 5, 3)})" for map_name, score in sorted_preferences])
    print(preference_string)
    print()
import csv
import os

# AI generated slop to create some arbitrary values for how much a team prefers a certain map.
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

    # Arbitrary weight value to prioritize recent vetoes. A veto will be worth 50% by the 10th match.
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
                                team_preferences[map_type][map_name] += (1 - max(weight, 0))
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
                print(map_name)
                if team == team_name:
                    for map_type, maps in map_types.items():
                        if map_name in maps:
                            team_preferences[map_type][map_name] -= (1 - max(weight, 0))
                            break
    

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
    print(f"Map Type: {map_type}")
    for map_name, score in preferences.items():
        rounded_score = round(score, 1)
        print(f"  {map_name}: {rounded_score}")
    print()
'''
Get Season Minutes Function
Komdean Masoumi
'''

import pandas as pd


def get_mins(df):
    # create data frame for minutes played
    minutes_played = df[(df['type.name'].isin(['Starting XI', 'Half End', 'Substitution'])) |
                        (df['foul_committed.card.name'].isin(['Red Card' or 'Second Yellow']))]

    # create new column with minutes and seconds
    minutes_played['timestamp'] = minutes_played['timestamp'].astype(str).str.split().str[1]
    minutes_played['timestamp'] = pd.to_timedelta(minutes_played['timestamp'])

    # Clean and sort 'minutes_played'
    minutes_played.dropna(axis=1, inplace=True, how='all')
    minutes_played = minutes_played.sort_values(by=['match_id', 'period', 'timestamp'])

    # Get list of all matches_ids
    match_ids = list(set(minutes_played['match_id']))

    # Create Dataframe for subs
    substitutions = minutes_played[minutes_played['type.name'] == 'Substitutions']

    # Create Dataframe for red cards
    red_cards = minutes_played[minutes_played['foul_committed.card.name'].isin(['Red Card' or 'Second Yellow'])]

    # Create an empty DataFrame for all matches and minutes played
    minutes_df = pd.DataFrame(columns=['player.id', 'playtime', 'match_id'])

    # Get minutes played per player by match
    for match in match_ids:
        minutes_dict = {}

        match_df = minutes_played[minutes_played['match_id'] == match]

        period_1 = match_df[(match_df['type.name'] == 'Half End') & (match_df['period'] == 1)].iloc[0]['timestamp']
        period_2 = match_df[(match_df['type.name'] == 'Half End') & (match_df['period'] == 2)].iloc[0]['timestamp']
        total_game_time = period_1 + period_2

        # Get the initial lineup
        lineup = match_df[match_df['type.name'] == 'Starting XI'].iloc[0]['tactics.lineup']
        lineup2 = match_df[match_df['type.name'] == 'Starting XI'].iloc[1]['tactics.lineup']

        # Initialize player in match dictionary
        for player in lineup:
            minutes_dict[player['player.id']] = total_game_time
        for player in lineup2:
            minutes_dict[player['player.id']] = total_game_time

        # Account for substitutions
        match_subs = substitutions[substitutions['match_id'] == match]
        for i in range(len(match_subs)):
            minutes_dict[match_subs['player.id'].iloc[i]] -= total_game_time - match_subs['timestamp'].iloc[i]
            if match_subs['period'].iloc[i] == 1:
                minutes_dict[match_subs['substitution.replacement.id'].iloc[i]] = total_game_time - match_subs['timestamp'].iloc[i]
            else:
                minutes_dict[match_subs['substitution.replacement.id'].iloc[i]] = period_2 - match_subs['timestamp'].iloc[i]

        # Account for red cards
        match_reds = red_cards[red_cards['match_id'] == match]
        if match_reds.empty:
            pass
        else:
            if len(match_reds) > 1:
                for i in range(len(match_reds)):
                    if match_reds['period'].iloc[i] == 1:
                        minutes_dict[match_reds['player.id'].iloc[i]] -= total_game_time - match_reds['timestamp'].iloc[i]
                    else:
                        minutes_dict[match_reds['player.id'].iloc[i]] -= period_2 - match_reds['timestamp'].iloc[i]
            else:
                player = int(list(match_reds['player.id'])[0])
                timestamp = list(match_reds['timestamp'])[0]
                if player not in minutes_dict:
                    pass
                else:
                    minutes_dict[player] -= total_game_time - timestamp

        # Create a DataFrame for the current match
        match_mins_df = pd.DataFrame(minutes_dict.items(), columns=['player.id', 'playtime'])
        match_mins_df['match_id'] = match

        # Append the current match DataFrame to the main DataFrame
        minutes_df = pd.concat([minutes_df, match_mins_df], ignore_index=True)

    # Convert timedelta to minutes
    minutes_df['playtime_minutes'] = minutes_df['playtime'].apply(lambda x: x.total_seconds() / 60)

    # Group by player to get sum of minutes
    season_mins_df = minutes_df.groupby('player.id')['playtime_minutes'].sum().reset_index()
    season_mins_df['player.id'] = season_mins_df['player.id'].astype('int')
    season_mins_df = season_mins_df.sort_values(by='playtime_minutes', ascending=False)

    return season_mins_df

def main():
    events = pd.read_json('sb_events.json')
    minutes_df = get_mins(events)
    print(minutes_df)

if __name__ == '__main__':
    main()
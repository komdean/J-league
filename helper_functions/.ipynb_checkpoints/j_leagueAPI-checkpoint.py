'''
Physical Data Api
Komdean Masoumi
'''

import pandas as pd

class J_leagueAPI:

    def load_data(self, filename):
        self.physical_data = pd.read_json(filename)


    def get_players(self):
        players = self.physical_data['player'].unique()
        return sorted(players)

    def get_teams(self):
        teams = self.physical_data['teamName'].unique()
        return sorted(teams)

    def get_params(self):
        params = list(['Count High Acceleration',
                       'Count Medium Acceleration',
                       'Count High Deceleration',
                       'Count Medium Deceleration',
                       'Max Speed',
                       'Total Distance',
                       'Sprinting Distance',
                       'High Speed Running (HSR) Distance',
                       'High Intensity (HI) Distance'])
        return params

    def sum_metrics(self, metric):
        cols = ['teamName', 'playerid', 'metric', 'phase', 'value', 'player']
        df = self.physical_data[cols]
        df = (df[(df['metric'] == metric) &
                                   (df['phase'] == 'Session')])
        df = df.groupby(['teamName', 'playerid', 'player']).sum('value').reset_index()
        df.rename(columns={'value': metric}, inplace=True)
        return df

    def max_metrics(self, metric):
        cols = ['teamName', 'playerid', 'metric', 'phase', 'value', 'player']
        df = self.physical_data[cols]
        df = (df[(df['metric'] == 'Max Speed') &
                                     (df['phase'] == 'Session')])
        df = df.groupby(['teamName', 'playerid', 'player']).max('value').reset_index()

        # Sort and organize dataframe
        df.rename(columns={'value': metric}, inplace=True)
        return df

    def extract_local_network(self, player1=None, player2=None):

        df_lst = []

        # Create high accelerations dataframe
        high_accelerations_df = self.sum_metrics('Count High Acceleration')
        df_lst.append(high_accelerations_df)

        # Create medium accelerations dataframe
        med_accelerations_df = self.sum_metrics('Count Medium Acceleration')
        df_lst.append(med_accelerations_df)

        # Create high decelerations dataframe
        high_decel_df = self.sum_metrics('Count High Deceleration')
        df_lst.append(high_decel_df)

        # Create medium decelerations dataframe
        med_decel_df = self.sum_metrics('Count Medium Deceleration')
        df_lst.append(med_decel_df)


        # Create max speed dataframe
        max_speed_df = self.max_metrics('Max Speed')
        df_lst.append(max_speed_df)

        # create a total distance dataframe
        distance_df = self.sum_metrics('Total Distance')
        distance_df['Total Distance'] = distance_df['Total Distance'] / 1000  # Change from meters to kilometers
        df_lst.append(distance_df)


        # Create total sprinting distance dataframe
        sprinting_distance_df = self.sum_metrics('Sprinting Distance')
        sprinting_distance_df['Sprinting Distance'] = sprinting_distance_df['Sprinting Distance'] / 1000  # Change from meters to kilometers
        df_lst.append(sprinting_distance_df)

        # create a high speed running distance dataframe
        hs_distance_df = self.sum_metrics('High Speed Running (HSR) Distance')
        hs_distance_df['High Speed Running (HSR) Distance'] = hs_distance_df['High Speed Running (HSR) Distance'] / 1000  # Change from meters to kilometers
        df_lst.append(hs_distance_df)


        # create a high intenstity distance dataframe
        hi_distance_df = self.sum_metrics('High Intensity (HI) Distance')
        hi_distance_df['High Intensity (HI) Distance'] = hi_distance_df['High Intensity (HI) Distance'] / 1000 # Change from meter to km
        df_lst.append(hi_distance_df)




        # merge dataframes
        local = df_lst[0]
        for df in df_lst[1:]:
            local = pd.merge(local, df, on=['teamName', 'playerid', 'player'])


        #filter for players
        if (player1 != None) & (player2 != None):
            local = local[(local['player'] == player1) | (local['player'] == player2)]
        elif player1:
            local = local[local['player'] == player1]

        return local




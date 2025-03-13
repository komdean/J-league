'''
Komdean Masoumi
Creating functions to pull out stats from statsbomb datasets
'''
import pandas as pd
import numpy as np

def is_progressive(x, y, end_x, end_y):
    start_dist = np.sqrt((120 - x) ** 2 + (40 - y) ** 2)
    end_dist = np.sqrt((120 - end_x) ** 2 + (40 - end_y) ** 2)
    # mark that passes to own half are not progressive
    thres = 100
    if x < 60 and end_x < 60:
        thres = 30
    elif x < 60 and end_x >= 60:
        thres = 15
    elif x >= 60 and end_x >= 60:
        thres = 10
    if thres > start_dist - end_dist:
        return False
    else:
        return True

def progressive_passes(df):
    '''
    Creates Dataframe with a count of progressive passes for each player
    :param df:
    :return: dataframe
    '''
    df['x'] = df['location'].str[0]
    df['y'] = df['location'].str[1]
    df['pass_end_x'] = df['pass.end_location'].str[0]
    df['pass_end_y'] = df['pass.end_location'].str[1]
    df["is_progressive"] = df.apply(lambda row: is_progressive(row['x'],
                                                               row['y'],
                                                               row['pass_end_x'],
                                                               row['pass_end_y']), axis=1)
    df = df[(df['is_progressive'] == True) |
            (df['pass.outcome.name'].isna())]
    df.dropna(axis=1, how='all')
    pp_df = df.groupby(['player.id', 'player.name']).size().reset_index(name='progressive_passes')
    pp_df['player.id'] = pp_df['player.id'].astype('int')

    return pp_df


def main():
    df = pd.read_json('sb_events.json')
    print(progressive_passes(df))


if __name__ == '__main__':
    main()

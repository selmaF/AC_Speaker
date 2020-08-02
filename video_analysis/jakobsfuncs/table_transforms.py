def nose_as_origin(data):
    "Transform standard output coordinates to format where nose position is (0/0) coordinate"
    df_nose = (data.loc[data['part_names'] == 'nose', ['frame_count', 'x', 'y']].copy())
    df_nose.columns = ['frame_count', 'x_nose', 'y_nose']
    df = data.merge(df_nose, how='left', on='frame_count')
    df['x'] -= df['x_nose']
    df['y'] -= df['y_nose']
    df = df.drop(['x_nose','y_nose'], axis=1)
    #df.rename(columns={"x": "x_dist_to_nose", "y": "y_dist_to_nose"},inplace=True)
    return df


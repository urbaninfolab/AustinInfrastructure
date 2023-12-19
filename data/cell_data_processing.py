import pandas as pd
import geopandas as gpd

gdf = pd.read_csv('Cellular_Towers.csv')[lambda df: df['LocCounty'] == 'TRAVIS']
gpd.GeoDataFrame(
    gdf.drop(columns=['X', 'Y']),
    geometry=gpd.points_from_xy(gdf['X'], gdf['Y']),
    crs=4326,
).to_file('cell.geojson', driver='GeoJSON')

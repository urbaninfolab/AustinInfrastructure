import asyncio
import requests

import pandas as pd
import geopandas as gpd

# Set global variables
STR_DIR, STR_ALT_FUEL = './', 'alt_fuel_raw.csv'
DICT_GAS_HEADER = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': '',  # API key
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.location',
}

TUPLE_TRAVIS_ZIPS = (
    73301,
    73344,
    78617,
    78645,
    78651,
    78652,
    78653,
    78660,
    78669,
    78691,
    78701,
    78702,
    78703,
    78704,
    78705,
    78708,
    78709,
    78710,
    78711,
    78712,
    78713,
    78714,
    78715,
    78716,
    78718,
    78719,
    78720,
    78721,
    78722,
    78723,
    78724,
    78725,
    78726,
    78727,
    78728,
    78730,
    78731,
    78732,
    78733,
    78734,
    78735,
    78736,
    78738,
    78739,
    78741,
    78742,
    78744,
    78745,
    78746,
    78747,
    78748,
    78749,
    78750,
    78751,
    78752,
    78753,
    78754,
    78755,
    78756,
    78757,
    78758,
    78759,
    78760,
    78761,
    78762,
    78763,
    78764,
    78765,
    78766,
    78767,
    78768,
    78772,
    78773,
    78774,
    78778,
    78779,
    78783,
    78799,
)


async def get_gas_in(zip: int):
    '''
    Request gas stations in a given zip code from Google Places API.
    '''
    res = requests.post(
        'https://places.googleapis.com/v1/places:searchText',
        headers=DICT_GAS_HEADER,
        json={'textQuery': f'Gas station, TX {zip}', 'regionCode': 'US'},
    ).json()

    if 'error' in res:
        raise Exception(res['error'])

    res = res['places']

    for dict_station in res:
        # Unpack `location` column
        dict_station |= dict_station['location']
        del dict_station['location']

        dict_station['displayName'] = dict_station['displayName']['text']

    return res


if __name__ == '__main__':
    gdf = asyncio.get_event_loop().run_until_complete(
        asyncio.gather(*tuple(get_gas_in(zip) for zip in TUPLE_TRAVIS_ZIPS))
    )
    gdf = (
        pd.DataFrame.from_dict(
            [dict_station for stations in gdf for dict_station in stations]
        )
        .rename(
            columns={
                'displayName': 'Name',
                'internationalPhoneNumber': 'Phone',
                'formattedAddress': 'Address',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
            }
        )
        .drop_duplicates()[
            lambda df: df['Address']
            .str.extract(r'(\d{5})', expand=False)
            .astype(int)
            .isin(TUPLE_TRAVIS_ZIPS)
        ]
    )
    gdf = gpd.GeoDataFrame(
        gdf.drop(columns=['Latitude', 'Longitude']),
        geometry=gpd.points_from_xy(gdf['Longitude'], gdf['Latitude']),
        crs=4326,
    )
    gdf.to_file(f'{STR_DIR}gas.geojson', driver='GeoJSON')

    # Parse alternative fuel data
    gdf = (
        pd.read_csv(f'{STR_DIR}{STR_ALT_FUEL}')
        .rename(
            columns={
                'Station Name': 'Name',
                'Access Code': 'Access',
                'Station Phone': 'Phone',
            }
        )
        .loc[lambda gdf: gdf['ZIP'].isin(TUPLE_TRAVIS_ZIPS)]
        .assign(
            **{
                'Access': lambda gdf: gdf['Access'].str.replace('p', 'P'),
                'Address': lambda gdf: gdf['Street Address'].str.cat(
                    gdf['ZIP'].astype(str), ', TX '
                ),
            }
        )
    )
    gdf = gpd.GeoDataFrame(
        gdf.drop(columns=['Latitude', 'Longitude']),
        geometry=gpd.points_from_xy(gdf['Longitude'], gdf['Latitude']),
        crs=4326,
    )
    arr_bool_elec = gdf['Fuel Type Code'] == 'ELEC'
    gdf[arr_bool_elec].to_file(f'{STR_DIR}elec.geojson', driver='GeoJSON')
    gdf[~arr_bool_elec].to_file(f'{STR_DIR}other.geojson', driver='GeoJSON')

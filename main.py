from enum import IntEnum
from io import BytesIO
from pathlib import Path
from typing import List
from zipfile import ZipFile

import matplotlib.pyplot as plt
import pandas as pd
import requests as requests
import sqlite3

def get_database_filename() -> Path:
    return Path(r'C:\Projects\Python\graaddagen\domoticz_2022_09.db')


def get_data_from_database() -> pd.DataFrame:
    db_filename = get_database_filename()

    query = "SELECT main.Meter_Calendar.Date, main.Meter_Calendar.Value FROM main.Meter_Calendar " \
            "WHERE main.Meter_Calendar.DeviceRowID is 7 ORDER BY main.Meter_Calendar.Date ASC"

    with sqlite3.connect(f'file:{db_filename}?mode=ro', uri=True) as conn:
        data = pd.read_sql_query(query, conn, index_col='Date', parse_dates=['Date'])

    data['Value'] = data['Value'] / 1000.0

    return data


class WeerStations(IntEnum):
    Voorschoten = 215
    Maastricht = 380


def get_historical_data(station: WeerStations) -> pd.DataFrame:
    knmi_data = requests.get(
        f'https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_{station.value}.zip')

    with  ZipFile(BytesIO(knmi_data.content)) as zipfile:
        csv_data = zipfile.open(f'etmgeg_{station.value}.txt').read()

    df = pd.read_csv(BytesIO(csv_data), skiprows=51, index_col='YYYYMMDD',
                     parse_dates=['YYYYMMDD'], infer_datetime_format=True)
    df = df.rename(columns=lambda x: x.strip())

    return df


def compute_graaddagen(df: pd.DataFrame, threshold: float = 18.0) -> pd.DataFrame:
    temperature: pd.DataFrame = df[['TG']].copy()
    temperature['TG'] = pd.to_numeric(temperature['TG'], errors='coerce', downcast='signed') * 0.1
    temperature = temperature.dropna()

    temperature['graaddag'] = temperature['TG'].map(lambda temp : max(0, threshold - temp))
    return temperature


def split_years(df: pd.DataFrame, col_name: str) -> List[pd.DataFrame]:
    df['year'] = df[col_name].dt.year
    return [df[df['year'] == y] for y in df['year'].unique()]


def plot_data(df: pd.DataFrame) -> None:
    dfs = split_years(df, 'YYYYMMDD')
    for year_df in dfs:
        year_df.plot(x='YYYYMMDD', y=['graaddag', 'TG'])
    plt.show()


def main() -> None:
    graad_dagen = compute_graaddagen(get_historical_data(WeerStations.Voorschoten))
    gas_usage = get_data_from_database()

    data = pd.merge(graad_dagen, gas_usage, left_index=True, right_index=True, how='inner')

    data.plot.scatter(x='graaddag', y='Value', c='DarkBlue')
    plt.show()


if __name__ == '__main__':
    main()

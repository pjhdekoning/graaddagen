from enum import IntEnum
from io import BytesIO
from typing import List
from zipfile import ZipFile

import matplotlib.pyplot as plt
import pandas as pd
import requests as requests

class WeerStations(IntEnum):
    Voorschoten = 215
    Maastricht = 380


def get_historical_data(station: WeerStations) -> pd.DataFrame:
    r = requests.get(f'https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_{station.value}.zip')
    zipfile = ZipFile(BytesIO(r.content))

    csv_data = zipfile.open(f'etmgeg_{station.value}.txt').read()

    df = pd.read_csv(BytesIO(csv_data), skiprows=51, parse_dates=['YYYYMMDD'], infer_datetime_format=True)
    df = df.rename(columns=lambda x: x.strip())

    return df


def split_years(df: pd.DataFrame) -> List[pd.DataFrame]:
    df['year'] = df['YYYYMMDD'].dt.year
    return [df[df['year'] == y] for y in df['year'].unique()]


def plot_data(df: pd.DataFrame) -> None:
    temperature: pd.DataFrame = df[['TG', 'YYYYMMDD']].copy()
    temperature['TG'] = pd.to_numeric(temperature['TG'], errors='coerce', downcast='signed') * 0.1
    temperature = temperature.dropna()

    dfs = split_years(temperature)
    for year_df in dfs:
        year_df.plot(x='YYYYMMDD', y='TG')
    plt.show()


def main() -> None:
    df = get_historical_data(WeerStations.Voorschoten)
    plot_data(df)


if __name__ == '__main__':
    main()

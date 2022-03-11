import pandas as pd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv('etmgeg_215.txt', skiprows=51, parse_dates=['YYYYMMDD'], infer_datetime_format=True)
    df = df.rename(columns=lambda x: x.strip())

    temperature = df[['TG', 'YYYYMMDD']]
    temperature['TG'] = pd.to_numeric(temperature['TG'], errors='coerce', downcast='signed')
    temperature = temperature.dropna()
    temperature.plot(x='YYYYMMDD', y='TG')
    plt.show()

if __name__ == '__main__':
    main()

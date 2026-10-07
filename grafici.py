from pipeline import connetti
import pandas as pd
from sqlalchemy import text
import matplotlib.pyplot as plt

if __name__ == "__main__":
    df = pd.read_sql(text("select year(numero_data) as year ,count(*) as misure, avg(wl_mbgl) as average from falde.misure group by year(numero_data) order by year(numero_data);"), connetti())
    print(df)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    ax1.plot(df['year'], df['misure'], marker='o', color='blue')
    ax2.plot(df['year'], df['average'], marker='o', color='orange')
    ax2.invert_yaxis()
    ax1.set_ylabel('Number of measurements')
    ax1.set_title('Number of measurements per year')
    ax2.set_ylabel('Average groundwater depth (m below ground)')
    ax2.set_xlabel('Year')
    ax2.set_title('Average groundwater depth per year')
    ax1.grid(alpha=0.3, linestyle="--", color='gray')
    ax2.grid(alpha=0.3, linestyle="--", color='gray')
    fig.tight_layout()
    fig.savefig('grafico.png')
    plt.show() 
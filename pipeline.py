from aqua_fetch import gw_punjab

def estrai():
    return gw_punjab(data_type = "full", country = "IND")

def pulisci(df):
    df = df.dropna(subset=["WL_MBGL"]) # Tolo le righe con valori NaN nella colonna WL_MBGL
    misure_per_pozzo = (df["WL_MBGL"].groupby(df["OW_ID"]).count())
    pozzi_buoni = misure_per_pozzo[misure_per_pozzo >= 30].index
    df_buoni = df[df["OW_ID"].isin(pozzi_buoni)]
    df_finestra = df_buoni[(df_buoni.index.year >= 1974) & (df_buoni.index.year <= 2015)]
    return df_finestra

grezzo = estrai()
pulito = pulisci(grezzo)
print(pulito["OW_ID"].nunique())
print((pulito["WL_MBGL"].groupby(pulito.index.year).agg(["mean", "count"]).to_string()))

from aqua_fetch import gw_punjab

df = gw_punjab(data_type = "full", country = "IND")
print(df) # Per visualizzare tutta la tabella 

print(df["WL_MBGL"].count()) # Conto le misure valide e scarto i NaN 
print(df["OW_ID"].nunique())

print(df.index.min())
print(df.index.max())
print(df["LOCATION"].unique()[:20]) # Controllo le prime 20 località uniche per la loro affidabilità

print(df["WL_MBGL"].groupby(df.index.year).agg(["mean", "count"]).to_string()) # Ragruppo per anno e calcolo media e numero di misure per anno ed evito che il risultato venga troncato a 20 righe
print(df["WL_MBGL"].groupby(df["OW_ID"]).count().describe()) 

misure_per_pozzo = (df["WL_MBGL"].groupby(df["OW_ID"]).count())
print ((misure_per_pozzo >= 30).sum())

pozzi_buoni = misure_per_pozzo[misure_per_pozzo >= 30].index
df_buoni = df[df["OW_ID"].isin(pozzi_buoni)]
print(df_buoni["OW_ID"].nunique())

df_finestra = df_buoni[(df_buoni.index.year >= 1974) & (df_buoni.index.year <= 2015)]
print(df_finestra["WL_MBGL"].groupby(df_finestra.index.year).agg(["mean", "count"]).to_string())

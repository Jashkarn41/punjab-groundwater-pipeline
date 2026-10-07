from aqua_fetch import gw_punjab
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

def estrai():
    return gw_punjab(data_type = "full", country = "IND")

def pulisci(df):
    df = df.dropna(subset=["WL_MBGL"]) # Tolo le righe con valori NaN nella colonna WL_MBGL
    misure_per_pozzo = (df["WL_MBGL"].groupby(df["OW_ID"]).count())
    pozzi_buoni = misure_per_pozzo[misure_per_pozzo >= 30].index
    df_buoni = df[df["OW_ID"].isin(pozzi_buoni)]
    df_finestra = df_buoni[(df_buoni.index.year >= 1974) & (df_buoni.index.year <= 2015)]
    return df_finestra

def connetti():
    
    load_dotenv()
    url=(f"mysql+pymysql://{os.getenv('db_user')}:{os.getenv('db_password')}"
     f"@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_name')}")
    engine = create_engine(url)

    return engine

def prepara_pozzi(df):
    
    pozzi = df[["OW_ID", "LOCATION", "LAT", "LONG"]]
    pozzi = pozzi.drop_duplicates(subset=["OW_ID"])
    pozzi = pozzi.rename(columns={"OW_ID": "ow_id", "LOCATION":"location", "LAT":"lat", "LONG":"longi"})
    
    return pozzi

def carica_pozzi(pozzi, engine):
    pozzi.to_sql("pozzi", if_exists="append", index=False, con=engine)

def prepara_misure(df):
    
    misure = df.reset_index()
    misure = misure[["OW_ID", "WL_MBGL", "DATE"]]
    misure = misure.rename(columns={"OW_ID": "ow_id", "WL_MBGL": "wl_mbgl", "DATE": "numero_data"})
    
    return misure

def carica_misure(misure, engine):
    misure.to_sql("misure", if_exists="append", index=False, con=engine)

grezzo = estrai()
pulito = pulisci(grezzo)
# pulito["OW_ID"].nunique()
# pulito["WL_MBGL"].groupby(pulito.index.year).agg(["mean", "count"]).to_string()
pozzi_puliti = prepara_pozzi(pulito)
#carica_pozzi(pozzi_puliti, connetti())
misure_pulite = prepara_misure(pulito)
#carica_misure(misure_pulite, connetti())
#print(pozzi_puliti)
#print(misure_pulite)
from aqua_fetch import gw_punjab
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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

def carica_tutto(pozzi, misure, engine):
    
    with engine.begin() as conn:
        
        conn.execute(text("delete from falde.misure"))
        conn.execute(text("delete from falde.pozzi"))
       
        pozzi.to_sql("pozzi", if_exists="append", index=False, con=conn)
        misure.to_sql("misure", if_exists="append", index=False, con=conn)

def applica_regole(df):
    df = df.reset_index()
    df = df.sort_values(["OW_ID", "DATE"])
    
    df["previous"] = df.groupby("OW_ID")["WL_MBGL"].shift(1)
    df["next"] = df.groupby("OW_ID")["WL_MBGL"].shift(-1)
    df["salto_prev"] = df["WL_MBGL"] - df["previous"]
    df["salto_next"] = df["WL_MBGL"] - df["next"]
    
    df["reason"] = None
    df.loc[df["reason"].isna() & df["WL_MBGL"].isna(), "reason"] = "misura_mancante"
    df.loc[df["reason"].isna() & ((df["salto_prev"] > 15) & (df["salto_next"] > 15) | (df["salto_prev"] < -15) & (df["salto_next"] < -15)), "reason"] = "picco_isolato"

    df["valida"] = df["reason"].isna()
    df["validi_pozzo"] = df.groupby("OW_ID")["valida"].transform("sum")
    df.loc[df["reason"].isna() & (df["validi_pozzo"] < 30), "reason"] = "poche_misure"

    df.loc[df["reason"].isna() & ((df["DATE"].dt.year < 1974) | (df["DATE"].dt.year > 2015)), "reason"] = "fuori_periodo"
    return df

if __name__ == "__main__":

    grezzo = estrai()
    pulito = pulisci(grezzo)
    risultato = applica_regole(grezzo)
    print(risultato["reason"].value_counts())
    # pulito["OW_ID"].nunique()
    # pulito["WL_MBGL"].groupby(pulito.index.year).agg(["mean", "count"]).to_string()
    pozzi_puliti = prepara_pozzi(pulito)
    #carica_pozzi(pozzi_puliti, connetti())
    misure_pulite = prepara_misure(pulito)
    #carica_misure(misure_pulite, connetti())
    #print(pozzi_puliti)
    #print(misure_pulite)

    #carica_tutto(pozzi_puliti, misure_pulite, connetti())


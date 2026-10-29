from aqua_fetch import gw_punjab
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
from sqlalchemy.engine import Engine

"""
Groundwater pipeline for Punjab and Haryana.

Downloads the dataset, labels every row as valid or rejected (with a reason)
and loads the valid and the rejected rows into MySQL.
Run it with: python pipeline.py
"""

def estrai() -> pd.DataFrame:
    
    """
    Downloads the groundwater dataset and keeps the wells in India.

    Returns:
        Table with one row per well per year, with DATE as index and the
        columns OW_ID, LONG, LAT, WL_MBGL (depth of the water in metres below
        the ground) and LOCATION. WL_MBGL is empty when the year has no
        measurement.
    """
    return gw_punjab(data_type = "full", country = "IND")

def connetti() -> Engine:
    
    """
    Creates the engine for the MySQL database.

    User, password, host, port and database name are read from the .env file,
    so they are never written in the code.

    Returns:
        SQLAlchemy engine. The connection is opened when it is first used.
    """
    load_dotenv()
    url=(f"mysql+pymysql://{os.getenv('db_user')}:{os.getenv('db_password')}"
     f"@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_name')}")
    engine = create_engine(url)

    return engine

def prepara_pozzi(df:pd.DataFrame) -> pd.DataFrame:
    
    """
    Builds the table of wells for the database.

    Args:
        df: valid rows, with the columns OW_ID, LOCATION, LAT and LONG.

    Returns:
        One row per well, with the columns ow_id, location, lat and longi.
    """ 
    pozzi = df[["OW_ID", "LOCATION", "LAT", "LONG"]]
    pozzi = pozzi.drop_duplicates(subset=["OW_ID"])
    pozzi = pozzi.rename(columns={"OW_ID": "ow_id", "LOCATION":"location", "LAT":"lat", "LONG":"longi"})
    
    return pozzi

def prepara_misure(df:pd.DataFrame) -> pd.DataFrame:
    
    """
    Builds the table of measurements for the database.

    Args:
        df: valid rows, with the columns OW_ID, WL_MBGL and DATE.

    Returns:
        One row per measurement, with the columns ow_id, wl_mbgl and
        numero_data.
    """  
    misure = df.reset_index()
    misure = misure[["OW_ID", "WL_MBGL", "DATE"]]
    misure = misure.rename(columns={"OW_ID": "ow_id", "WL_MBGL": "wl_mbgl", "DATE": "numero_data"})
    
    return misure

def carica_tutto(pozzi:pd.DataFrame, misure:pd.DataFrame, scarti:pd.DataFrame, engine:Engine) -> None:
    
    """
    Replaces the content of the database with the given tables.

    Empties misure, pozzi and scarti (in this order, because misure points to
    pozzi) and loads pozzi, misure and scarti, all in one transaction: if
    something fails, the database stays as it was. Running it twice gives
    the same result.

    Args:
        pozzi: table of wells.
        misure: table of valid measurements.
        scarti: table of rejected rows.
        engine: connection to the database.
    """   
    with engine.begin() as conn:
        
        conn.execute(text("delete from falde.misure"))
        conn.execute(text("delete from falde.pozzi"))
        conn.execute(text("delete from falde.scarti"))
       
        pozzi.to_sql("pozzi", if_exists="append", index=False, con=conn)
        misure.to_sql("misure", if_exists="append", index=False, con=conn)
        scarti.to_sql("scarti", if_exists="append", index=False, con=conn)

def applica_regole(df:pd.DataFrame) -> pd.DataFrame:
    
    """
    Labels every row with the reason why it is rejected, or leaves it empty if valid.

    The rules are applied in this order and a row gets only the first reason
    that applies:
    1. misura_mancante: the row has no measurement.
    2. picco_isolato: the depth differs by more than 15 m from both the
       previous and the next year, in the same direction.
    3. poche_misure: the well has fewer than 30 valid measurements, counted
       after rules 1 and 2.
    4. fuori_periodo: the year is outside 1974-2015.

    Args:
        df: raw table returned by estrai, with DATE as index.

    Returns:
        New table sorted by well and date, with DATE as a column, a "reason"
        column (empty for valid rows) and the helper columns used by the
        rules. The table passed in is not modified.
    """
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

def prepara_scarti(scarti:pd.DataFrame) -> pd.DataFrame:
    
    """
    Builds the table of rejected rows for the database.

    Each row keeps its reason and the 5-year block it belongs to (for example
    1985-1989), so that the rejections can be counted by period. The column
    "loaded" is filled by MySQL.

    Args:
        scarti: rejected rows, with the columns OW_ID, DATE, WL_MBGL and reason.

    Returns:
        Table with the columns ow_id, numero_data, wl_mbgl, reason,
        start_year and end_year.
    """
    rename_scarti = scarti[["OW_ID", "DATE", "WL_MBGL", "reason"]]
    rename_scarti = rename_scarti.rename(columns={"OW_ID":"ow_id", "DATE":"numero_data", "WL_MBGL":"wl_mbgl"})
    rename_scarti["start_year"] = rename_scarti["numero_data"].dt.year // 5*5
    rename_scarti["end_year"] = rename_scarti["start_year"] + 4
    return rename_scarti
   

if __name__ == "__main__":

    grezzo = estrai()
    risultato = applica_regole(grezzo)
    valide = risultato[risultato["reason"].isna()]
    scarti = risultato[risultato["reason"].notna()]
    assert len(valide) + len(scarti) == len(grezzo)

    carica_tutto(prepara_pozzi(valide), prepara_misure(valide), prepara_scarti(scarti), connetti())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# =================================
# CORS (FRONTEND COMPATIBLE)
# =================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================
# FILE PATH
# =================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "REPORTE KLEOS SEMANAL.xlsx")

# =================================
# LOAD DATA (CLEAN VERSION)
# =================================
def load_data():

    act = pd.read_excel(FILE, sheet_name="ACT")
    in_whs = pd.read_excel(FILE, sheet_name="IN WHS")
    out_whs = pd.read_excel(FILE, sheet_name="LT OUT WHS")

    # 🔥 CLEAN COLUMN NAMES (CRITICAL FIX)
    act.columns = act.columns.str.strip()
    in_whs.columns = in_whs.columns.str.strip()
    out_whs.columns = out_whs.columns.str.strip()

    # SOURCE TAG
    act["Source"] = "ACT"
    in_whs["Source"] = "IN WHS"
    out_whs["Source"] = "OUT WHS"

    # NORMALIZE COLUMN NAMES
    act = act.rename(columns={"Order number": "Order Number"})
    in_whs = in_whs.rename(columns={"Order number": "Order Number"})
    out_whs = out_whs.rename(columns={"Order number": "Order Number"})

    # CONCAT ALL DATA
    df = pd.concat([act, in_whs, out_whs], ignore_index=True, sort=False)

    # 🔥 FINAL CLEANING (IMPORTANT)
    df.columns = df.columns.str.strip()

    # REMOVE DUPLICATE COLUMNS IF ANY
    df = df.loc[:, ~df.columns.duplicated()]

    # FILL EMPTY VALUES
    return df.fillna("")


# =================================
# API ENDPOINT
# =================================
@app.get("/orders/{user}")
def get_orders(user: str):

    users_file = os.path.join(BASE_DIR, "users.xlsx")
    users = pd.read_excel(users_file)

    # CLEAN USERS FILE
    users.columns = users.columns.str.strip()

    # FIND USER
    user_row = users[users["User"].str.lower() == user.lower()]

    if user_row.empty:
        return {"error": "Invalid user"}

    customer = user_row.iloc[0]["Customer"]

    # LOAD DATA
    df = load_data()

    # FILTER BY CUSTOMER
    df.columns = df.columns.str.strip()

    filtered = df[
        df["Customer"].astype(str).str.strip() ==
        str(customer).strip()
    ]

    return filtered.to_dict(orient="records")
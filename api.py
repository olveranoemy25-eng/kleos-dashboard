from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# FILES
# =========================================

ORDERS_FILE = "REPORTE KLEOS SEMANAL.xlsx"
USERS_FILE = "users.xlsx"

# =========================================
# CLEAN COLUMNS
# =========================================

def clean_columns(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.replace("  ", " ")
    )

    return df

# =========================================
# LOAD ORDERS
# =========================================

def load_orders():

    # LOAD SHEETS
    act = pd.read_excel(ORDERS_FILE, sheet_name="ACT")
    in_whs = pd.read_excel(ORDERS_FILE, sheet_name="IN WHS")
    out_whs = pd.read_excel(ORDERS_FILE, sheet_name="LT OUT WHS")

    # CLEAN COLUMNS
    act = clean_columns(act)
    in_whs = clean_columns(in_whs)
    out_whs = clean_columns(out_whs)

    # SOURCES
    act["Source"] = "ACT"
    in_whs["Source"] = "IN WHS"
    out_whs["Source"] = "OUT WHS"

    # NORMALIZE COLUMN NAMES
    rename_map = {
        "Order number": "Order Number",
        "Business Unit ": "Business Unit",
        "DAYS IN WHS ": "DAYS IN WHS",
    }

    act = act.rename(columns=rename_map)
    in_whs = in_whs.rename(columns=rename_map)
    out_whs = out_whs.rename(columns=rename_map)

    # CONCAT
    master = pd.concat(
        [act, in_whs, out_whs],
        ignore_index=True,
        sort=False
    )

    # FINAL CLEAN
    master = clean_columns(master)

    # FILL EMPTY
    master = master.fillna("")

    return master

# =========================================
# LOGIN + FILTER
# =========================================

@app.get("/orders/{user}")

def get_orders(user: str):

    # LOAD USERS
    users = pd.read_excel(USERS_FILE)

    users = clean_columns(users)

    # FIND USER
    user_row = users[
        users["User"]
        .astype(str)
        .str.strip()
        .str.lower()
        ==
        user.strip().lower()
    ]

    # INVALID USER
    if user_row.empty:

        raise HTTPException(
            status_code=404,
            detail="Invalid user"
        )

    # CUSTOMER
    customer = str(
        user_row.iloc[0]["Customer"]
    ).strip()

    # LOAD ORDERS
    df = load_orders()

    # VERIFY CUSTOMER COLUMN
    if "Customer" not in df.columns:

        raise HTTPException(
            status_code=500,
            detail="Customer column not found"
        )

    # FILTER CUSTOMER
    filtered = df[
        df["Customer"]
        .astype(str)
        .str.strip()
        ==
        customer
    ]

    return filtered.to_dict(orient="records")
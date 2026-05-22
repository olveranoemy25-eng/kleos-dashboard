from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE = os.path.join(BASE_DIR, "REPORTE KLEOS SEMANAL.xlsx")

def load_data():

    act = pd.read_excel(FILE, sheet_name="ACT")
    in_whs = pd.read_excel(FILE, sheet_name="IN WHS")
    out_whs = pd.read_excel(FILE, sheet_name="LT OUT WHS")

    act["Source"] = "ACT"
    in_whs["Source"] = "IN WHS"
    out_whs["Source"] = "OUT WHS"

    act = act.rename(columns={"Order number": "Order Number"})
    in_whs = in_whs.rename(columns={"Order number": "Order Number"})
    out_whs = out_whs.rename(columns={"Order number": "Order Number"})

    df = pd.concat([act, in_whs, out_whs], ignore_index=True, sort=False)

    return df.fillna("")

@app.get("/orders/{user}")
def get_orders(user: str):

    users_file = os.path.join(BASE_DIR, "users.xlsx")
    users = pd.read_excel(users_file)

    users.columns = users.columns.str.strip()

    user_row = users[users["User"].str.lower() == user.lower()]

    if user_row.empty:
        return {"error": "Invalid user"}

    customer = user_row.iloc[0]["Customer"]

    df = load_data()

    df.columns = df.columns.str.strip()

    filtered = df[df["Customer"].astype(str).str.strip() == str(customer).strip()]

    return filtered.to_dict(orient="records")
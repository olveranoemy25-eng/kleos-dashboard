import pandas as pd

file = r"REPORTE KLEOS SEMANAL.xlsx"

# Leer hojas
act = pd.read_excel(file, sheet_name="ACT")
in_whs = pd.read_excel(file, sheet_name="IN WHS")
out_whs = pd.read_excel(file, sheet_name="LT OUT WHS")
fill = pd.read_excel(file, sheet_name="FILL RATE")

# Agregar tipo de estado
act["Source"] = "ACT"
in_whs["Source"] = "IN WHS"
out_whs["Source"] = "OUT WHS"
fill["Source"] = "FILL RATE"

# Normalizar columnas principales
act_clean = act.rename(columns={"Order number":"Order Number"})
in_clean = in_whs.rename(columns={"Order number":"Order Number"})
out_clean = out_whs.rename(columns={"Order Number":"Order Number"})
fill_clean = fill.rename(columns={"Order Number ":"Order Number"})

# Unir todo
master = pd.concat([act_clean, in_clean, out_clean], ignore_index=True, sort=False)

# Merge fill rate
master = master.merge(
    fill_clean[["Order Number", "Value Fill Rate"]],
    on="Order Number",
    how="left"
)

print("\n🔥 MASTER TABLE (preview)")
print(master.head())

print("\n📊 Total rows:", len(master))
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "data" / "rossmann_train.csv"
OUTPUT_PATH = ROOT / "data" / "rossmann_demo_30.csv"

N_STORES = 30

df = pd.read_csv(INPUT_PATH)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

top_stores = (
    df.groupby("Store")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(N_STORES)
    .index
    .tolist()
)

demo = df[df["Store"].isin(top_stores)].copy()
demo = demo.sort_values(["Store", "Date"])

demo.to_csv(OUTPUT_PATH, index=False)

print(f"Sačuvano: {OUTPUT_PATH}")
print(f"Broj prodavnica: {demo['Store'].nunique()}")
print(f"Broj redova: {len(demo):,}")
print(f"Period: {demo['Date'].min().date()} -> {demo['Date'].max().date()}")
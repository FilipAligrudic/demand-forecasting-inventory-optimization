"""
Učitavanje i čišćenje prodajnih podataka.

Podržava više formata CSV-a zahvaljujući automatskom prepoznavanju kolona:
- sample/Rossmann šema (Date, Sales, Store, Promo...)
- proizvoljne CSV-ove (npr. ChatGPT-generisane) sa kolonama tipa
  date / units_sold / warehouse_city / product_name / promotion_flag / unit_price_eur ...

Takođe rješava UTF-8 BOM i različita kodiranja.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"Date", "Sales"}

# Kanonsko ime -> lista mogućih naziva u ulaznom fajlu (po prioritetu).
# Poređenje je neosjetljivo na velika/mala slova i razmake.
COLUMN_ALIASES: dict[str, list[str]] = {
    "Date": ["date", "datum", "dan", "ds", "order_date", "orderdate", "timestamp", "time", "period"],
    "Sales": [
        "sales", "units_sold", "unitssold", "units", "quantity", "qty", "demand", "y",
        "prodaja", "prodato", "prodate_jedinice", "kolicina", "količina", "potraznja", "potražnja",
    ],
    "Store": [
        "store", "store_id", "storeid", "warehouse_city", "warehousecity", "warehouse",
        "warehouse_id", "warehouseid", "shop", "location", "lokacija",
        "prodavnica", "magacin", "skladiste", "skladište", "radnja", "objekat", "filijala",
    ],
    "Product": [
        "product", "product_name", "productname", "product_id", "productid",
        "item", "item_id", "sku", "proizvod", "artikal", "artikl", "naziv_proizvoda",
    ],
    "Promo": ["promo", "promotion_flag", "promotionflag", "promotion", "promo_flag", "promocija", "akcija"],
    "Price": [
        "price", "unit_price_eur", "unit_price", "unitprice", "unitpriceeur",
        "cijena", "cena", "prodajna_cijena", "jedinicna_cijena",
    ],
    "StateHoliday": [
        "stateholiday", "state_holiday", "holiday_flag", "holidayflag", "holiday",
        "praznik", "drzavni_praznik", "državni_praznik",
    ],
    "SchoolHoliday": ["schoolholiday", "school_holiday", "skolski_praznik", "školski_praznik"],
    "Customers": ["customers", "n_customers", "num_customers", "broj_kupaca", "kupci", "posjetioci", "posetioci"],
}


def _read_csv_any(path: str | Path) -> pd.DataFrame:
    """Pročitaj CSV robustno: prvo UTF-8 (sa BOM), pa fallback kodiranja."""
    for enc in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            if hasattr(path, "seek"):
                path.seek(0)
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    # posljednji pokušaj — pusti pandas da sam odluči
    if hasattr(path, "seek"):
        path.seek(0)
    return pd.read_csv(path)


def _resolve_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Preimenuj prepoznate kolone u kanonska imena. Vraća (df, mapiranje)."""
    # normalizovano ime -> originalno ime
    norm_to_orig = {str(c).strip().lower(): c for c in df.columns}
    rename: dict[str, str] = {}
    mapping: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        # ako kanonsko ime već postoji (bilo kako napisano), prihvati ga
        if canonical.lower() in norm_to_orig and norm_to_orig[canonical.lower()] not in rename:
            orig = norm_to_orig[canonical.lower()]
            if orig != canonical:
                rename[orig] = canonical
            mapping[canonical] = orig
            continue
        for alias in aliases:
            if alias in norm_to_orig and norm_to_orig[alias] not in rename:
                orig = norm_to_orig[alias]
                rename[orig] = canonical
                mapping[canonical] = orig
                break
    if rename:
        df = df.rename(columns=rename)
    return df, mapping


def load_sales_csv(path: str | Path) -> pd.DataFrame:
    """Učitaj CSV, automatski prepoznaj kolone i normalizuj tipove."""
    df = _read_csv_any(path)
    df, mapping = _resolve_columns(df)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        available = ", ".join(str(c) for c in df.columns)
        raise ValueError(
            "Ne mogu pronaći obavezne kolone: "
            + ", ".join(sorted(missing))
            + ".\nDostupne kolone u fajlu: "
            + available
            + ".\nPreimenuj kolonu sa datumom u 'Date' i kolonu sa prodajom/količinom u 'Sales' "
            + "(ili koristi nazive tipa date/units_sold/quantity koje alat automatski prepoznaje)."
        )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Originalni Rossmann nema Product — uvedi placeholder da kasniji kod bude isti
    if "Product" not in df.columns:
        df["Product"] = "ALL"
    if "Store" not in df.columns:
        df["Store"] = "Store_1"

    # Store/Product u tekst (da brojčani ID-evi ne prave probleme u selectbox-u)
    df["Store"] = df["Store"].astype(str)
    df["Product"] = df["Product"].astype(str)

    # Bazni tipovi
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0.0)
    for opt_col in ("Customers", "Promo", "SchoolHoliday", "Price"):
        if opt_col in df.columns:
            df[opt_col] = pd.to_numeric(df[opt_col], errors="coerce")
    if "StateHoliday" in df.columns:
        df["StateHoliday"] = df["StateHoliday"].astype(str)

    df = df.sort_values(["Store", "Product", "Date"]).reset_index(drop=True)
    df.attrs["column_mapping"] = mapping
    return df


def filter_series(df: pd.DataFrame, store: str, product: str) -> pd.DataFrame:
    """Izvuci vremensku seriju za jedan (Store, Product) par."""
    sub = df[(df["Store"] == store) & (df["Product"] == product)].copy()
    return sub.sort_values("Date").reset_index(drop=True)


def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Sedmična agregacija (W-MON anchor)."""
    if df.empty:
        return df
    grouped = (
        df.set_index("Date")
        .groupby(["Store", "Product"])
        .resample("W-MON")
        .agg(
            {
                "Sales": "sum",
                **({"Customers": "sum"} if "Customers" in df.columns else {}),
                **({"Promo": "max"} if "Promo" in df.columns else {}),
                **({"Price": "mean"} if "Price" in df.columns else {}),
            }
        )
        .reset_index()
    )
    return grouped


def basic_summary(df: pd.DataFrame) -> dict:
    """Brz pregled za dashboard."""
    return {
        "rows": int(len(df)),
        "date_min": str(df["Date"].min().date()) if not df.empty else None,
        "date_max": str(df["Date"].max().date()) if not df.empty else None,
        "n_stores": int(df["Store"].nunique()),
        "n_products": int(df["Product"].nunique()),
        "total_sales": float(df["Sales"].sum()),
    }

"""
Sintetički Rossmann-like dataset.

Generiše dnevnu prodaju za nekoliko prodavnica/proizvoda sa realističnim
sezonskim obrascem, trendom, promocijama, praznicima i šumom. Koristi se
kao fallback kada korisnik nema originalni Rossmann CSV.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_sample_sales(
    start_date: str = "2022-01-01",
    end_date: str = "2024-12-31",
    n_stores: int = 4,
    n_products: int = 5,
    seed: int = 42,
) -> pd.DataFrame:
    """Vrati DataFrame sa kolonama: Date, Store, Product, Sales, Customers, Promo,
    StateHoliday, SchoolHoliday, Price."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start_date, end_date, freq="D")

    stores = [f"Store_{i + 1}" for i in range(n_stores)]
    products = [f"SKU_{i + 1}" for i in range(n_products)]

    rows = []
    for store in stores:
        store_factor = rng.uniform(0.7, 1.3)
        for product in products:
            product_factor = rng.uniform(0.6, 1.4)
            base = 80 * store_factor * product_factor
            price = round(rng.uniform(5, 25), 2)

            for d in dates:
                dow = d.dayofweek
                month = d.month

                # nedjelja je obično slabija, subota jača
                dow_factor = {0: 1.0, 1: 0.95, 2: 0.95, 3: 1.0, 4: 1.1, 5: 1.25, 6: 0.6}[dow]
                # sezonski obrazac (peak u decembru i ljeti)
                seasonal = 1.0 + 0.25 * np.sin(2 * np.pi * (month - 3) / 12)
                # blagi trend rasta
                trend = 1.0 + 0.0002 * (d - dates[0]).days

                promo = int(rng.random() < 0.15)
                promo_lift = 1.4 if promo else 1.0

                # praznici — random oko Nove godine, Uskrsa, Božića
                state_holiday = "0"
                if (month == 12 and d.day in (25, 26)) or (month == 1 and d.day == 1):
                    state_holiday = "a"
                school_holiday = int(month in (7, 8) and rng.random() < 0.4)

                holiday_effect = 0.4 if state_holiday != "0" else 1.0

                noise = rng.normal(1.0, 0.08)
                sales = max(0, base * dow_factor * seasonal * trend * promo_lift * holiday_effect * noise)
                customers = max(0, sales / rng.uniform(8, 14))

                rows.append(
                    {
                        "Date": d,
                        "Store": store,
                        "Product": product,
                        "Sales": round(sales, 2),
                        "Customers": int(customers),
                        "Promo": promo,
                        "StateHoliday": state_holiday,
                        "SchoolHoliday": school_holiday,
                        "Price": price,
                    }
                )

    df = pd.DataFrame(rows)
    return df


def ensure_sample_data(path: str | Path) -> Path:
    """Ako CSV ne postoji na zadatoj putanji — generiše ga. Vraća putanju."""
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        df = generate_sample_sales()
        df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
    p = ensure_sample_data(out)
    print(f"Sample data written to: {p}")

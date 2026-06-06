# Prezentacija — Demand Forecasting & Inventory Optimization

Sadržaj 11 slajdova spremnih za kopiranje u PowerPoint.

---

## Slajd 1 — Naslovni slajd

**Predikcija potražnje i optimizacija zaliha**
*"Koliko da naručimo?"*

ISZPO · Individualni projekat · 30 bodova
Autor: [Tvoje ime] · [Datum odbrane]

---

## Slajd 2 — Poslovni problem

- Maloprodajni lanci i e-commerce kompanije konstantno balansiraju između **viška** i **manjka** zaliha.
- **Previše zaliha** → vezani kapital, troškovi skladištenja, kvarenje.
- **Premalo zaliha** → izgubljena prodaja, nezadovoljni kupci, gubitak market share-a.
- Klasične "intuicija + Excel" odluke ne skaliraju na hiljade SKU-ova × stotine prodavnica.

> Cilj: za svaki par (prodavnica, proizvod) automatski odgovoriti — **"Koliko jedinica da naručimo i kada?"**

---

## Slajd 3 — Cilj rješenja

Razviti alat koji:

1. Predviđa dnevnu potražnju po proizvodu i prodavnici.
2. Računa optimalnu količinu narudžbe (EOQ + safety stock + reorder point).
3. Detektuje anomalije u prodajnim podacima.
4. **Objašnjava** zašto je model dao određenu prognozu.
5. Generiše automatsku narudžbenicu za eksport (CSV / Excel).
6. Omogućava **what-if simulaciju** — promocija, cijena, lead time.

---

## Slajd 4 — Dataset

**Rossmann Store Sales** (Kaggle):
- `Date`, `Store`, `Sales`, `Customers`, `Promo`, `StateHoliday`, `SchoolHoliday`
- Dnevna granularnost — idealno za forecasting.

**Sintetički fallback dataset:**
- Generiše se automatski ako korisnik nema originalni CSV.
- Realističan: trend + sezona + promocije + praznici + šum.
- Rezultati nad njim su **demonstracioni**.

---

## Slajd 5 — Data pipeline i feature engineering

**Pipeline:**
CSV → čišćenje → kalendarski feature-i → lag → rolling statistika → model

**Generisani feature-i (~30):**
- Kalendar: dayofweek, month, weekofyear, vikend, sin/cos enkoding sezone
- Lag: t-1, t-2, t-3, t-7, t-14, t-28
- Rolling: mean i std za 7/14/28 dana (sa shift(1) — bez data leakage)
- Eksogeni: Promo, StateHoliday, SchoolHoliday, Price, Customers

---

## Slajd 6 — ML modeli i evaluacija

| Model | Uloga |
|-------|-------|
| Moving Average | Baseline (donja granica) |
| **LightGBM** | **Glavni model** — point + 2 quantile za interval pouzdanosti |
| Prophet | Opcioni sezonski model |

**Metrike (backtest, zadnjih 28 dana):**
- MAE, RMSE, MAPE
- Tipičan rezultat na sample dataset-u: **LightGBM smanjuje MAE ~45%** u poređenju sa baseline-om.

---

## Slajd 7 — Optimizacija zaliha

**EOQ formula:** $EOQ = \sqrt{2DS/H}$
- D = godišnja potražnja, S = ordering cost, H = holding cost

**Safety stock:** $SS = z \cdot \sigma_d \cdot \sqrt{L}$
- z = faktor service level-a (npr. 1.65 za 95%)

**Reorder point:** $ROP = \bar{D} \cdot L + SS$

**Recommended order:** kombinuje EOQ + pokrivanje review_period + lead_time + safety stock − trenutni lager.

---

## Slajd 8 — Dashboard i What-if simulacije

**Streamlit dashboard, 6 tabova:**
- Forecast (sa intervalom pouzdanosti)
- Optimizacija zaliha (osjetljivost na service level i lead time)
- Anomalije (Isolation Forest)
- SHAP objašnjenja
- Automatska narudžbenica (CSV / Excel export)
- Evaluacija modela

**What-if scenariji:**
- Promocija → +35% potražnja
- Promjena cijene → elastičnost −1.2
- Dodatno kašnjenje lead time-a → veći safety stock

---

## Slajd 9 — Objašnjenja modela (SHAP)

- **Global importance:** koji feature-i imaju najveći uticaj na potražnju u prosjeku.
- **Lokalno objašnjenje:** zašto je model za određeni dan dao tu prognozu.

Tipično za naš dataset:
1. `lag_7` (prodaja prije sedmicu) — najjači prediktor
2. `rmean_28` (mjesečni prosjek)
3. `Promo`, `is_weekend`, `month_sin`/`month_cos`

> Transparentnost → povjerenje korisnika → adopcija alata.

---

## Slajd 10 — Rezultati i poslovna vrijednost

**Tehnički rezultati (sample dataset):**
- LightGBM MAPE ~7-8%
- Validna detekcija anomalija (Isolation Forest)
- Stabilne narudžbenice za 20+ Store/Product parova

**Poslovna vrijednost:**
- Smanjenje troškova zaliha (EOQ optimum)
- Manje stockout situacija (safety stock + service level kontrola)
- **Brže odluke** — automatska narudžbenica umjesto manuelnog Excel-a
- **Transparentnost** — SHAP objašnjenja za supply chain tim

---

## Slajd 11 — Zaključak i buduća poboljšanja

**Šta je urađeno:**
- Funkcionalan end-to-end alat (data → forecast → optimizacija → narudžbenica)
- Modularan kod (`src/` paket), notebook eksperimenti, Streamlit UI
- Pokretanje sa jednom komandom: `streamlit run app.py`

**Buduća poboljšanja:**
- DeepAR / LSTM / TFT za zajedničko učenje preko serija
- Hijerarhijski forecast (total → category → SKU)
- Rolling-origin cross-validation
- Optimizacija promo kalendara
- A/B test stvarnih narudžbi vs preporuka

---

## Slajd 12 — Demo i pitanja

- Live demo dashboarda
- Forecast → SHAP → Narudžbenica → Excel
- What-if: promocija + lead time
- Pitanja & odgovori

---

## Vizuelni savjeti

- Boje: 1 primary (#1f2d3d navy) + 1 accent (#d62728 red) + 1 success (#2ca02c green)
- Screenshot-ovi dashboarda na slajdovima 8, 9, 10
- Slika EOQ krive na slajdu 7 (zbir ordering + holding troška sa minimumom)
- Tabela poređenja modela na slajdu 6

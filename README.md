# Demand Forecasting & Inventory Optimization

**Predikcija potražnje i optimizacija zaliha — "Koliko da naručimo?"**

Praktičan alat za supply chain tim maloprodajnog lanca / e-commerce kompanije.
Sistem predviđa dnevnu potražnju, optimizuje količinu narudžbe (EOQ + safety stock + reorder point),
detektuje anomalije, objašnjava predikcije (SHAP) i generiše automatsku narudžbenicu.

---

## Sadržaj

1. [Poslovni problem](#poslovni-problem)
2. [Poslovna vrijednost](#poslovna-vrijednost)
3. [Dataset](#dataset)
4. [Instalacija](#instalacija)
5. [Pokretanje aplikacije](#pokretanje-aplikacije)
6. [Struktura projekta](#struktura-projekta)
7. [Objašnjenje modela](#objašnjenje-modela)
8. [EOQ i safety stock logika](#eoq-i-safety-stock-logika)
9. [Dashboard — opis](#dashboard--opis)
10. [Primjer korišćenja](#primjer-korišćenja)
11. [Rezultati](#rezultati)
12. [Moguće nadogradnje](#moguće-nadogradnje)

---

## Poslovni problem

Maloprodajni lanac i e-commerce kompanije neprestano balansiraju između **viška** i **manjka** zaliha:

- **Previše zaliha** → vezani kapital, troškovi skladištenja, rizik od kvarenja.
- **Premalo zaliha** → izgubljena prodaja, nezadovoljni kupci, gubitak market share-a.

Klasične "intuicija + Excel" odluke ne skaliraju na hiljade SKU-ova × stotine prodavnica.
Potreban je sistem koji za svaki par (prodavnica, proizvod) odgovara na pitanje:
**"Koliko jedinica da naručimo i kada?"**

## Poslovna vrijednost

- **Smanjenje troškova zaliha** kroz EOQ optimizaciju (matematički optimum ordering + holding troška).
- **Manje stockout situacija** zahvaljujući safety stock-u koji uračunava varijabilnost potražnje i lead time.
- **Bolji weekly planning** — automatske preporuke umjesto manuelnog Excel-a.
- **Brže donošenje odluka** — what-if simulacija (promocija, cijena, lead time) u realnom vremenu.
- **Transparentnost** — SHAP objašnjenja pokazuju **zašto** model traži više/manje jedinica.

## Dataset

Projekat koristi **Rossmann Store Sales** šemu:

```text
Date · Store · Sales · Customers · Promo · StateHoliday · SchoolHoliday
```

Za finalni demo koristi se:

```text
data/rossmann_demo_30.csv
```

To je podskup od **30 Rossmann prodavnica**, napravljen iz punog Rossmann dataseta kako bi se aplikacija brzo pokretala tokom prezentacije. Puni Rossmann dataset ima **1115 prodavnica** i može se koristiti za offline trening, ali nije praktičan za live demo jer učitavanje i trening traju znatno duže.

Rossmann dataset nema `Product` / `SKU` kolonu. Zbog toga aplikacija automatski tretira svaku prodavnicu kao jednu vremensku seriju sa:

```text
Product = ALL
```

Arhitektura projekta ipak podržava `Product` kolonu, tako da se isti sistem može koristiti i za dataset sa pojedinačnim proizvodima/SKU-ovima.

### Priprema Rossmann demo dataseta

Ako postoji puni dataset:

```text
data/rossmann_train.csv
```

može se napraviti demo dataset od 30 prodavnica komandom:

```bash
python make_rossmann_demo.py
```

Rezultat je:

```text
data/rossmann_demo_30.csv
```

> Napomena: puni Rossmann dataset može se preuzeti sa Kaggle takmičenja Rossmann Store Sales. Zbog pravila distribucije dataset može ostati lokalno, dok se za demo koristi manji pripremljeni fajl.


## Instalacija

Potreban Python 3.10+.

```powershell
# Windows / PowerShell
cd demand-forecasting-inventory-optimization
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Linux / Mac
cd demand-forecasting-inventory-optimization
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Pokretanje aplikacije

```bash
streamlit run app.py
```

Aplikacija se otvara u browseru na:

```text
http://localhost:8501
```

Dashboard podrazumijevano učitava:

```text
data/rossmann_demo_30.csv
```

Ako fajl ne postoji, potrebno je ubaciti demo CSV u `data/` folder ili ga napraviti pomoću:

```bash
python make_rossmann_demo.py
```


## GitHub i Streamlit Cloud

1. Napravi ili koristi postojeći GitHub repo i pushuj ovaj projekat.
2. Na Streamlit Cloud-u izaberi taj GitHub repo.
3. Kao main file postavi `app.py`.
4. Kao Python dependencies koristi `requirements.txt`.
5. Deploy će raditi direktno iz GitHub-a; promjene u repou se automatski povlače na Streamlit.

## Struktura projekta

```
demand-forecasting-inventory-optimization/
├── app.py                          # Streamlit dashboard (navigacija po prikazima)
├── .streamlit/config.toml          # tema (boje, font, upload limit)
├── requirements.txt
├── README.md
├── data/
│   └── sample_sales.csv            # generiše se automatski
├── src/
│   ├── data_processing.py          # učitavanje + auto-prepoznavanje kolona + čišćenje
│   ├── feature_engineering.py      # lag, rolling, kalendar (29 feature-a)
│   ├── forecasting.py              # baseline, seasonal-naive, LightGBM, Holt-Winters, ensemble, Prophet
│   ├── inventory_optimization.py   # EOQ, safety stock, ROP, newsvendor (stockout)
│   ├── anomaly_detection.py        # Isolation Forest + z-score
│   ├── explainability.py           # SHAP global + lokalno
│   ├── order_generator.py          # narudžbenica + CSV/Excel export
│   └── generate_sample_data.py     # sintetički demo dataset
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_model_training.ipynb
├── outputs/                        # snimljene narudžbenice
└── presentation/
    ├── presentation_outline.md             # kratki sadržaj slajdova
    ├── odbrana_prezentacija.md             # detaljan paket za odbranu (govor, Q&A, demo plan)
    ├── Odbrana_Demand_Forecasting.pptx     # gotova prezentacija (PowerPoint)
    └── build_pptx.js                       # skripta koja generiše .pptx
```

## Objašnjenje modela

> **Status modela (važno):**
> - **LightGBM** (ML) — glavni model, uvijek radi.
> - **Holt-Winters** (klasičan sezonski, `statsmodels`) — radi i na Python 3.13.
> - **Ensemble (hibrid)** — težinski spoj LightGBM + Holt-Winters; **podrazumijevani** model i obično najtačniji/najrobusniji. Ovo je "hibridni model" iz postavke zadatka.
> - **Sezonski naivni** — brz klasičan benchmark bez ijedne biblioteke.
> - **Prophet** — *opcioni*, samo na Python < 3.13 (na 3.13 se preskače; ulogu sezonskog modela preuzima Holt-Winters).
> - **LSTM / Transformer** — planirana nadogradnja (vidi [Moguće nadogradnje](#moguće-nadogradnje)).
>
> U dashboardu se glavni model bira u sidebaru ("Glavni model za prognozu"), a tab **Evaluacija** mjeri sve modele pošteno (backtest + rolling-origin CV).

### Baseline — moving average

Prosjek prodaje posljednjih 7 dana, ponovljen N puta. Daje donju granicu performansi
sa kojom poredimo glavni model.

### Sezonski naivni (seasonal naive)

Prognoza za dan *t* = stvarna prodaja od prije 7 dana (`y[t-7]`). Jednostavan, brz i
iznenađujuće jak benchmark za serije sa sedmičnom sezonalnošću. Nema eksternih zavisnosti,
pa **uvijek** radi — za razliku od Prophet-a. Interval pouzdanosti se računa iz reziduala
sezonskog ponavljanja na istoriji.

### Holt-Winters (klasičan sezonski model)

Exponential Smoothing (trend + sedmična sezonalnost, `seasonal_periods=7`) iz `statsmodels`.
Radi na Python 3.13 (za razliku od Prophet-a), brz je i odlično hvata sedmični obrazac.
Interval pouzdanosti se računa iz reziduala.

### Ensemble (hibridni model) — podrazumijevani

Težinski prosjek prognoza više modela poravnatih po datumima:

```
yhat_ensemble = 0.6 · yhat_LightGBM + 0.4 · yhat_HoltWinters   (+ Prophet ako postoji)
```

Ovo je **hibridni model** iz postavke — spaja jaku ML metodu (LightGBM, hvata nelinearne
interakcije i egzogene faktore) sa klasičnim sezonskim modelom (Holt-Winters). U backtest-u
je obično najtačniji ili najrobusniji jer "uprosječuje" greške pojedinačnih modela.

### Glavni model (ML) — LightGBM

Gradient boosted decision trees. Izabran jer:

- **Brz** i dobro radi sa tabularnim podacima i lag feature-ima.
- Hvata **nelinearne interakcije** (npr. promocija × vikend).
- Lako daje **quantile predikcije** za interval pouzdanosti (10% i 90% percentil).
- SHAP TreeExplainer je egzaktan i brz.

Feature-i:

- **Kalendarski:** dayofweek, month, weekofyear, quarter, vikend, sin/cos enkoding.
- **Lag:** `Sales_{t-1, t-2, t-3, t-7, t-14, t-28}`.
- **Rolling:** rolling mean i std za 7/14/28 dana (sa shift(1) — bez data leakage-a).
- **Eksogeni:** Promo, StateHoliday, SchoolHoliday, Price.
  > `Customers` se **namjerno izostavlja** — to je istovremena (same-day) informacija koja nije
  > poznata u trenutku prognoze; uključivanje bi bilo curenje informacija (data leakage) i kvarilo bi
  > rekurzivni forecast. Takođe, budući dani podrazumijevaju "bez promocije/praznika" osim ako se ne
  > zada kroz What-if (kopiranje zadnjeg dana bi naduvalo forecast ako je zadnji dan bio promo).

### Prophet (opciono)

Facebook Prophet — sezonski model dobar za serije sa jasnim godišnjim/sedmičnim ciklusom.
Aktivira se opciono u dashboardu zbog sporog treniranja. **Napomena:** na Python 3.13 Prophet
nije instaliran (nema zvaničnog wheel-a), pa ga aplikacija preskače i jasno to prikaže;
u tom slučaju ulogu sezonskog modela preuzima *sezonski naivni* benchmark.

### Confidence intervali

Dva pristupa kombinovana:
- **Quantile LightGBM** — dva dodatna modela trenirana sa `objective="quantile"` i α=0.1 / α=0.9.
- Prophet vraća sopstveni 80% interval iz Bayesian inference.

## EOQ i safety stock logika

### Economic Order Quantity (EOQ)

$$EOQ = \sqrt{\frac{2 \cdot D \cdot S}{H}}$$

gdje su:
- `D` — godišnja potražnja
- `S` — trošak po narudžbi
- `H` — holding cost po jedinici godišnje

Minimizuje zbir ordering + holding troškova.

### Safety stock

$$SS = z \cdot \sigma_d \cdot \sqrt{L}$$

- `z` — z-vrijednost iz normalne raspodjele za izabrani service level (npr. 1.65 za 95%)
- `σ_d` — standardna devijacija dnevne potražnje
- `L` — lead time u danima

Štiti od stockout-a kada potražnja iznenada raste tokom lead time-a.

### Reorder point

$$ROP = \bar{D} \cdot L + SS$$

Kada nivo zaliha padne ispod ROP — naručuje se EOQ.

### Preporučena količina

Aplikacija kombinuje EOQ sa pokrivanjem `review_period + lead_time`:

```
recommended = max(EOQ, mean_daily_demand × (review_period + lead_time) + safety_stock - current_stock)
```

### Stockout cost — newsvendor model

`stockout_cost` (trošak izgubljene prodaje po jedinici) ulazi u dvije veličine:

- **Ekonomski optimalan service level** (newsvendor kritični odnos):

$$SL^* = \frac{C_u}{C_u + C_o}, \quad C_u = \text{stockout cost}, \quad C_o = \text{holding} \times \frac{\text{cover days}}{365}$$

  Dashboard prikazuje ovaj optimum i poredi ga sa trenutno izabranim service level-om —
  tako korisnik vidi da li mu je trenutni izbor ekonomski opravdan.

- **Očekivani trošak manjka po ciklusu** preko standardne funkcije gubitka normalne raspodjele:

$$E[\text{manjak}] = \sigma_L \cdot L(z), \quad L(z) = \varphi(z) - z\,(1 - \Phi(z))$$

  gdje je $\sigma_L = \sigma_d \sqrt{L}$. Veći service level → manji očekivani manjak → manji stockout trošak.

## Dashboard — opis

Dashboard koristi **navigaciju po prikazima** (sidebar radio), a ne klasične tabove.
Razlog je performansa: u Streamlit-u se kod *svih* tabova izvršava pri svakoj interakciji,
pa bi SHAP i Isolation Forest reagovali na svaki pomjeraj klizača. Sa navigacijom se
izvršava **samo aktivni prikaz**, čime je svaka interakcija reda 0.1–0.4 s (nakon što se
model jednom istrenira i keširaju rezultati).

| Prikaz | Opis |
|--------|------|
| **Pregled** | Poslovni kontekst: ukupna prodaja, trend, top proizvodi/prodavnice, uputstvo. |
| **Forecast** | Stvarna prodaja, LightGBM forecast sa intervalom pouzdanosti, baseline + opcioni sezonski naivni / Prophet. |
| **Optimizacija zaliha** | EOQ, safety stock, ROP, osjetljivost na service level i lead time. |
| **Anomalije** | Isolation Forest / z-score detekcija, vizuelno označavanje na grafiku. |
| **Objašnjenja (SHAP)** | Global feature importance + lokalno objašnjenje posljednje tačke. |
| **Narudžbenica** | Automatska generacija za sve (Store, Product) parove — CSV i Excel export. |
| **Evaluacija modela** | Pošteno poređenje: brzi backtest **i** rolling-origin CV (3 prozora). MAE/RMSE/MAPE za Baseline / Sezonski naivni / Holt-Winters / LightGBM / Ensemble. |

Tema i izgled su definisani u `.streamlit/config.toml` + CSS u `app.py` (hero header, KPI kartice).

Sidebar omogućava:
- Upload vlastitog CSV-a (fallback je sample dataset).
- Izbor prodavnice i proizvoda.
- **Izbor glavnog modela** (Ensemble / LightGBM / Holt-Winters / Sezonski naivni).
- **Granularnost prikaza:** dnevno ili sedmično (zadatak traži oboje).
- Promjenu inventory parametara (ordering cost, holding cost, lead time, service level...).
- **What-if simulacija:** promocija, promjena cijene, dodatni lead time.

## Primjer korišćenja

1. Otvori dashboard (`streamlit run app.py`).
2. Iz sidebar-a izaberi `Store_1` i `SKU_2`.
3. Pomjeri service level na 0.98 — safety stock raste, vidiš novu preporuku.
4. Uključi **What-if: Promocija** — forecast skoči ~35%, preporučena količina takođe.
5. Idi na **Objašnjenja (SHAP)** — vidiš da je lag_7 (prodaja prije sedmicu dana) najjači prediktor.
6. Idi na **Narudžbenica → Generiši** — dobiješ tabelu za sve parove, klikneš **Preuzmi Excel**.

## Rezultati

Na sintetičkom dataset-u (4 prodavnice × 5 proizvoda × ~3 godine):

**Pošten višednevni backtest** (28 dana unaprijed), prosjek preko svih 20 serija sintetičkog dataset-a:

| Model | MAE | RMSE | MAPE |
|-------|-----|------|------|
| Baseline (moving avg) | 17.7 | 23.1 | 34.1% |
| Sezonski naivni | 16.4 | 22.7 | 28.1% |
| Holt-Winters | 12.1 | 17.0 | 21.8% |
| LightGBM | 12.3 | 17.4 | 20.2% |
| **Ensemble (hibrid)** | **11.6** | **16.9** | **19.8%** |

> **Ensemble (LightGBM + Holt-Winters) je najtačniji** na sve tri metrike — to je poenta hibridnog modela.
> Brojevi variraju po seriji; **Evaluacija → Pokreni evaluaciju** daje tačne vrijednosti (i rolling-origin CV).
>
> **Važna napomena o MAPE:** validaciona MAPE (1 korak, sa stvarnim lag-ovima) je oko **7%**, ali to je
> optimistično. Realnu tačnost daje **višednevni backtest** iznad (~20%), jer se tu prognoze hrane same
> sobom kroz 28 dana. KPI kartica prikazuje 1-korak vrijednost (jasno označenu), a tab Evaluacija realnu.

## Već urađeno (iznad osnovne postavke)

- **Hibridni ensemble** (LightGBM + Holt-Winters) kao podrazumijevani model.
- **Rolling-origin cross-validacija** (ne samo jedan backtest).
- **Dnevna i sedmična** granularnost prikaza.
- **Ispravljen data leakage** (`Customers`) i bug rekurzivnog forecasta (promo se više ne "lijepi").

## Moguće nadogradnje

- **DeepAR / LSTM / Temporal Fusion Transformer** za multi-series zajedničko učenje.
- **Hijerarhijski forecasting** (store/category/total) sa reconciliation.
- **Promo planner** — optimizacija kalendara promocija na osnovu elastičnosti.
- **Live ingestion** — Kafka/Airflow pipeline za dnevno osvježavanje.
- **A/B test** stvarnih narudžbi vs preporuke alata.
- **Multi-echelon optimizacija** (centralni magacin + prodavnice).

---

**Projekat:** ISZPO (3. godina, 6. semestar) · Individualni projekat (30 bodova) · Rok: 15. jun 2026.

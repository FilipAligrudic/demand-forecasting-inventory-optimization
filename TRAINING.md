# Offline trening modela

Ovaj projekat već trenira LightGBM model direktno iz Streamlit aplikacije, ali za odbranu je korisno imati poseban trening fajl koji jasno pokazuje:

- koji model je treniran
- na kojim Store/Product serijama
- koje metrike su dobijene
- gdje su sačuvani modeli, forecast i rezultati

## Glavni model

Koristi se:

```text
Hybrid Ensemble = 0.6 × LightGBM Quantile Regressor + 0.4 × Holt-Winters
```

LightGBM je glavni ML model, a Holt-Winters dodaje klasičnu sedmičnu sezonalnost. LightGBM se trenira u tri varijante:

```text
point model   -> objective="regression"
lower bound   -> objective="quantile", alpha=0.1
upper bound   -> objective="quantile", alpha=0.9
```

Na taj način dobija se dnevni forecast + interval pouzdanosti.

## Instalacija

```bash
pip install -r requirements.txt
```

Ako si već instalirao dependencies prije dodavanja ovog patch-a, pokreni:

```bash
pip install joblib
```

## Trening na punom Rossmann datasetu

```bash
python train_model.py
```

Ovo trenira model za sve Store/Product serije iz:

```text
data/rossmann_train.csv
```

Pošto puni Rossmann dataset ima 1115 prodavnica, ovaj trening može trajati dugo.

## Trening demo verzije sa 30 prodavnica

```bash
python train_model.py --data data/rossmann_demo_30.csv --horizon 28
```

Ovo je preporučena opcija za brzu provjeru i live demo.

## Trening demo verzije sa rolling-origin cross-validacijom

```bash
python train_model.py --data data/rossmann_demo_30.csv --horizon 28 --cv
```

Ovo je sporije, ali bolje za odbranu jer pokazuje realniju procjenu kvaliteta forecasta.

## Trening jedne serije

```bash
python train_model.py --data data/rossmann_demo_30.csv --store 1 --product ALL --horizon 28
```

Koristi se kada želiš da treniraš samo jednu prodavnicu/seriju.

## Output

Nakon treninga dobijaš folder `models/`:

```text
models/
├── model_Store_1__SKU_1.joblib
├── forecast_Store_1__SKU_1.csv
├── metrics_Store_1__SKU_1.csv
├── training_summary.csv
└── manifest.json
```

Najbitniji fajl za odbranu je:

```text
models/training_summary.csv
```

Tu vidiš za svaki Store/Product par:

- da li je model uspješno istreniran
- broj redova
- broj feature-a
- najbolji model po MAPE
- MAPE LightGBM validacije
- preporučenu količinu narudžbe

## Preporučena komanda za finalnu odbranu

```bash
python train_model.py --horizon 28 --cv
streamlit run app.py
```

Prvo treniraš i sačuvaš modele/metrike, a zatim pokrećeš aplikaciju za demo.

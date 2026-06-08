# Odbrana projekta — kompletan paket za prezentaciju

**Projekat:** Demand Forecasting & Inventory Optimization — *„Koliko da naručimo?“*
**Predmet:** ISZPO (3. godina, 6. semestar) · Individualni projekat
**Trajanje izlaganja:** ~10–12 min + live demo (2–4 min) + pitanja

---

## 0. Analiza projekta (osnova za svaki slajd)

> Ovo je interna analiza — ne ide na slajd, ali svaki slajd je izveden iz nje.

**1. Problem:** Maloprodaja i e-commerce stalno balansiraju između viška i manjka zaliha. Previše = zarobljen kapital i trošak skladištenja; premalo = izgubljena prodaja i nezadovoljni kupci. Odluka „koliko naručiti“ se najčešće donosi intuicijom i u Excel-u, što ne skalira na hiljade SKU-ova.

**2. Cilj:** Funkcionalan alat koji za svaki par (prodavnica, proizvod) predviđa potražnju i preporučuje optimalnu količinu narudžbe, uz objašnjenje i simulaciju scenarija.

**3. Ciljna grupa:** supply chain / planning tim, nabavka, category menadžeri u retailu i e-commerce-u; posebno manje firme bez skupog ERP forecasting modula.

**4. Glavne funkcionalnosti (IMPLEMENTIRANO):** forecasting (5 modela), confidence intervali, EOQ optimizacija zaliha, detekcija anomalija, SHAP objašnjenja, what-if simulacija, automatska narudžbenica sa Excel/CSV exportom, evaluacija modela (backtest + rolling-origin CV), Streamlit dashboard sa 7 prikaza.

**5. Arhitektura:** modularni Python paket (`src/`) + Streamlit UI; file-based ulaz/izlaz (CSV → CSV/Excel), bez baze.

**6. Tehnologije:** Python, pandas, numpy, scikit-learn, LightGBM, statsmodels (Holt-Winters), SHAP, scipy, Plotly, Streamlit, openpyxl; Prophet opciono.

**7. Način rada:** CSV (ili sintetički demo) → čišćenje + feature engineering (29 feature-a) → trening modela → rekurzivni forecast + intervali → EOQ/safety stock/ROP → narudžbenica.

**8. Najvažnije tehničke odluke:** sprečavanje data leakage-a (shift(1), izbacivanje `Customers`), rekurzivni multi-step forecast, quantile regression za intervale, ensemble (hibrid), graceful fallback Prophet → Holt-Winters na Python 3.13, keširanje u Streamlit-u.

**9. Rezultati (STVARNO IZMJERENO na demo podacima):** LightGBM backtest MAPE ~19%, rolling-origin CV ~14%; jasno bolji od naivnih benchmarka (MA 52%, sezonski naivni 37%). 26/26 modula prošlo smoke test, app se diže bez greške.

**10. Ograničenja / budućnost:** single-series modeli, demo podaci, fiksna elastičnost u what-if, bez baze/autentikacije → budućnost: DeepAR/LSTM/TFT, hijerarhijski forecast, baza + live ingestion, optimizacija promo kalendara.

---

## 1. VIZUELNI IDENTITET

**Paleta (3 glavne boje + neutralne):**

| Uloga | Boja | HEX |
|---|---|---|
| Pozadina | Bijela / vrlo svijetla slate | `#FFFFFF` (sekcije: `#F8FAFC`) |
| Tekst / naslovi | Navy (slate-900) | `#0F172A` |
| Akcent (primarni) | Plava | `#2563EB` |
| Akcent (sekundarni) | Sky | `#0EA5E9` |
| Pozitivno (rezultati/uspjeh) | Zelena | `#16A34A` |
| Upozorenje / anomalije | Crvena | `#DC2626` |

> Pravilo: na slajdu nikad više od **2 akcentne boje istovremeno**. Navy je za tekst, plava za naglaske, zelena/crvena samo na slajdu rezultata i anomalija. Boje su namjerno iste kao u aplikaciji → vizuelni kontinuitet sa live demom.

**Tipografija:**
- Naslovi: **Poppins SemiBold** (geometrijski, moderan, tehnološki). Alternativa: Montserrat.
- Tekst: **Inter Regular/Medium** (čist, čitljiv na projektoru). Alternativa: Roboto.
- Veličine: naslov slajda 32–40pt, podnaslov 20–24pt, bullet 18–20pt, caption 14pt.

**Ikonice:** linijske (stroke), tanke, konzistentne — **Lucide** ili **Phosphor**. Sve u navy ili plavoj, bez šarenila. Jedna debljina linije kroz cijelu prezentaciju.

**Stil dijagrama:** flat, zaobljeni pravougaonici (border-radius ~12px), tanki konektori sa strelicama, jedna akcentna boja, mnogo praznog prostora. Bez 3D, bez sjenki osim vrlo blage (0 8px 24px rgba navy 8%).

**Screenshotovi aplikacije:** uokvireni u suptilan „browser“ ram (svijetla traka + tri tačkice) ili u zaobljenu karticu sa mekom sjenkom, postavljeni na `#F8FAFC` pozadinu. Bitni detalji uvećani (zoom) sa plavim okvirom 2px. Uvijek čitljivi — radije pola screenshota čitljivo nego cijeli sitan.

**Princip:** mnogo bijelog prostora, velik naslov, kratak tekst, jedna poruka po slajdu. Bez clipart-a, bez gradijenata na tekstu, bez senki na fontu.

---

## 2. GLOBALNE ANIMACIJE (konzistentno kroz cijelu prezentaciju)

- **Tranzicija između slajdova:** `Fade` (0.4s) — svuda ista. Izuzetak: **Problem → Rješenje** koristi `Morph` (0.6s).
- **Pojava elemenata:** `Appear` ili `Fade In` (0.3s), sekvencijalno odozgo nadolje.
- **Koraci u dijagramu:** `Wipe` slijeva (0.3s po koraku) — pojavljuju se jedan po jedan.
- **Naglašavanje detalja:** `Zoom` (0.4s) samo na ključni broj/metriku ili dio screenshota.
- **Bullet liste:** „by paragraph“, svaka stavka `Fade In` 0.2s, redom.

> Pravilo: maksimalno 2 tipa animacije po slajdu. Animacija nikad ne traje duže od 0.6s. Nema rotacija, odskakanja, „fly-in spin“ efekata.

---

## 3. SLAJDOVI — kompletan sadržaj

Za svaki slajd: **tekst na slajdu** (kratak), **vizuelni element**, **raspored**, **govor** (ono što izgovaram), **trajanje**, **animacija**.

---

### SLAJD 1 — Naslovni

**Tekst na slajdu:**
- (Naslov) **Demand Forecasting & Inventory Optimization**
- (Podnaslov) Predviđanje potražnje i optimizacija zaliha — *„Koliko da naručimo?“*
- (Sitno, dno) Ime i prezime · ISZPO · 2026

**Vizuelni element:** veliki naslov lijevo, desno suptilan screenshot forecast grafika (linija prodaje + plavi confidence interval) u browser ramu, blago zatamnjen.

**Raspored:** lijeva polovina tekst (lijevo poravnat), desna polovina vizual. Dosta praznog prostora gore i dolje.

**Govor:** „Dobar dan. Moj projekat se zove Demand Forecasting & Inventory Optimization. To je alat koji maloprodajnim i e-commerce timovima odgovara na jedno svakodnevno, ali skupo pitanje — koliko proizvoda naručiti da ne ostanemo ni u višku ni u manjku zaliha. U narednih desetak minuta pokazaću problem, rješenje, kako sistem radi i uživo demonstrirati aplikaciju.“

**Trajanje:** 25–30s

**Animacija:** naslov `Fade In` (0.4s), pa podnaslov `Fade In` (0.3s), pa screenshot `Zoom` blagi (0.4s).

---

### SLAJD 2 — Problem

**Tekst na slajdu:**
- (Naslov) Višak ili manjak — oba koštaju
- Previše zaliha → zarobljen kapital i trošak skladištenja
- Premalo zaliha → izgubljena prodaja i nezadovoljni kupci
- Odluka se donosi „od oka“ i u Excel-u — ne skalira

**Vizuelni element:** jednostavan vizual sa dvije strane vage: lijevo ikona kutija/skladište (višak), desno prazna polica (manjak), u sredini znak pitanja. Monohromatski.

**Raspored:** naslov gore, tri kratke stavke lijevo, vaga-vizual desno.

**Govor:** „Svaki trgovac ima isti problem. Ako naruči previše, novac mu stoji zaključan u zalihama i plaća skladištenje, a roba može i da propadne. Ako naruči premalo, gubi prodaju i kupce koji odu kod konkurencije. Kratak primjer: lanac sa hiljadu artikala u stotinu prodavnica donosi te odluke ručno, u tabelama. To je sporo, subjektivno i ne može da uhvati sezonu, promocije ni praznike. Upravo tu nastaje prostor za grešku — i za alat koji to radi sistematski.“

**Trajanje:** 45–60s

**Animacija:** stavke `Fade In` redom (po 0.2s). Vaga-vizual `Appear`. (Ovaj slajd je polazna tačka za Morph na sljedeći.)

---

### SLAJD 3 — Predloženo rješenje

**Tekst na slajdu:**
- (Naslov) Jedan alat — od podataka do narudžbenice
- *Sistem koji predviđa potražnju i preporučuje tačnu količinu narudžbe, sa objašnjenjem.*
- Forecast · Optimizacija zaliha · Objašnjenja · Automatska narudžbenica

**Vizuelni element:** centralni screenshot dashboarda (Forecast prikaz) u browser ramu; ispod tri-četiri male pill oznake funkcionalnosti.

**Raspored:** naslov gore, jedna rečenica ispod (bold, veća), screenshot centralno.

**Govor:** „Moje rješenje je web aplikacija koja cijeli taj proces automatizuje. U jednoj rečenici: sistem predviđa buduću potražnju za svaki proizvod i prodavnicu, a zatim na osnovu te prognoze računa koliko tačno treba naručiti — i to objašnjava. Korisnik dobije prognozu sa intervalom pouzdanosti, preporučenu količinu, i gotovu narudžbenicu koju može izvesti u Excel. Sve kroz čist dashboard, bez pisanja koda.“

**Trajanje:** 40–50s

**Animacija:** **Morph** sa prethodnog slajda (vaga „pitanje“ se transformiše u dashboard) — 0.6s. Pill oznake `Wipe` redom.

---

### SLAJD 4 — Ciljevi projekta

**Tekst na slajdu:**
- (Naslov) Šta sam želio da postignem
- **Glavni cilj:** pretvoriti istoriju prodaje u konkretnu preporuku narudžbe
- Tačan forecast po proizvodu/prodavnici
- Optimalna količina (EOQ + safety stock)
- Transparentnost (zašto baš toliko)
- Simulacija scenarija (what-if)

**Vizuelni element:** vertikalna lista sa 4 linijske ikonice (grafikon, kutija, lupa, klizač). Glavni cilj izdvojen u plavoj kartici na vrhu.

**Raspored:** glavni cilj kao istaknuta kartica, ispod 4 podcilja u dva reda (2×2) ili vertikalno.

**Govor:** „Postavio sam jedan glavni cilj i četiri podcilja. Glavni cilj je da od sirove istorije prodaje dobijem konkretan broj — koliko naručiti. Da bih do toga došao, trebalo mi je: prvo, tačan forecast po svakom artiklu; drugo, optimalna količina kroz klasične formule zaliha; treće, transparentnost — da menadžer vidi zašto model predlaže baš toliko; i četvrto, mogućnost da simulira scenarije, na primjer šta ako pokrene promociju ili ako dobavljač kasni.“

**Trajanje:** 40–50s

**Animacija:** glavni cilj `Fade In`, pa 4 podcilja `Appear` redom (0.2s svaki).

---

### SLAJD 5 — Kako sistem funkcioniše (flow)

**Tekst na slajdu:**
- (Naslov) Od podataka do odluke — u pet koraka
- (Flow dijagram, vidi ispod)

**Flow dijagram (horizontalno, 5 čvorova):**
`CSV / demo podaci` → `Čišćenje + Feature engineering` → `ML modeli + intervali` → `Optimizacija zaliha (EOQ)` → `Narudžbenica + Export`

**Vizuelni element:** 5 zaobljenih pravougaonika povezanih strelicama, svaki sa malom ikonicom. Ispod svakog jedna riječ-objašnjenje.

**Raspored:** naslov gore, flow centralno preko cijele širine, dosta vazduha iznad/ispod.

**Govor:** „Sistem radi u pet koraka. Prvo, učita podatke — ili korisnikov CSV ili ugrađeni demo dataset. Drugo, očisti ih i napravi oko trideset feature-a: dan u sedmici, mjesec, praznici, prošla prodaja, pokretni prosjeci. Treće, istrenira modele i napravi prognozu sa intervalom pouzdanosti. Četvrto, na osnovu prognoze izračuna EOQ, safety stock i reorder point. I peto, sklopi gotovu narudžbenicu koju izvozi u Excel ili CSV. Korisnik prati svaki korak kroz prikaze u dashboardu.“

**Trajanje:** 50–60s

**Animacija:** čvorovi se pojavljuju **Wipe** slijeva, jedan po jedan (0.3s), strelice `Fade In` između njih. Ovo je „animirano pojavljivanje koraka u dijagramu“.

---

### SLAJD 6 — Glavne funkcionalnosti

**Tekst na slajdu:**
- (Naslov) Šest stubova aplikacije

Kartice (ikonica + naziv + jedna rečenica):
- 📈 **Forecast** — prognoza potražnje sa intervalom pouzdanosti
- 📦 **Optimizacija zaliha** — EOQ, safety stock, reorder point
- 🚨 **Anomalije** — automatsko otkrivanje skokova i padova prodaje
- 🔍 **SHAP objašnjenja** — koji faktori najviše utiču na potražnju
- 🎛️ **What-if** — simulacija promocije, cijene i lead time-a
- 🧾 **Narudžbenica** — automatski izvještaj sa Excel/CSV exportom

**Vizuelni element:** grid 3×2 kartica, svaka sa linijskom ikonicom u plavoj.

**Raspored:** naslov gore, 6 jednakih kartica u mreži.

**Govor:** „Aplikacija ima šest glavnih funkcionalnosti, i upravo njih ću pokazati u demu. Forecast daje prognozu sa rasponom — ne samo jednu liniju nego i interval pouzdanosti. Optimizacija zaliha pretvara prognozu u konkretne brojeve preko EOQ formule. Detekcija anomalija označava neobične dane u prodaji. SHAP objašnjava koji faktori guraju potražnju gore ili dolje. What-if dozvoljava simulaciju scenarija. I na kraju, automatska narudžbenica — tabela spremna za nabavku, sa exportom u Excel.“

**Trajanje:** 50–60s

**Animacija:** kartice `Fade In` sekvencijalno (0.15s svaka), redom.

---

### SLAJD 7 — Tehnologije

**Tekst na slajdu:**
- (Naslov) Tehnološki stack

| Sloj | Tehnologija | Zašto |
|---|---|---|
| Frontend / UI | Streamlit + Plotly | brz, interaktivni dashboard bez web razvoja |
| Logika / podaci | Python, pandas, numpy | standard za obradu tabelarnih podataka |
| Machine Learning | LightGBM, scikit-learn, statsmodels | tačni i brzi modeli za tabelarne serije |
| Objašnjivost | SHAP | egzaktno objašnjenje predikcija |
| Export | openpyxl | narudžbenica u Excel |

**Vizuelni element:** tabela ili 5 horizontalnih traka, svaka sa logom/ikonom tehnologije.

**Raspored:** naslov gore, tabela centralno. Kolona „Zašto“ vizuelno lakša (sivlja).

**Govor:** „Za stack sam birao alate koji su provjereni i pogodni za studentski, ali ozbiljan projekat. Streamlit sa Plotly mi je dao moderan interaktivni dashboard bez pisanja klasičnog frontenda. Pandas i numpy su standard za obradu podataka. Za modele sam koristio LightGBM — gradient boosting koji odlično radi sa tabelarnim podacima — uz scikit-learn i statsmodels za klasične metode. SHAP koristim da objasnim predikcije, što je danas obavezno za povjerenje u model. A openpyxl pravi Excel narudžbenicu. Namjerno nemam bazu — ulaz i izlaz su fajlovi, što je dovoljno za ovaj obim.“

**Trajanje:** 50–60s

**Animacija:** redovi tabele `Wipe` slijeva, jedan po jedan (0.2s).

---

### SLAJD 8 — Arhitektura sistema

**Tekst na slajdu:**
- (Naslov) Arhitektura — modularno i pregledno
- (Dijagram, vidi ispod)

**Dijagram (vertikalni tok, lijevo→desno):**
```
   [ Korisnik ]
        │  (upload CSV / izbor proizvoda)
        ▼
 [ Streamlit dashboard ]  ◄── interaktivni Plotly grafici
        │
        ▼
 [ src/  Python moduli ]
   ├── data_processing      (čišćenje)
   ├── feature_engineering  (29 feature-a)
   ├── forecasting          (LightGBM, Holt-Winters, ensemble)
   ├── inventory_optimization (EOQ, SS, ROP)
   ├── anomaly_detection    (Isolation Forest)
   ├── explainability       (SHAP)
   └── order_generator      (narudžbenica)
        │
        ▼
 [ Izlaz: tabela + CSV / Excel ]
```

**Vizuelni element:** čist blok-dijagram; korisnik gore, dashboard u sredini, `src/` moduli kao grupa kartica, izlaz dolje. Tanki konektori.

**Raspored:** naslov gore, dijagram centralno preko cijele širine.

**Govor:** „Arhitektura je namjerno jednostavna i modularna. Korisnik komunicira samo sa dashboardom — učita CSV i izabere proizvod. Dashboard poziva sloj Python modula, gdje je svaka odgovornost u zasebnom fajlu: jedan modul čisti podatke, drugi pravi feature-e, treći trenira modele, četvrti računa zalihe, peti traži anomalije, šesti objašnjava, sedmi pravi narudžbenicu. Na kraju izlaz ide nazad u dashboard i u Excel fajl. Ovakva podjela znači da svaki dio mogu testirati i mijenjati nezavisno — što sam i radio kroz smoke test koji prolazi kroz svih sedam modula.“

**Trajanje:** 55–65s

**Animacija:** blokovi `Wipe` odozgo nadolje (korisnik → dashboard → moduli → izlaz), 0.3s po nivou. Moduli unutar grupe `Fade In` zajedno.

---

### SLAJD 9 — Ključne tehničke odluke i izazovi

**Tekst na slajdu:**
- (Naslov) Tri odluke koje su napravile razliku
- **Data leakage** → shift(1) na rolling feature-ima, izbačen `Customers`
- **Pošteno mjerenje** → rekurzivni forecast + rolling-origin CV
- **Intervali pouzdanosti** → quantile LightGBM (10%/90%)

**Vizuelni element:** tri kartice „Izazov → Rješenje“, svaka sa malom strelicom. Po želji mali grafikon intervala desno.

**Raspored:** tri vertikalne kartice jedna do druge; gornji dio crveno-sivkast (izazov), donji plavo (rješenje).

**Govor:** „Izdvojiću tri odluke. Prva — sprečavanje data leakage-a. Pokretne prosjeke računam sa pomakom za jedan dan, da model slučajno ne vidi današnju prodaju kad predviđa današnji dan. Iz istog razloga sam izbacio kolonu broja kupaca, jer je to informacija dostupna tek na kraju dana. Druga — pošteno mjerenje tačnosti. Forecast je rekurzivan, predikcija jednog dana ulazi kao ulaz za sljedeći, pa se greška gomila. Da to ne sakrijem, evaluaciju radim rolling-origin kros-validacijom, na više vremenskih prozora. I treća — interval pouzdanosti. Umjesto jedne tačke, treniram dva dodatna modela za 10. i 90. percentil, pa korisnik vidi raspon, ne lažnu preciznost. Dodatno, Prophet ne radi na Python-u 3.13, pa sam ga napravio opcionim, a njegovu ulogu preuzima Holt-Winters u ensemble modelu.“

**Trajanje:** 60–75s

**Animacija:** kartice `Fade In` redom; unutar svake, „Rješenje“ dio `Wipe` nagore nakon „Izazov“ dijela.

---

### SLAJD 10 — Live demo (najava)

**Tekst na slajdu:**
- (Naslov) Live demo
- 1. Izbor proizvoda i prognoza → 2. Optimizacija zaliha → 3. What-if → 4. Narudžbenica
- *Demo: ~3 minuta · realan primjer*

**Vizuelni element:** veliki „play“ vizual ili 4 numerisana koraka u traci. Minimalno teksta — ovo je tranziciona tačka ka aplikaciji.

**Raspored:** veliki naslov centralno, 4 koraka kao numerisana traka ispod.

**Govor:** „Sada prelazim na živu demonstraciju. Pokazaću kompletan tok: izabraću jedan proizvod i pogledati prognozu sa intervalom, zatim preći na optimizaciju zaliha i vidjeti preporučenu količinu, onda uključiti promociju kao what-if scenario da vidimo kako se preporuka mijenja, i na kraju generisati narudžbenicu i izvesti je u Excel. Krećemo.“

**Trajanje:** 15–20s (pa prelazak na app)

**Animacija:** naslov `Zoom` blagi; 4 koraka `Wipe`. Tranzicija na app — `Fade`.

---

### SLAJD 11 — Rezultati i vrijednost

**Tekst na slajdu:**
- (Naslov) Mjerljivo bolje od ručnog planiranja
- Tabela (backtest, 28 dana):

| Model | MAPE |
|---|---|
| Baseline (moving avg) | 52% |
| Sezonski naivni | 37% |
| **LightGBM** | **19%** |
| Ensemble (hibrid) | 19% |

- Rolling-origin CV: LightGBM ~14% MAPE
- 26/26 modula prošlo automatski test · app se diže bez greške
- *Rezultati su demonstracioni (sintetički podaci)*

**Vizuelni element:** bar chart poređenja modela (manje = bolje), LightGBM istaknut zelenom. Desno tri mini-KPI kartice (MAPE, broj modela, status testa).

**Raspored:** tabela/chart lijevo, kratke poslovne koristi desno (3 bullet-a: niži troškovi, manje stockout-a, brže odluke).

**Govor:** „Šta sam izmjerio. Na demo podacima, glavni model — LightGBM — ima grešku oko devetnaest posto MAPE u backtestu, dok najjednostavniji pristup, prosjek prošle sedmice, ima preko pedeset posto. Dakle više nego upola manja greška. Rolling-origin kros-validacija daje još stabilnijih četrnaest posto. Važno: ovo su demonstracioni rezultati jer koristim sintetičke podatke — ne tvrdim da su to brojevi iz stvarne firme. Ali metodologija je ista i na pravim podacima. Poslovna vrijednost je jasna: niži troškovi zaliha, manje situacija bez robe, i brže, objašnjivo donošenje odluka. Cijeli sistem prolazi automatski test od dvadeset šest provjera.“

**Trajanje:** 60–70s

**Animacija:** barovi `Wipe` nagore redom; LightGBM bar `Zoom` naglasak. KPI kartice `Fade In`.

---

### SLAJD 12 — Ograničenja i budući razvoj

**Tekst na slajdu:**
- (Naslov) Šta dalje
- **Sada:** single-series modeli · demo podaci · file-based · fiksna elastičnost u what-if
- **Sljedeće:** DeepAR/LSTM · hijerarhijski forecast · baza + live ingestion · optimizacija promo kalendara

**Vizuelni element:** dvije kolone — „Trenutna ograničenja“ (sivo) i „Budući razvoj“ (plavo), sa strelicom između.

**Raspored:** lijevo ograničenja, desno budućnost, jasno odvojeno.

**Govor:** „Budući da je ovo individualni projekat, namjerno sam povukao granice. Trenutno svaki proizvod ima svoj model — nema zajedničkog učenja preko serija. Podaci u demu su sintetički, ulaz i izlaz su fajlovi, a elastičnost u what-if simulaciji je pojednostavljena. To su svjesne odluke, ne propusti. Kao sljedeće korake vidim napredne modele tipa LSTM ili DeepAR za zajedničko učenje, hijerarhijski forecast od ukupnog nivoa do artikla, pravu bazu sa dnevnim osvježavanjem podataka, i optimizaciju kalendara promocija. Arhitektura je modularna baš zato da se ovo može dograditi bez prepravke cijelog sistema.“

**Trajanje:** 45–55s

**Animacija:** lijeva kolona `Fade In`, strelica `Wipe`, desna kolona `Fade In`.

---

### SLAJD 13 — Zaključak

**Tekst na slajdu:**
- (Naslov) „Koliko da naručimo?“ — sada imamo odgovor
- Problem: skup višak ili manjak zaliha
- Rješenje: forecast + EOQ + objašnjenje + narudžbenica, u jednom alatu
- **Hvala na pažnji · Pitanja?**

**Vizuelni element:** čist slajd, veliki naslov, mali screenshot dashboarda u dnu kao potpis. Akcentna plava linija.

**Raspored:** naslov centralno, tri kratke linije, „Hvala / Pitanja“ veliko na dnu.

**Govor:** „Da zaključim. Krenuo sam od svakodnevnog, ali skupog problema — koliko naručiti. Napravio sam funkcionalan alat koji predviđa potražnju, računa optimalnu količinu, objašnjava svoju preporuku i izvozi gotovu narudžbenicu — sve u jednom dashboardu, spremno za demonstraciju. Vjerujem da projekat pokazuje i tehničku ozbiljnost i jasnu praktičnu primjenu. Hvala na pažnji, spreman sam za vaša pitanja.“

**Trajanje:** 25–30s

**Animacija:** naslov `Fade In`, tri linije `Appear` redom, „Hvala / Pitanja“ `Zoom` blagi.

---

## 4. LIVE DEMO PLAN (detaljno)

**Cilj:** za ~3 min pokazati kompletan tok: Forecast → Zalihe → What-if → Narudžbenica.

### Priprema unaprijed (prije ulaska u salu)
1. Pokrenuti app **prije prezentacije**: `streamlit run app.py` — neka radi u pozadini (browser tab već otvoren).
2. Otvoriti tab na **Pregled** prikazu, sa već učitanim demo datasetom (ne uploadovati uživo).
3. U sidebaru unaprijed izabrati `Store_1` i `SKU_1` (poznata, lijepa serija).
4. **Istrenirati jednom prije** (otvoriti Forecast da se model keŠira) — da uživo ne čekamo trening.
5. Zumirati browser na ~110–125% radi čitljivosti sa projektora.
6. Zatvoriti sve ostale tabove, notifikacije, Slack/mail.
7. Pripremiti **rezervu**: folder sa 5–6 screenshotova svakog prikaza + 60s snimak ekrana (mp4).

### Tačan redosljed (sa govorom i vremenom)

**Korak 1 — Forecast (45s)**
- Akcija: otvoriti prikaz **📈 Forecast**.
- Govor: „Ovo je prognoza potražnje za izabrani proizvod. Plava linija je stvarna prodaja, crvena je forecast, a osjenčani pojas je interval pouzdanosti — raspon u kojem očekujemo potražnju.“
- Istaći: KPI kartice na vrhu (Forecast suma, Preporučena narudžba, Safety stock, MAPE).

**Korak 2 — Optimizacija zaliha (40s)**
- Akcija: prikaz **📦 Optimizacija zaliha**.
- Govor: „Sada prognozu pretvaramo u brojeve. EOQ je ekonomična količina narudžbe, safety stock je zaštitna zaliha, reorder point je nivo na kojem ponovo naručujemo. Desno je osjetljivost — kako safety stock raste kako dižemo service level.“
- Istaći: kako se brojevi mijenjaju kad u sidebaru pomjerim **Service level** sa 0.95 na 0.98.

**Korak 3 — What-if: promocija (40s)**
- Akcija: u sidebaru čekirati **„Pokreni promociju“**.
- Govor: „Pretpostavimo da pokrećemo promociju. Forecast odmah skače oko trideset pet posto, a sa njim i preporučena količina narudžbe. Ovako planer može unaprijed da odluči koliko da dokupi za akciju.“
- Istaći: promjenu KPI kartice „Preporučena narudžba“ prije/poslije.

**Korak 4 — Narudžbenica + Export (45s)**
- Akcija: prikaz **🧾 Narudžbenica** → dugme **„Generiši za sve parove“** → kad se popuni, kliknuti **„Preuzmi Excel“**.
- Govor: „Na kraju, alat pravi gotovu narudžbenicu za sve proizvode i prodavnice odjednom — sa količinama, safety stockom i procijenjenim troškom. Jedan klik i imamo Excel spreman za nabavku.“
- Istaći: ukupan broj jedinica i procijenjeni trošak (mini-KPI iznad tabele).

**Opcioni korak (ako ima vremena, 30s):** prikaz **🔍 SHAP** — „Model objašnjava sebe: najveći uticaj imaju promocija i prodaja od prije sedam dana.“

### Šta posebno istaći
- Interval pouzdanosti (ne samo jedna linija).
- Trenutna promjena KPI-ja na what-if (vizuelno najefektnije).
- Excel export — opipljiv, poslovni rezultat.

### Ako nešto ne radi (fallback)
- **App ne reaguje / spor trening:** „Da ne čekamo trening uživo, pripremio sam snimak istog toka“ → pustiti 60s snimak ili proći kroz screenshotove.
- **Nema interneta:** nije problem — aplikacija radi **potpuno lokalno**, demo ne zavisi od mreže. (Ovo i reći komisiji kao prednost.)
- **Browser/projektor problem:** preći na screenshot-deck (slajdovi 6 i 11 već sadrže ključne screenshotove).
- **Zlatno pravilo:** nikad ne debug-ovati uživo duže od 10 sekundi — odmah na rezervu, pa nastaviti priču.

---

## 5. PITANJA KOMISIJE (15+ sa odgovorima)

> ⭐ = 5 najvjerovatnijih pitanja.

**⭐ 1. Zašto si izabrao baš ovu temu?**
Jer je problem upravljanja zalihama univerzalan i mjerljivo skup — svaka greška u narudžbi ima direktnu cijenu. Tema spaja machine learning sa konkretnom poslovnom odlukom, što mi je bilo i tehnički izazovno i praktično korisno.

**⭐ 2. Koja je praktična vrijednost — ko bi ovo stvarno koristio?**
Supply chain i planning timovi, nabavka, category menadžeri, posebno u manjim firmama koje nemaju skup ERP forecasting modul. Alat zamjenjuje ručno Excel planiranje objašnjivom, automatskom preporukom i smanjuje i višak i manjak zaliha.

**⭐ 3. Zašto LightGBM, a ne neuronska mreža ili klasična statistika?**
LightGBM je za tabelarne podatke sa lag feature-ima obično tačniji i mnogo brži od neuronskih mreža, a ne traži velike količine podataka. Klasične metode (Holt-Winters) sam ipak uključio i kombinovao u ensemble. Neuronske mreže (LSTM/DeepAR) sam ostavio kao budući korak jer bi za ovaj obim bile preveliki overhead.

**⭐ 4. Kako garantuješ da rezultati nisu posljedica data leakage-a?**
Tri zaštite: pokretne statistike računam sa pomakom (shift(1)) da model ne vidi tekući dan; izbacio sam kolonu broja kupaca jer je to same-day informacija; i evaluaciju radim rolling-origin kros-validacijom na podacima koje model nije vidio, ne na trening skupu.

**⭐ 5. Koliko su tačni rezultati i šta tačno znači MAPE od 19%?**
MAPE od 19% znači prosječno odstupanje prognoze od stvarne prodaje od 19%. To je na demo, sintetičkim podacima, pa su rezultati demonstracioni. Bitno je poređenje: naivni pristup ima preko 50%, dakle model više nego prepolovi grešku. Metodologija je identična i na realnim podacima.

**6. Zašto nemaš bazu podataka?**
Za ovaj obim — ulaz je CSV, izlaz je CSV/Excel — fajlovi su dovoljni i čine alat lakim za pokretanje (jedan `streamlit run`). Bazu sam naveo kao budući korak kad bi se uvelo dnevno osvježavanje i više korisnika.

**7. Kako bi sistem skalirao na hiljade proizvoda?**
Trenutno se model trenira po seriji, što je za hiljade SKU-ova sporo. Rješenje je global/multi-series model (jedan model za sve serije, npr. LightGBM sa ID feature-ima ili DeepAR), plus keširanje i batch trening. Arhitektura je modularna pa se forecasting modul može zamijeniti bez diranja ostatka.

**8. Kako računaš interval pouzdanosti?**
Za LightGBM treniram dva dodatna modela sa quantile objective za 10. i 90. percentil — to daje raspon. Za Holt-Winters i sezonski naivni interval računam iz reziduala (standardne devijacije greške) na istoriji.

**9. Kako radi optimizacija zaliha — koje formule?**
Klasične supply chain formule: EOQ = √(2DS/H), safety stock = z·σ·√L, reorder point = prosječna potražnja·lead time + safety stock. Service level pretvaram u z-vrijednost preko normalne raspodjele. Korisnik može mijenjati sve parametre i odmah vidi efekat.

**10. Šta je „ensemble“ i zašto je default?**
Ensemble je težinski spoj LightGBM-a (60%) i Holt-Wintersa (40%) — kombinuje jaku ML metodu sa klasičnim sezonskim modelom. Pošto „uprosječuje“ greške pojedinačnih modela, obično je najrobusniji. To je hibridni model iz postavke zadatka.

**11. Kako si testirao sistem?**
Napisao sam smoke test koji prolazi kroz svih sedam modula — od učitavanja podataka do narudžbenice — sa stvarnim pozivima, ne samo provjerom sintakse. Prošlo je 26 od 26 provjera, a Streamlit app se diže bez greške (HTTP 200).

**12. Koje su performanse — koliko traje trening?**
Trening jedne serije traje desetak sekundi, a Streamlit keŠira rezultat pa se ne ponavlja pri svakom kliku. Forecast i optimizacija su trenutni. Za narudžbenicu svih parova trening ide redom uz progress bar.

**13. Koja su glavna ograničenja projekta?**
Single-series modeli (nema zajedničkog učenja), demo podaci su sintetički, what-if elastičnost je pojednostavljena i fiksna, i nema baze ni autentikacije. Sve su to svjesne granice obima, ne propusti.

**14. Šta je sigurnosni aspekt sistema?**
Aplikacija radi lokalno, ne šalje podatke na internet, pa je rizik minimalan. Za produkciju bi trebalo dodati autentikaciju, validaciju uploadovanih fajlova i kontrolu pristupa — to je dio budućeg razvoja.

**15. Šta je bio najteži dio razvoja?**
Rekurzivni multi-step forecast — jer predikcija jednog dana postaje ulaz za sljedeći, pa se greška gomila i lako se napravi data leakage. Riješio sam to pažljivim feature inženjeringom (shift) i poštenom rolling-origin evaluacijom.

**16. Šta bi uradio drugačije da kreneš ispočetka?**
Od starta bih išao na global multi-series model umjesto modela po seriji — bilo bi brže i tačnije. Takođe bih ranije postavio rolling-origin CV kao glavnu metriku.

**17. Koji je tvoj individualni doprinos?**
Cijeli projekat je individualan — od arhitekture, kroz svih sedam modula, do dashboarda, testa i dokumentacije. Sam sam birao dataset, modele, formule zaliha i dizajn dashboarda.

**18. Zašto Rossmann, a ne Walmart dataset?**
Rossmann ima jednostavniju šemu sa svim potrebnim feature-ima (promocije, praznici, dnevna prodaja), pa sam više vremena posvetio modelima i dashboardu. Dodatno, aplikacija radi i bez originalnog dataseta jer ima ugrađen generator sintetičkih podataka.

---

## 6. UVODNI GOVOR (~30s)

„Dobar dan. Zovem se [ime] i predstaviću svoj projekat — Demand Forecasting & Inventory Optimization. To je alat koji maloprodajnim i e-commerce timovima odgovara na jedno svakodnevno, ali skupo pitanje: koliko proizvoda naručiti da ne ostanemo ni u višku ni u manjku zaliha. Sistem predviđa potražnju, računa optimalnu količinu narudžbe i sve to objašnjava kroz pregledan dashboard. Pokazaću vam problem, rješenje, kako radi, i demonstriraću ga uživo.“

---

## 7. ZAVRŠNI GOVOR (~20s)

„Ukratko — krenuo sam od skupog problema viška i manjka zaliha i napravio funkcionalan, objašnjiv alat koji daje konkretnu preporuku narudžbe. Projekat je modularan, testiran i spreman za demonstraciju. Hvala na pažnji — rado ću odgovoriti na vaša pitanja.“

---

## 8. CHECKLISTA PRIJE ODBRANE

**Tehnika (dan ranije):**
- [ ] `pip install -r requirements.txt` prošao bez greške na laptopu za prezentaciju
- [ ] `streamlit run app.py` se diže i radi offline (isključi WiFi i provjeri)
- [ ] Demo dataset generisan (`data/sample_sales.csv` postoji)
- [ ] Model za `Store_1 / SKU_1` već istreniran/keŠiran (Forecast otvoren bar jednom)
- [ ] Narudžbenica generisana bar jednom (Excel export radi)

**Rezerva:**
- [ ] Folder sa screenshotovima svih 7 prikaza
- [ ] 60s snimak ekrana kompletnog toka (mp4)
- [ ] Prezentacija u PDF-u (ako PowerPoint pukne) + na USB-u i na mailu

**Sadržaj:**
- [ ] Otvoreni tabovi: samo prezentacija + app
- [ ] Notifikacije / Slack / mail isključeni
- [ ] Browser zoom 110–125%, projektor rezolucija provjerena
- [ ] Baterija puna + punjač ponesen
- [ ] Govori (uvod/zaključak) provježbani naglas, mjereno vrijeme < 12 min

**Mentalno:**
- [ ] Pripremljeno 5 ⭐ pitanja i odgovori provježbani
- [ ] Zna se rečenica „ovo su demonstracioni rezultati (sintetički podaci)“ — reći je proaktivno
- [ ] Pravilo: ne debug-ovati uživo, odmah na rezervu

---

## 9. PROMPT ZA AUTOMATSKO GENERISANJE PREZENTACIJE

> Za alate tipa **Gamma, Tome, Beautiful.ai, Decktopus** ili Copilot/PowerPoint Designer. Kopiraj cijeli blok.

```
Napravi profesionalnu prezentaciju od 13 slajdova na crnogorskom/srpskom jeziku za
završnu odbranu studentskog ML projekta.

TEMA: "Demand Forecasting & Inventory Optimization — Koliko da naručimo?"
Alat predviđa potražnju u maloprodaji/e-commerce i preporučuje optimalnu količinu
narudžbe (EOQ, safety stock, reorder point), uz objašnjenja i automatsku narudžbenicu.

VIZUELNI STIL: moderan, minimalistički, tehnološki, čist, mnogo praznog prostora.
Paleta: pozadina bijela (#FFFFFF), tekst navy (#0F172A), akcent plava (#2563EB),
sekundarni akcent sky (#0EA5E9), zelena (#16A34A) samo za rezultate, crvena (#DC2626)
samo za upozorenja. Font naslova: Poppins SemiBold. Font teksta: Inter. Linijske
(stroke) ikonice, monohromatske u plavoj. Flat dijagrami sa zaobljenim pravougaonicima.
Maksimalno jedna poruka i 3–5 kratkih stavki po slajdu (20–40 riječi). Bez clipart-a.

SLAJDOVI:
1. Naslovni: "Demand Forecasting & Inventory Optimization", podnaslov "Predviđanje
   potražnje i optimizacija zaliha — Koliko da naručimo?", ime autora, ISZPO 2026.
2. Problem: višak zaliha = zarobljen kapital; manjak = izgubljena prodaja; odluke se
   donose ručno u Excel-u i ne skaliraju.
3. Rješenje: jedan alat od podataka do narudžbenice — forecast, optimizacija zaliha,
   objašnjenja, automatska narudžbenica.
4. Ciljevi: glavni cilj (od istorije prodaje do preporuke narudžbe) + 4 podcilja
   (tačan forecast, optimalna količina, transparentnost, what-if simulacija).
5. Kako radi (flow dijagram 5 koraka): CSV/demo podaci → čišćenje + feature engineering
   → ML modeli + intervali → EOQ optimizacija → narudžbenica + export.
6. Glavne funkcionalnosti (6 kartica sa ikonicama): Forecast, Optimizacija zaliha,
   Detekcija anomalija, SHAP objašnjenja, What-if simulacija, Automatska narudžbenica.
7. Tehnologije (tabela sloj/tehnologija/zašto): Streamlit+Plotly (UI), Python/pandas/numpy
   (logika), LightGBM/scikit-learn/statsmodels (ML), SHAP (objašnjivost), openpyxl (Excel).
8. Arhitektura (dijagram): Korisnik → Streamlit dashboard → 7 Python modula u src/
   (data_processing, feature_engineering, forecasting, inventory_optimization,
   anomaly_detection, explainability, order_generator) → izlaz CSV/Excel.
9. Ključne tehničke odluke: sprečavanje data leakage-a (shift(1), izbačen Customers);
   pošteno mjerenje (rolling-origin CV); intervali pouzdanosti (quantile LightGBM 10/90%).
10. Live demo (najava): koraci 1) prognoza 2) optimizacija zaliha 3) what-if promocija
    4) narudžbenica; ~3 minuta.
11. Rezultati: backtest MAPE — Baseline 52%, Sezonski naivni 37%, LightGBM 19%,
    Ensemble 19%; rolling-origin CV LightGBM ~14%; 26/26 modula prošlo test.
    Napomena: rezultati su demonstracioni (sintetički podaci). Bar chart poređenja.
12. Ograničenja i budući razvoj: sada (single-series modeli, demo podaci, file-based,
    fiksna elastičnost) → sljedeće (LSTM/DeepAR, hijerarhijski forecast, baza + live
    ingestion, optimizacija promo kalendara).
13. Zaključak: ponovi problem → rješenje → vrijednost; "Hvala na pažnji · Pitanja?".

Animacije: dosljedno Fade tranzicija između slajdova; elementi se pojavljuju
sekvencijalno (Fade In / Wipe); Morph samo između slajda 2 i 3. Bez djetinjastih efekata.
Ostavi prostor za screenshot aplikacije na slajdovima 1, 3, 6 i 11.
```

---

## 10. SCREENSHOTOVI — koji, gdje i kako

> Napravi ih iz pokrenute aplikacije (`streamlit run app.py`), pri zoom-u ~110%, čist prozor.

| # | Prikaz u app-u | Šta da se vidi | Ide na slajd |
|---|---|---|---|
| 1 | **📈 Forecast** | linija prodaje + crveni forecast + plavi interval pouzdanosti + KPI kartice gore | Slajd 1 (hero, zatamnjen), Slajd 3, Slajd 10 |
| 2 | **📦 Optimizacija zaliha** | EOQ / safety stock / reorder point + grafik osjetljivosti | Slajd 6, Slajd 11 |
| 3 | **🚨 Anomalije** | linija prodaje sa crvenim X markerima anomalija | Slajd 6 |
| 4 | **🔍 SHAP** | horizontalni bar chart važnosti feature-a (Promocija, lag_7…) | Slajd 6, Slajd 9 |
| 5 | **🧾 Narudžbenica** | tabela narudžbenice + mini-KPI (jedinice, trošak) + dugmad za export | Slajd 6, Slajd 11 |
| 6 | **🎯 Evaluacija** | tabela poređenja modela + grupisani bar chart MAE/RMSE/MAPE | Slajd 11 |
| 7 | **🏠 Pregled** | ukupna dnevna prodaja + top proizvodi | Slajd 1 ili 3 (opciono) |

**Kako ih prikazati:** uokviriti u svijetli „browser“ ram ili zaobljenu karticu sa blagom sjenkom, na `#F8FAFC` pozadini. Za slajd 9 i 11 zumirati ključni detalj (interval / najbolji bar) plavim okvirom 2px. Nikad ne lijepiti pun-sitan screenshot — radije isjeći na relevantni dio.

---

*Kraj paketa. Srećno na odbrani 🎓*

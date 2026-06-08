/* Odbrana — Demand Forecasting & Inventory Optimization
   13 slajdova, profesionalni stil, boje iz aplikacije. */
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

// ---------- Paleta ----------
const C = {
  white: "FFFFFF",
  section: "F8FAFC",
  navy: "0F172A",
  navy2: "1E293B",
  blue: "2563EB",
  sky: "0EA5E9",
  green: "16A34A",
  red: "DC2626",
  amber: "D97706",
  slate: "64748B",
  slate2: "94A3B8",
  border: "E2E8F0",
  ice: "CADCFC",
};
const HFONT = "Segoe UI Semibold";
const BFONT = "Segoe UI";

// ---------- Icon helper ----------
async function icon(IconComp, color = "#2563EB", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComp, { color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
const sh = () => ({ type: "outer", color: "0F172A", blur: 9, offset: 3, angle: 135, opacity: 0.12 });

(async () => {
  const p = new pptxgen();
  p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
  p.layout = "W";
  p.author = "ISZPO 2026";
  p.title = "Demand Forecasting & Inventory Optimization";
  const W = 13.333, H = 7.5;

  // Preload icons
  const I = {
    chart: await icon(fa.FaChartLine, "#FFFFFF"),
    box: await icon(fa.FaBoxOpen, "#FFFFFF"),
    warn: await icon(fa.FaExclamationTriangle, "#FFFFFF"),
    search: await icon(fa.FaSearchPlus, "#FFFFFF"),
    sliders: await icon(fa.FaSlidersH, "#FFFFFF"),
    invoice: await icon(fa.FaFileInvoiceDollar, "#FFFFFF"),
    target: await icon(fa.FaBullseye, "#2563EB"),
    cogs: await icon(fa.FaCogs, "#2563EB"),
    check: await icon(fa.FaCheckCircle, "#16A34A"),
    play: await icon(fa.FaPlayCircle, "#FFFFFF"),
    code: await icon(fa.FaLayerGroup, "#2563EB"),
    flask: await icon(fa.FaFlask, "#2563EB"),
    db: await icon(fa.FaDatabase, "#2563EB"),
    brain: await icon(fa.FaBrain, "#2563EB"),
    rocket: await icon(fa.FaRocket, "#FFFFFF"),
  };

  // ---------- Reusable ----------
  function footer(slide, n, dark = false) {
    slide.addText("Demand Forecasting & Inventory Optimization", {
      x: 0.5, y: 7.04, w: 9, h: 0.3, fontFace: BFONT, fontSize: 9,
      color: dark ? C.slate2 : C.slate, align: "left", margin: 0,
    });
    slide.addText(`${n} / 13`, {
      x: 11.83, y: 7.04, w: 1, h: 0.3, fontFace: BFONT, fontSize: 9,
      color: dark ? C.slate2 : C.slate, align: "right", margin: 0,
    });
  }
  function kicker(slide, txt, color = C.blue) {
    slide.addText(txt.toUpperCase(), {
      x: 0.6, y: 0.5, w: 8, h: 0.32, fontFace: HFONT, fontSize: 12.5,
      color, charSpacing: 3, bold: true, margin: 0,
    });
  }
  function title(slide, txt, w = 11.5) {
    slide.addText(txt, {
      x: 0.6, y: 0.84, w, h: 0.9, fontFace: HFONT, fontSize: 32,
      color: C.navy, bold: true, margin: 0,
    });
  }
  function iconBadge(slide, data, x, y, s = 0.62, bg = C.blue) {
    slide.addShape(p.shapes.ROUNDED_RECTANGLE, {
      x, y, w: s, h: s, rectRadius: 0.1, fill: { color: bg }, line: { type: "none" },
      shadow: sh(),
    });
    slide.addImage({ data, x: x + s * 0.22, y: y + s * 0.22, w: s * 0.56, h: s * 0.56 });
  }

  // ============================================================= 1 — NASLOVNI
  let s = p.addSlide();
  s.background = { color: C.navy };
  // suptilni dekor krugovi
  s.addShape(p.shapes.OVAL, { x: 10.2, y: -1.6, w: 5, h: 5, fill: { color: C.blue, transparency: 82 }, line: { type: "none" } });
  s.addShape(p.shapes.OVAL, { x: 11.6, y: 4.2, w: 3.6, h: 3.6, fill: { color: C.sky, transparency: 86 }, line: { type: "none" } });
  s.addText("ISZPO · INDIVIDUALNI PROJEKAT · 2026", {
    x: 0.9, y: 1.5, w: 9, h: 0.4, fontFace: HFONT, fontSize: 13, color: C.sky, charSpacing: 3, bold: true, margin: 0,
  });
  s.addText("Demand Forecasting &\nInventory Optimization", {
    x: 0.9, y: 2.05, w: 11, h: 1.9, fontFace: HFONT, fontSize: 46, color: C.white, bold: true, lineSpacing: 50, margin: 0,
  });
  s.addText("Predviđanje potražnje i optimizacija zaliha — „Koliko da naručimo?“", {
    x: 0.9, y: 4.05, w: 10.5, h: 0.5, fontFace: BFONT, fontSize: 18, color: C.ice, italic: true, margin: 0,
  });
  // tanka akcent linija (samo na naslovnom, dekor)
  s.addShape(p.shapes.RECTANGLE, { x: 0.92, y: 4.75, w: 1.4, h: 0.05, fill: { color: C.blue }, line: { type: "none" } });
  s.addText([
    { text: "Autor: ", options: { color: C.slate2 } },
    { text: "[Ime i prezime]", options: { color: C.white, bold: true } },
  ], { x: 0.9, y: 5.15, w: 8, h: 0.4, fontFace: BFONT, fontSize: 15, margin: 0 });
  s.addText("LightGBM forecasting  ·  EOQ optimizacija  ·  SHAP objašnjenja  ·  Streamlit dashboard", {
    x: 0.9, y: 6.4, w: 11.5, h: 0.4, fontFace: BFONT, fontSize: 12.5, color: C.slate2, margin: 0,
  });

  // ============================================================= 2 — PROBLEM
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Problem");
  title(s, "Višak ili manjak — oba koštaju");
  // dvije kartice (višak / manjak)
  const probCards = [
    { t: "Previše zaliha", d: "Zarobljen kapital, trošak skladištenja, rizik od kvarenja robe.", c: C.amber, ic: I.box },
    { t: "Premalo zaliha", d: "Izgubljena prodaja, nezadovoljni kupci, odlazak konkurenciji.", c: C.red, ic: I.warn },
  ];
  probCards.forEach((pc, i) => {
    const x = 0.6 + i * 4.05;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.1, w: 3.75, h: 2.5, rectRadius: 0.12, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
    iconBadge(s, pc.ic, x + 0.35, y0 = 2.45, 0.62, pc.c);
    s.addText(pc.t, { x: x + 0.35, y: 3.25, w: 3.05, h: 0.45, fontFace: HFONT, fontSize: 19, color: C.navy, bold: true, margin: 0 });
    s.addText(pc.d, { x: x + 0.35, y: 3.72, w: 3.1, h: 0.8, fontFace: BFONT, fontSize: 13.5, color: C.slate, margin: 0, lineSpacing: 18 });
  });
  // desni panel — poenta
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 8.95, y: 2.1, w: 3.78, h: 2.5, rectRadius: 0.12, fill: { color: C.navy }, line: { type: "none" }, shadow: sh() });
  s.addText("Odluka se donosi „od oka“", { x: 9.25, y: 2.45, w: 3.2, h: 0.5, fontFace: HFONT, fontSize: 17, color: C.white, bold: true, margin: 0 });
  s.addText("Planiranje u Excel-u je sporo, subjektivno i ne skalira na hiljade artikala u stotinama prodavnica.", { x: 9.25, y: 3.05, w: 3.25, h: 1.4, fontFace: BFONT, fontSize: 13.5, color: C.ice, margin: 0, lineSpacing: 19 });
  // donja traka primjer
  s.addText([
    { text: "Primjer:  ", options: { bold: true, color: C.blue } },
    { text: "lanac sa 1.000 artikala × 100 prodavnica = 100.000 odluka o narudžbi — ručno, svake sedmice.", options: { color: C.navy } },
  ], { x: 0.6, y: 5.25, w: 12.1, h: 0.7, fontFace: BFONT, fontSize: 15, align: "center", valign: "middle", margin: 0, fill: { color: C.section } });
  footer(s, 2);

  // ============================================================= 3 — RJEŠENJE
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Predloženo rješenje");
  title(s, "Jedan alat — od podataka do narudžbenice");
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.95, w: 5.9, h: 1.5, rectRadius: 0.12, fill: { color: C.section }, line: { color: C.border, width: 1 } });
  s.addText("Sistem koji predviđa potražnju i preporučuje tačnu količinu narudžbe — sa objašnjenjem i simulacijom scenarija.", {
    x: 0.95, y: 2.2, w: 5.3, h: 1.05, fontFace: BFONT, fontSize: 17, color: C.navy, italic: true, margin: 0, valign: "middle", lineSpacing: 23,
  });
  const pills = [
    ["Forecast", C.blue], ["Optimizacija zaliha", C.sky], ["Objašnjenja", C.green], ["Narudžbenica", C.navy2],
  ];
  // dva reda da staju u lijevi panel (≤ 6.1 in širine, prije screenshot-a na x=7.0)
  const pillRows = [[pills[0], pills[1]], [pills[2], pills[3]]];
  pillRows.forEach((row, ri) => {
    let px = 0.6;
    const py = 3.7 + ri * 0.66;
    row.forEach(([t, c]) => {
      const w = 0.34 + t.length * 0.088;
      s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: px, y: py, w, h: 0.5, rectRadius: 0.25, fill: { color: c }, line: { type: "none" } });
      s.addText(t, { x: px, y: py, w, h: 0.5, fontFace: HFONT, fontSize: 11.5, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
      px += w + 0.18;
    });
  });
  s.addText("Sve kroz čist dashboard — bez pisanja koda. Korisnik dobije prognozu s rasponom, preporučenu količinu i Excel narudžbenicu.", {
    x: 0.6, y: 5.1, w: 6, h: 1.3, fontFace: BFONT, fontSize: 14, color: C.slate, margin: 0, lineSpacing: 20,
  });
  // desno — placeholder za screenshot Forecast prikaza
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 7.0, y: 1.95, w: 5.73, h: 4.55, rectRadius: 0.1, fill: { color: C.section }, line: { color: C.border, width: 1.5 }, shadow: sh() });
  s.addShape(p.shapes.RECTANGLE, { x: 7.0, y: 1.95, w: 5.73, h: 0.42, fill: { color: C.navy }, line: { type: "none" } });
  s.addShape(p.shapes.OVAL, { x: 7.22, y: 2.07, w: 0.16, h: 0.16, fill: { color: "FF5F57" }, line: { type: "none" } });
  s.addShape(p.shapes.OVAL, { x: 7.45, y: 2.07, w: 0.16, h: 0.16, fill: { color: "FEBC2E" }, line: { type: "none" } });
  s.addShape(p.shapes.OVAL, { x: 7.68, y: 2.07, w: 0.16, h: 0.16, fill: { color: "28C840" }, line: { type: "none" } });
  s.addText("[ SCREENSHOT: Forecast prikaz — linija prodaje + interval pouzdanosti ]", {
    x: 7.3, y: 3.8, w: 5.1, h: 0.9, fontFace: BFONT, fontSize: 13, color: C.slate2, align: "center", valign: "middle", italic: true, margin: 0,
  });
  footer(s, 3);

  // ============================================================= 4 — CILJEVI
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Ciljevi projekta");
  title(s, "Šta sam želio da postignem");
  // glavni cilj kartica
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.95, w: 12.13, h: 1.15, rectRadius: 0.12, fill: { color: C.navy }, line: { type: "none" }, shadow: sh() });
  iconBadge(s, I.target, 0.95, 2.22, 0.6, C.blue);
  s.addText([
    { text: "GLAVNI CILJ   ", options: { color: C.sky, bold: true, fontSize: 12, charSpacing: 2 } },
    { text: "Pretvoriti istoriju prodaje u konkretnu preporuku narudžbe", options: { color: C.white, bold: true, fontSize: 18 } },
  ], { x: 1.75, y: 1.95, w: 10.8, h: 1.15, fontFace: HFONT, valign: "middle", margin: 0 });
  // 4 podcilja
  const goals = [
    ["Tačan forecast", "po proizvodu i prodavnici, s intervalom pouzdanosti"],
    ["Optimalna količina", "EOQ, safety stock i reorder point"],
    ["Transparentnost", "SHAP objašnjava zašto baš toliko"],
    ["What-if simulacija", "promocija, cijena, lead time"],
  ];
  goals.forEach((g, i) => {
    const x = 0.6 + i * 3.06;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 3.4, w: 2.86, h: 2.65, rectRadius: 0.12, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.OVAL, { x: x + 0.3, y: 3.7, w: 0.66, h: 0.66, fill: { color: C.blue }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + 0.3, y: 3.7, w: 0.66, h: 0.66, fontFace: HFONT, fontSize: 22, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(g[0], { x: x + 0.3, y: 4.55, w: 2.3, h: 0.5, fontFace: HFONT, fontSize: 16, color: C.navy, bold: true, margin: 0 });
    s.addText(g[1], { x: x + 0.3, y: 5.05, w: 2.4, h: 0.9, fontFace: BFONT, fontSize: 12.5, color: C.slate, margin: 0, lineSpacing: 17 });
  });
  footer(s, 4);

  // ============================================================= 5 — KAKO RADI (flow)
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Kako sistem funkcioniše");
  title(s, "Od podataka do odluke — u pet koraka");
  const steps = [
    ["CSV / demo\npodaci", "učitavanje"],
    ["Čišćenje +\nfeature eng.", "29 feature-a"],
    ["ML modeli +\nintervali", "LightGBM, HW"],
    ["Optimizacija\nzaliha", "EOQ, SS, ROP"],
    ["Narudžbenica\n+ export", "CSV / Excel"],
  ];
  const cw = 2.18, stepX0 = 0.55, gap = 0.31;
  steps.forEach((st, i) => {
    const x = stepX0 + i * (cw + gap);
    const filled = i === 2;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.9, w: cw, h: 1.9, rectRadius: 0.12, fill: { color: filled ? C.blue : C.section }, line: { color: filled ? C.blue : C.border, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.OVAL, { x: x + cw / 2 - 0.28, y: 2.62, w: 0.56, h: 0.56, fill: { color: filled ? C.navy : C.blue }, line: { color: C.white, width: 2 } });
    s.addText(String(i + 1), { x: x + cw / 2 - 0.28, y: 2.62, w: 0.56, h: 0.56, fontFace: HFONT, fontSize: 18, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(st[0], { x: x + 0.1, y: 3.35, w: cw - 0.2, h: 0.8, fontFace: HFONT, fontSize: 14.5, color: filled ? C.white : C.navy, bold: true, align: "center", valign: "middle", margin: 0, lineSpacing: 17 });
    s.addText(st[1], { x: x + 0.1, y: 4.2, w: cw - 0.2, h: 0.4, fontFace: BFONT, fontSize: 11.5, color: filled ? C.ice : C.slate, align: "center", margin: 0 });
    if (i < steps.length - 1) {
      s.addText("›", { x: x + cw - 0.02, y: 3.35, w: gap + 0.04, h: 0.9, fontFace: HFONT, fontSize: 26, color: C.slate2, align: "center", valign: "middle", margin: 0 });
    }
  });
  s.addText("Korisnik prati svaki korak kroz zasebne prikaze u dashboardu.", {
    x: 0.55, y: 5.4, w: 12.2, h: 0.5, fontFace: BFONT, fontSize: 14, color: C.slate, align: "center", italic: true, margin: 0,
  });
  footer(s, 5);

  // ============================================================= 6 — FUNKCIONALNOSTI
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Glavne funkcionalnosti");
  title(s, "Šest stubova aplikacije");
  const feats = [
    [I.chart, C.blue, "Forecast", "Prognoza potražnje sa intervalom pouzdanosti"],
    [I.box, C.sky, "Optimizacija zaliha", "EOQ, safety stock i reorder point"],
    [I.warn, C.red, "Detekcija anomalija", "Automatsko otkrivanje skokova i padova"],
    [I.search, C.green, "SHAP objašnjenja", "Koji faktori najviše utiču na potražnju"],
    [I.sliders, C.amber, "What-if simulacija", "Promocija, cijena i lead time scenariji"],
    [I.invoice, C.navy2, "Narudžbenica", "Automatski izvještaj + Excel / CSV export"],
  ];
  feats.forEach((f, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.6 + col * 4.05, y = 1.95 + row * 2.15;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.78, h: 1.92, rectRadius: 0.12, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
    iconBadge(s, f[0], x + 0.32, y + 0.3, 0.6, f[1]);
    s.addText(f[2], { x: x + 1.1, y: y + 0.32, w: 2.55, h: 0.58, fontFace: HFONT, fontSize: 16, color: C.navy, bold: true, valign: "middle", margin: 0 });
    s.addText(f[3], { x: x + 0.32, y: y + 1.02, w: 3.2, h: 0.75, fontFace: BFONT, fontSize: 12.5, color: C.slate, margin: 0, lineSpacing: 17 });
  });
  footer(s, 6);

  // ============================================================= 7 — TEHNOLOGIJE
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Tehnologije");
  title(s, "Tehnološki stack");
  const techRows = [
    [I.chart, "Frontend / UI", "Streamlit + Plotly", "Brz, interaktivni dashboard bez klasičnog web razvoja"],
    [I.code, "Logika / podaci", "Python · pandas · numpy", "Standard za obradu tabelarnih podataka"],
    [I.brain, "Machine Learning", "LightGBM · scikit-learn · statsmodels", "Tačni i brzi modeli za tabelarne vremenske serije"],
    [I.flask, "Objašnjivost", "SHAP", "Egzaktno objašnjenje svake predikcije"],
    [I.db, "Export", "openpyxl", "Narudžbenica direktno u Excel"],
  ];
  techRows.forEach((r, i) => {
    const y = 1.95 + i * 0.95;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 12.13, h: 0.82, rectRadius: 0.08, fill: { color: i % 2 ? C.white : C.section }, line: { color: C.border, width: 1 } });
    iconBadge(s, r[0] === I.chart ? I.chart : r[0], 0.8, y + 0.11, 0.6, C.blue);
    s.addText(r[1], { x: 1.6, y, w: 2.5, h: 0.82, fontFace: HFONT, fontSize: 14, color: C.slate, bold: true, valign: "middle", margin: 0 });
    s.addText(r[2], { x: 4.1, y, w: 4.0, h: 0.82, fontFace: HFONT, fontSize: 14.5, color: C.navy, bold: true, valign: "middle", margin: 0 });
    s.addText(r[3], { x: 8.2, y, w: 4.4, h: 0.82, fontFace: BFONT, fontSize: 12.5, color: C.slate, valign: "middle", margin: 0, lineSpacing: 16 });
  });
  footer(s, 7);

  // ============================================================= 8 — ARHITEKTURA
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Arhitektura sistema");
  title(s, "Modularno i pregledno");
  // Korisnik
  function flowBox(x, y, w, h, txt, sub, fill, txtcol, subcol) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: fill === C.white ? C.border : fill, width: 1 }, shadow: sh() });
    s.addText(txt, { x, y: sub ? y + 0.12 : y, w, h: sub ? h - 0.4 : h, fontFace: HFONT, fontSize: 15, color: txtcol, bold: true, align: "center", valign: "middle", margin: 0 });
    if (sub) s.addText(sub, { x, y: y + h - 0.42, w, h: 0.34, fontFace: BFONT, fontSize: 11, color: subcol, align: "center", margin: 0 });
  }
  flowBox(4.9, 1.85, 3.5, 0.62, "Korisnik", null, C.navy, C.white);
  s.addText("↓  upload CSV · izbor proizvoda", { x: 4.9, y: 2.48, w: 3.5, h: 0.3, fontFace: BFONT, fontSize: 10.5, color: C.slate, align: "center", margin: 0 });
  flowBox(3.9, 2.82, 5.5, 0.62, "Streamlit dashboard  +  Plotly grafici", null, C.blue, C.white);
  s.addText("↓", { x: 6.4, y: 3.44, w: 0.5, h: 0.3, fontFace: HFONT, fontSize: 16, color: C.slate2, align: "center", margin: 0 });
  // 7 modula
  s.addText("src /  Python moduli", { x: 0.6, y: 3.78, w: 12.13, h: 0.3, fontFace: HFONT, fontSize: 12, color: C.slate, bold: true, align: "center", charSpacing: 1, margin: 0 });
  const mods = [
    ["data_processing", "čišćenje"],
    ["feature_eng.", "29 feature-a"],
    ["forecasting", "LightGBM + HW"],
    ["inventory_opt.", "EOQ · SS · ROP"],
    ["anomaly_detect.", "Isolation Forest"],
    ["explainability", "SHAP"],
    ["order_generator", "narudžbenica"],
  ];
  const mw = 1.66, mg = 0.14, mx0 = (W - (7 * mw + 6 * mg)) / 2;
  mods.forEach((m, i) => {
    const x = mx0 + i * (mw + mg);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 4.2, w: mw, h: 1.15, rectRadius: 0.09, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 4.2, w: mw, h: 0.07, fill: { color: C.sky }, line: { type: "none" } });
    s.addText(m[0], { x: x + 0.05, y: 4.42, w: mw - 0.1, h: 0.5, fontFace: HFONT, fontSize: 11.5, color: C.navy, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(m[1], { x: x + 0.05, y: 4.92, w: mw - 0.1, h: 0.35, fontFace: BFONT, fontSize: 9.5, color: C.slate, align: "center", margin: 0 });
  });
  s.addText("↓", { x: 6.4, y: 5.42, w: 0.5, h: 0.3, fontFace: HFONT, fontSize: 16, color: C.slate2, align: "center", margin: 0 });
  flowBox(4.5, 5.78, 4.3, 0.62, "Izlaz:  tabela + CSV / Excel", null, C.green, C.white);
  footer(s, 8);

  // ============================================================= 9 — TEHNIČKE ODLUKE
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Ključne tehničke odluke");
  title(s, "Tri odluke koje su napravile razliku");
  const dec = [
    ["Data leakage", "shift(1) na rolling feature-ima; izbačena kolona Customers (same-day informacija).", "Model ne vidi budućnost"],
    ["Pošteno mjerenje", "Rekurzivni forecast + rolling-origin kros-validacija na neviđenim prozorima.", "Realna, ne lažna tačnost"],
    ["Intervali pouzdanosti", "Quantile LightGBM (10% / 90% percentil) umjesto jedne tačke.", "Raspon, ne lažna preciznost"],
  ];
  dec.forEach((d, i) => {
    const x = 0.6 + i * 4.05;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.0, w: 3.78, h: 3.9, rectRadius: 0.12, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
    // izazov header
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.0, w: 3.78, h: 0.95, rectRadius: 0.12, fill: { color: C.navy }, line: { type: "none" } });
    s.addShape(p.shapes.RECTANGLE, { x, y: 2.55, w: 3.78, h: 0.4, fill: { color: C.navy }, line: { type: "none" } });
    s.addText("IZAZOV", { x: x + 0.3, y: 2.12, w: 3.2, h: 0.3, fontFace: HFONT, fontSize: 10.5, color: C.sky, bold: true, charSpacing: 2, margin: 0 });
    s.addText(d[0], { x: x + 0.3, y: 2.4, w: 3.2, h: 0.5, fontFace: HFONT, fontSize: 18, color: C.white, bold: true, margin: 0 });
    s.addText("RJEŠENJE", { x: x + 0.3, y: 3.2, w: 3.2, h: 0.3, fontFace: HFONT, fontSize: 10.5, color: C.green, bold: true, charSpacing: 2, margin: 0 });
    s.addText(d[1], { x: x + 0.3, y: 3.5, w: 3.2, h: 1.5, fontFace: BFONT, fontSize: 13.5, color: C.navy, margin: 0, lineSpacing: 19 });
    s.addImage({ data: I.check, x: x + 0.3, y: 5.18, w: 0.32, h: 0.32 });
    s.addText(d[2], { x: x + 0.7, y: 5.16, w: 2.9, h: 0.4, fontFace: BFONT, fontSize: 12, color: C.green, bold: true, valign: "middle", margin: 0 });
  });
  s.addText("Bonus: Prophet ne radi na Python 3.13 → napravljen opcionim, ulogu sezonskog modela preuzima Holt-Winters u ensemble-u.", {
    x: 0.6, y: 6.1, w: 12.13, h: 0.5, fontFace: BFONT, fontSize: 12.5, color: C.slate, align: "center", italic: true, margin: 0,
  });
  footer(s, 9);

  // ============================================================= 10 — LIVE DEMO (divider)
  s = p.addSlide();
  s.background = { color: C.navy };
  s.addShape(p.shapes.OVAL, { x: -1.5, y: 4.5, w: 5, h: 5, fill: { color: C.blue, transparency: 84 }, line: { type: "none" } });
  iconBadge(s, I.play, 0.9, 1.5, 0.85, C.blue);
  s.addText("LIVE DEMO", { x: 0.9, y: 2.55, w: 8, h: 0.9, fontFace: HFONT, fontSize: 44, color: C.white, bold: true, margin: 0 });
  s.addText("Kompletan tok rada — uživo u aplikaciji  ·  ~3 minuta", { x: 0.92, y: 3.5, w: 9, h: 0.5, fontFace: BFONT, fontSize: 17, color: C.ice, italic: true, margin: 0 });
  const demoSteps = ["Prognoza\n+ interval", "Optimizacija\nzaliha", "What-if\npromocija", "Narudžbenica\n+ Excel"];
  demoSteps.forEach((d, i) => {
    const x = 0.9 + i * 2.95;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 4.7, w: 2.65, h: 1.5, rectRadius: 0.12, fill: { color: C.navy2 }, line: { color: C.blue, width: 1.2 } });
    s.addShape(p.shapes.OVAL, { x: x + 0.25, y: 4.92, w: 0.5, h: 0.5, fill: { color: C.blue }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + 0.25, y: 4.92, w: 0.5, h: 0.5, fontFace: HFONT, fontSize: 16, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(d, { x: x + 0.85, y: 4.88, w: 1.7, h: 1.1, fontFace: HFONT, fontSize: 13.5, color: C.white, bold: true, valign: "middle", margin: 0, lineSpacing: 16 });
  });
  footer(s, 10, true);

  // ============================================================= 11 — REZULTATI
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Rezultati i vrijednost");
  title(s, "Mjerljivo bolje od ručnog planiranja");
  // chart MAPE
  s.addText("Greška prognoze (MAPE %) — backtest na 28 dana, manje je bolje", {
    x: 0.6, y: 1.9, w: 7, h: 0.35, fontFace: BFONT, fontSize: 12.5, color: C.slate, bold: true, margin: 0,
  });
  s.addChart(p.charts.BAR, [{
    name: "MAPE", labels: ["Baseline (MA)", "Sezonski naivni", "LightGBM", "Ensemble"], values: [52, 37, 19, 19],
  }], {
    x: 0.5, y: 2.3, w: 7.2, h: 4.0, barDir: "bar",
    chartColors: [C.red, C.amber, C.green, C.green],
    chartArea: { fill: { color: C.white } },
    catAxisLabelColor: C.navy, catAxisLabelFontSize: 12, catAxisLabelFontFace: BFONT,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.navy, dataLabelFontSize: 13, dataLabelFontBold: true,
    dataLabelFormatCode: '0"%"',
    showLegend: false, showTitle: false, barGapWidthPct: 55,
  });
  // desno — koristi + KPI
  const kpis = [
    ["~14%", "MAPE — rolling-origin CV (LightGBM)", C.blue],
    ["26 / 26", "modula prošlo automatski test", C.green],
    [">2×", "manja greška od naivnog pristupa", C.sky],
  ];
  kpis.forEach((k, i) => {
    const y = 2.25 + i * 1.18;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 8.05, y, w: 4.68, h: 1.0, rectRadius: 0.1, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
    s.addText(k[0], { x: 8.25, y, w: 1.7, h: 1.0, fontFace: HFONT, fontSize: 26, color: k[2], bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(k[1], { x: 9.95, y, w: 2.65, h: 1.0, fontFace: BFONT, fontSize: 12.5, color: C.navy, valign: "middle", margin: 0, lineSpacing: 16 });
  });
  s.addText("Niži troškovi zaliha  ·  manje stockout-a  ·  brže i objašnjivo odlučivanje", {
    x: 8.05, y: 5.85, w: 4.68, h: 0.5, fontFace: BFONT, fontSize: 12, color: C.slate, italic: true, valign: "middle", margin: 0, lineSpacing: 16,
  });
  s.addText("* Rezultati su demonstracioni — dobijeni na sintetičkim podacima. Metodologija je identična na realnim podacima.", {
    x: 0.6, y: 6.55, w: 12.13, h: 0.35, fontFace: BFONT, fontSize: 10.5, color: C.slate2, italic: true, margin: 0,
  });
  footer(s, 11);

  // ============================================================= 12 — OGRANIČENJA / BUDUĆNOST
  s = p.addSlide();
  s.background = { color: C.white };
  kicker(s, "Ograničenja i budući razvoj");
  title(s, "Šta dalje");
  // sada
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 2.0, w: 5.5, h: 4.0, rectRadius: 0.12, fill: { color: C.section }, line: { color: C.border, width: 1 }, shadow: sh() });
  s.addText("TRENUTNA OGRANIČENJA", { x: 0.95, y: 2.3, w: 4.9, h: 0.4, fontFace: HFONT, fontSize: 14, color: C.slate, bold: true, charSpacing: 1.5, margin: 0 });
  [
    "Single-series modeli (model po proizvodu)",
    "Demo podaci su sintetički",
    "File-based ulaz/izlaz, bez baze",
    "Pojednostavljena elastičnost u what-if",
    "Bez autentikacije / više korisnika",
  ].forEach((t, i) => {
    s.addText(t, { x: 1.0, y: 2.85 + i * 0.6, w: 4.9, h: 0.5, fontFace: BFONT, fontSize: 13.5, color: C.navy, bullet: { code: "2013", indent: 14 }, margin: 0, valign: "middle" });
  });
  // strelica
  s.addText("→", { x: 6.15, y: 3.7, w: 1.0, h: 0.6, fontFace: HFONT, fontSize: 34, color: C.blue, align: "center", valign: "middle", bold: true, margin: 0 });
  // sljedeće
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 7.23, y: 2.0, w: 5.5, h: 4.0, rectRadius: 0.12, fill: { color: C.navy }, line: { type: "none" }, shadow: sh() });
  s.addText("BUDUĆI RAZVOJ", { x: 7.58, y: 2.3, w: 4.9, h: 0.4, fontFace: HFONT, fontSize: 14, color: C.sky, bold: true, charSpacing: 1.5, margin: 0 });
  [
    "Napredni modeli: LSTM / DeepAR / TFT",
    "Hijerarhijski forecast + reconciliation",
    "Baza podataka + live ingestion",
    "Optimizacija kalendara promocija",
    "A/B test: preporuke vs stvarne narudžbe",
  ].forEach((t, i) => {
    s.addText(t, { x: 7.63, y: 2.85 + i * 0.6, w: 4.9, h: 0.5, fontFace: BFONT, fontSize: 13.5, color: C.ice, bullet: { code: "2013", indent: 14 }, margin: 0, valign: "middle" });
  });
  s.addText("Modularna arhitektura omogućava dogradnju bez prepravke cijelog sistema.", {
    x: 0.6, y: 6.25, w: 12.13, h: 0.4, fontFace: BFONT, fontSize: 13, color: C.slate, align: "center", italic: true, margin: 0,
  });
  footer(s, 12);

  // ============================================================= 13 — ZAKLJUČAK
  s = p.addSlide();
  s.background = { color: C.navy };
  s.addShape(p.shapes.OVAL, { x: 9.8, y: 3.2, w: 6, h: 6, fill: { color: C.blue, transparency: 85 }, line: { type: "none" } });
  s.addText("ZAKLJUČAK", { x: 0.9, y: 1.3, w: 8, h: 0.4, fontFace: HFONT, fontSize: 13, color: C.sky, charSpacing: 3, bold: true, margin: 0 });
  s.addText("„Koliko da naručimo?“\nSada imamo odgovor.", {
    x: 0.9, y: 1.8, w: 11, h: 1.7, fontFace: HFONT, fontSize: 40, color: C.white, bold: true, lineSpacing: 44, margin: 0,
  });
  const concl = [
    ["Problem", "skup višak ili manjak zaliha", C.red],
    ["Rješenje", "forecast + EOQ + objašnjenje + narudžbenica — u jednom alatu", C.sky],
    ["Vrijednost", "niži troškovi, manje stockout-a, brže i objašnjivo odlučivanje", C.green],
  ];
  concl.forEach((c, i) => {
    const y = 3.85 + i * 0.66;
    s.addShape(p.shapes.OVAL, { x: 0.95, y: y + 0.06, w: 0.16, h: 0.16, fill: { color: c[2] }, line: { type: "none" } });
    s.addText([
      { text: c[0] + ":  ", options: { color: C.white, bold: true } },
      { text: c[1], options: { color: C.ice } },
    ], { x: 1.3, y, w: 10.8, h: 0.45, fontFace: BFONT, fontSize: 15.5, valign: "middle", margin: 0 });
  });
  s.addText("Hvala na pažnji   ·   Pitanja?", {
    x: 0.9, y: 6.1, w: 11, h: 0.7, fontFace: HFONT, fontSize: 26, color: C.white, bold: true, margin: 0,
  });
  footer(s, 13, true);

  await p.writeFile({ fileName: "Odbrana_Demand_Forecasting.pptx" });
  console.log("OK — Odbrana_Demand_Forecasting.pptx");
})();

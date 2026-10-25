"""
¿Dónde abrir un café en Bogotá? · SP Lab · v1 (nivel localidad)
Fuentes:
  - Oferta: Dinámica Empresarial Bogotá (Datos Abiertos Bogotá, corte mar 2026, CC BY-SA 4.0), base limpia del caso
    "Radiografía del emprendimiento" (00_datos_limpios.csv).
  - Demanda: Proyecciones de población por localidad 2005-2035 (Datos Abiertos Bogotá / SDP, CC BY 4.0), año 2026.
Uso: python analisis_cafe.py <datos_limpios_empresas.csv> <poblacion_localidad.csv> <carpeta_salida>
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

EMP, POB, OUT = sys.argv[1:4]
for sub in ["tablas", "graficos"]:
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

# ---------- 1. Oferta: competencia directa ----------
emp = pd.read_csv(EMP, dtype={"ciiu": str})
COMP = {"5613": "cafeterias", "1081": "panaderias"}  # en Bogotá la panadería de barrio también vende café
of = (emp[emp.ciiu.isin(COMP)]
      .assign(tipo=lambda x: x.ciiu.map(COMP))
      .pivot_table(index="localidad", columns="tipo", values=["vigentes", "creadas"], aggfunc="sum", fill_value=0))
of.columns = [f"{t}_{m}" for m, t in of.columns]
of["competidores"] = of.cafeterias_vigentes + of.panaderias_vigentes
of["competidores_nuevos"] = of.cafeterias_creadas + of.panaderias_creadas
emp_tot = emp.groupby("localidad").vigentes.sum().rename("empresas_vigentes")

# ---------- 2. Demanda: población 2026 ----------
p = pd.read_csv(POB, sep=";", encoding="utf-8-sig")
p = p[p.ANO == 2026]
dem = pd.DataFrame({
    "poblacion_2026": p.groupby("NOMBRE_LOCALIDAD").POBLACION.sum(),
    "adultos_2026": p[p.EDAD >= 18].groupby("NOMBRE_LOCALIDAD").POBLACION.sum(),
})
bog = dem.loc["Bogotá"]
dem = dem.drop("Bogotá")
assert dem.poblacion_2026.sum() == bog.poblacion_2026, "Las localidades no suman el total de Bogotá"

# ---------- 3. Cruce e indicadores ----------
t = dem.join(of, how="left").join(emp_tot, how="left")
t = t.drop(index="Sumapaz")  # rural, sin datos en la base de empresas
t["adultos_por_competidor"] = t.adultos_2026 / t.competidores
t["empresas_por_competidor"] = t.empresas_vigentes / t.competidores
t["competidores_por_10mil_adultos"] = t.competidores / t.adultos_2026 * 1e4
t["tasa_entrada_pct"] = t.competidores_nuevos / t.competidores * 100

z = lambda s: (s - s.mean()) / s.std(ddof=0)
PESOS = {"adultos_por_competidor": 0.5, "empresas_por_competidor": 0.3, "tasa_entrada_pct": -0.2}
t["indice_oportunidad"] = sum(w * z(t[c]) for c, w in PESOS.items())
t = t.sort_values("indice_oportunidad", ascending=False)
t["ranking"] = range(1, len(t) + 1)

ciudad = pd.Series({
    "adultos_por_competidor": t.adultos_2026.sum() / t.competidores.sum(),
    "empresas_por_competidor": t.empresas_vigentes.sum() / t.competidores.sum(),
    "tasa_entrada_pct": t.competidores_nuevos.sum() / t.competidores.sum() * 100,
})

# Sensibilidad: ¿cambia el top 3 con otros pesos?
escenarios = {
    "base (0,5 / 0,3 / -0,2)": PESOS,
    "solo residentes": {"adultos_por_competidor": 1.0},
    "solo demanda diurna": {"empresas_por_competidor": 1.0},
    "iguales (1/3 c/u)": {"adultos_por_competidor": 1/3, "empresas_por_competidor": 1/3, "tasa_entrada_pct": -1/3},
}
sens = pd.DataFrame({k: sum(w * z(t[c]) for c, w in v.items()).rank(ascending=False).astype(int) for k, v in escenarios.items()})
sens = sens.sort_values("base (0,5 / 0,3 / -0,2)")

cols = ["ranking", "indice_oportunidad", "poblacion_2026", "adultos_2026", "empresas_vigentes",
        "cafeterias_vigentes", "panaderias_vigentes", "competidores", "competidores_nuevos",
        "adultos_por_competidor", "empresas_por_competidor", "competidores_por_10mil_adultos", "tasa_entrada_pct"]
with pd.ExcelWriter(os.path.join(OUT, "tablas", "resultados_donde_abrir_cafe.xlsx")) as xw:
    t[cols].round(2).to_excel(xw, "01_ranking_localidades")
    ciudad.round(2).rename("Bogotá").to_frame().to_excel(xw, "02_referencia_bogota")
    sens.to_excel(xw, "03_sensibilidad_pesos")
    pd.DataFrame({"indicador": list(PESOS), "peso": list(PESOS.values()),
                  "lectura": ["más adultos por punto = menos saturación residencial",
                              "más empresas por punto = más demanda diurna (oficinas, comercio)",
                              "más entrada de competidores = mercado que se está llenando"]}).to_excel(xw, "04_metodo", index=False)
t[cols].round(3).to_csv(os.path.join(OUT, "tablas", "ranking_localidades.csv"), encoding="utf-8-sig")

# ---------- 4. Gráficos (paleta SP Lab) ----------
for f in fm.findSystemFonts():
    if "Inter" in f:
        fm.fontManager.addfont(f)
plt.rcParams.update({"font.family": "Inter", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "#F8FAF7", "axes.facecolor": "#F8FAF7"})
VERDE, GRIS, CARBON, DORADO, NEUTRO = "#245B45", "#66736C", "#202824", "#D6A64F", "#B9C2BC"
fmt = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
pie_txt = ("Fuentes: Datos Abiertos Bogotá — Dinámica Empresarial (mar 2026, CC BY-SA 4.0) y proyecciones de población "
           "por localidad 2026 (CC BY 4.0) · Análisis: Sebas Padilla Lab")
cuad = t[(t.adultos_por_competidor > ciudad.adultos_por_competidor) & (t.empresas_por_competidor > ciudad.empresas_por_competidor)].index
top3 = cuad  # resaltado: localidades por encima de Bogotá en ambas demandas

def encabezado(fig, ti, sub):
    fig.text(0.02, 0.965, ti, fontsize=15, fontweight="bold", color=CARBON, va="top")
    fig.text(0.02, 0.91, sub, fontsize=10.5, color=GRIS, va="top")
    fig.text(0.02, 0.02, pie_txt, fontsize=7.5, color=GRIS)

# 4.1 Matriz demanda residencial vs demanda diurna por punto
fig, ax = plt.subplots(figsize=(9.5, 7.4)); fig.subplots_adjust(left=0.1, right=0.95, top=0.84, bottom=0.12)
sz = t.adultos_2026 / t.adultos_2026.max() * 900 + 40
ax.scatter(t.adultos_por_competidor, t.empresas_por_competidor, s=sz,
           c=[VERDE if i in top3 else NEUTRO for i in t.index], alpha=0.85, edgecolor="white", lw=1, zorder=3)
ax.axvline(ciudad.adultos_por_competidor, color=DORADO, ls="--", lw=1.3, zorder=1)
ax.axhline(ciudad.empresas_por_competidor, color=DORADO, ls="--", lw=1.3, zorder=1)
ax.text(ciudad.adultos_por_competidor + 8, ax.get_ylim()[1] * 0.97, f"Bogotá: {fmt(ciudad.adultos_por_competidor)} adultos por punto",
        color="#9A7425", fontsize=8.5, va="top")
ax.text(ax.get_xlim()[1] * 0.995, ciudad.empresas_por_competidor - 1.0, f"Bogotá: {fmt(ciudad.empresas_por_competidor)} empresas por punto",
        color="#9A7425", fontsize=8.5, ha="right", va="top")
OFF = {"Ciudad Bolívar": (4, 14), "Bosa": (-16, -18), "Usme": (6, -12), "Kennedy": (6, 4), "Suba": (8, 4), "Engativá": (6, -12),
       "Rafael Uribe Uribe": (6, 4), "San Cristóbal": (6, -12), "Tunjuelito": (-6, -14), "Fontibón": (6, 4),
       "Usaquén": (6, 4), "Puente Aranda": (6, -12), "Antonio Nariño": (6, 4), "Los Mártires": (6, 4),
       "Santa Fe": (6, -12), "La Candelaria": (6, 4), "Teusaquillo": (6, -12), "Barrios Unidos": (6, 4), "Chapinero": (6, 4)}
for loc, r in t.iterrows():
    dx, dy = OFF.get(loc, (6, 4))
    ax.annotate(loc, (r.adultos_por_competidor, r.empresas_por_competidor), xytext=(dx, dy), textcoords="offset points",
                fontsize=8.8, color=CARBON if loc in top3 else GRIS, fontweight="bold" if loc in top3 else "normal",
                ha="right" if dx < 0 else "left")
ax.set_xlabel("Adultos que viven en la localidad por cada cafetería o panadería", color=GRIS)
ax.set_ylabel("Empresas vigentes por cada cafetería o panadería", color=GRIS)
ax.tick_params(colors=GRIS); ax.spines["left"].set_color("#C9CFCB"); ax.spines["bottom"].set_color("#C9CFCB")
ax.xaxis.set_major_formatter(lambda v, _: fmt(v)); ax.yaxis.set_major_formatter(lambda v, _: fmt(v))
encabezado(fig, f"Solo {' y '.join(cuad)} superan a Bogotá en las dos demandas por punto de café",
           "Adultos y empresas por cada cafetería o panadería. Tamaño = adultos 2026; líneas = promedio de Bogotá")
fig.savefig(os.path.join(OUT, "graficos", "01_matriz_demanda_competencia.png"), dpi=200); plt.close(fig)

# 4.2 Dos modelos de café: barrio (residentes) frente a oficina (demanda diurna)
fig, axes = plt.subplots(1, 2, figsize=(10, 6.6)); fig.subplots_adjust(left=0.15, right=0.97, top=0.8, bottom=0.08, wspace=0.75)
for ax, col, ref, nom in [(axes[0], "adultos_por_competidor", ciudad.adultos_por_competidor, "Café de barrio\nadultos por punto de café"),
                          (axes[1], "empresas_por_competidor", ciudad.empresas_por_competidor, "Café de oficina\nempresas por punto de café")]:
    r = t[col].sort_values(ascending=False).head(8).iloc[::-1]
    ax.barh(r.index, r.values, color=[VERDE if i in cuad else NEUTRO for i in r.index], height=0.66)
    ax.axvline(ref, color=DORADO, ls="--", lw=1.3)
    for k, v in enumerate(r.values):
        ax.text(v * 1.02, k, fmt(v), va="center", fontsize=9, color=CARBON,
                bbox=dict(facecolor="#F8FAF7", edgecolor="none", pad=0.5))
    ax.set_title(nom, loc="left", fontsize=11, color=CARBON, fontweight="bold")
    ax.set_xticks([]); ax.tick_params(axis="y", length=0, colors=CARBON)
    for sp in ["left", "bottom"]: ax.spines[sp].set_visible(False)
    ax.set_xlim(0, r.max() * 1.22)
    ax.text(ref, -0.95, f"Bogotá {fmt(ref)}", color="#9A7425", fontsize=8.5, ha="center")
encabezado(fig, "El mejor lugar depende del tipo de café",
           "Las 8 localidades con menos competencia por punto en cada modelo. Verde = arriba del promedio en ambos")
fig.savefig(os.path.join(OUT, "graficos", "02_dos_modelos_de_cafe.png"), dpi=200); plt.close(fig)

print(t[cols].round(2).to_string()); print(ciudad.round(2)); print(sens.to_string())

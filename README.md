# ¿Dónde abrir un café en Bogotá? · v1

**Sebas Padilla Lab · Pilar Market Intelligence · Versión 1 (25 oct 2026)**

> **Pregunta:** ¿En qué localidad de Bogotá conviene abrir un café: dónde hay más demanda por cada punto de café que ya existe?

## English summary
**Where should you open a café in Bogotá?** Location-intelligence analysis crossing registered coffee shops and bakeries (competition) with 2026 adult population and active businesses (demand) across Bogotá's 19 urban localities. Only Suba and Usaquén beat the city average on both residential and daytime demand per coffee outlet; the best spot depends on the business model (neighborhood café vs. office café). A weighted opportunity index is reported with a sensitivity test showing it is not robust to weights. Python · pandas · matplotlib.

## En 30 segundos
- En las 19 localidades urbanas de Bogotá hay **9.338 puntos de café con localidad asignada** (3.688 cafeterías + 5.650 panaderías). Hay **668 adultos** y **47 empresas** por cada uno.
- **Solo Suba y Usaquén superan el promedio de la ciudad en las dos demandas**: la de quienes viven en la localidad y la de quienes trabajan allí. Son las apuestas más equilibradas.
  - Suba: 887 adultos y 51 empresas por punto; es la localidad más poblada (1,25 millones de habitantes).
  - Usaquén: 773 adultos y 76 empresas por punto.
- **El mejor lugar depende del tipo de café:**
  - *Café de barrio* (vive de residentes): Usme (1.142 adultos por punto), Ciudad Bolívar (1.088) y Bosa (1.005) son las menos saturadas.
  - *Café de oficina* (vive de quienes trabajan en la zona): Chapinero (116 empresas por punto) y Usaquén (76).
- **Las más saturadas:** La Candelaria (94 adultos por punto, 106 puntos por cada 10.000 adultos) y Los Mártires (163). Sin embargo, su población flotante (turistas, comercio) no aparece en estos datos.
- **La competencia que más entra:** en Rafael Uribe Uribe (8,0 %) y Tunjuelito (7,3 %) se crearon más puntos de café nuevos en el trimestre, en proporción a los existentes. Bogotá: 5,1 %.

## Recomendación
1. **Si el modelo es mixto (barrio + trabajo): Suba o Usaquén.** Son las únicas localidades por encima del promedio en ambas demandas.
2. **Si es un café de barrio con precio accesible: Usme, Ciudad Bolívar o Bosa.** Tienen mucha gente por punto, pero hay que validar el poder adquisitivo, porque este análisis no lo mide.
3. **Si es un café de especialidad para oficinas: Chapinero.** Tiene la mayor demanda diurna por punto, pero sus residentes ya están muy atendidos.
4. **Siguiente paso:** bajar a nivel de UPZ o barrio, con estrato, valor del suelo y flujo peatonal, antes de firmar un arriendo.

## Método
- **Oferta (competencia directa):** empresas vigentes en marzo 2026 con CIIU 5613 (*expendio de comidas preparadas en cafeterías*) y 1081 (*elaboración de productos de panadería*). Se incluye la panadería porque en Bogotá es el lugar de barrio donde más se toma café.
- **Demanda residencial:** adultos (18 años o más) proyectados para 2026 en cada localidad.
- **Demanda diurna:** empresas vigentes en la localidad, como indicador de la población que trabaja allí.
- **Indicadores:** adultos por punto, empresas por punto, puntos por cada 10.000 adultos y tasa de entrada (puntos creados en ene–mar ÷ vigentes).
- **Índice de oportunidad (ejemplo):** 0,5 × z(adultos por punto) + 0,3 × z(empresas por punto) − 0,2 × z(tasa de entrada). La hoja `03_sensibilidad_pesos` muestra que el ranking cambia mucho con los pesos. Por eso la conclusión principal no es un ranking único, sino la matriz y los dos modelos de café.
- Sumapaz queda por fuera porque es rural y no tiene datos en la base de empresas. También quedan por fuera 528 puntos de café registrados "Sin localidad".

## Datos
| Fuente | Uso | Licencia |
| --- | --- | --- |
| [Dinámica Empresarial Bogotá](https://datosabiertos.bogota.gov.co/en/dataset/dinamica-empresarial-bogota/resource/170b171a-19bb-46ca-83e8-3074fe7d74be), corte mar 2026 (base limpia del caso "Radiografía del emprendimiento") | Cafeterías, panaderías y empresas vigentes por localidad | CC BY-SA 4.0 |
| Proyecciones de población por localidad 2005–2035 (Datos Abiertos Bogotá / SDP), año 2026 | Población y adultos por localidad | CC BY 4.0 |

Control de calidad: la suma de las 20 localidades da 7.945.996 habitantes en 2026, igual al total de Bogotá del archivo.

Como el análisis combina una fuente CC BY-SA, las tablas y gráficos derivados se comparten bajo **CC BY-SA 4.0**.

## Contenido de la carpeta
| Archivo | Contenido |
| --- | --- |
| `tablas/resultados_donde_abrir_cafe.xlsx` | Ranking por localidad con todos los indicadores, referencia de Bogotá, sensibilidad de pesos y método |
| `tablas/ranking_localidades.csv` | La misma tabla de localidades en CSV |
| `graficos/01_matriz_demanda_competencia.png` | Matriz: adultos frente a empresas por punto de café |
| `graficos/02_dos_modelos_de_cafe.png` | Las 8 localidades menos saturadas para el café de barrio y para el café de oficina |
| `datos/empresas_bogota_limpio.csv` | Base limpia de empresas (del repo [bogota-business-births](https://github.com/Sebaspadi97/bogota-business-births)) |
| `datos/poblacion_localidad.csv` | Proyecciones de población por localidad 2005–2035 (Datos Abiertos Bogotá) |
| `scripts/analisis_cafe.py` | Código reproducible |

Para reproducir: `pip install -r requirements.txt` y luego `python scripts/analisis_cafe.py datos/empresas_bogota_limpio.csv datos/poblacion_localidad.csv .`

## Limitaciones
- **La localidad es una unidad muy grande:** Suba o Usaquén tienen zonas saturadas y zonas vacías. Para v2: UPZ.
- **Sin ingresos, estrato ni flujo peatonal:** mucha gente por punto no garantiza capacidad de pago.
- **Las empresas registradas no son trabajadores:** Chapinero concentra sedes legales, lo que puede inflar su demanda diurna.
- **Solo competencia formal y registrada:** la venta informal de tinto no aparece. Tampoco se cuentan los restaurantes ni las tiendas que venden café.
- **Un solo corte (mar 2026)** para la oferta.
- Gráficos en tipografía Inter; para el sitio se rehacen en Montserrat / Open Sans.

## Licencia
- **Código** (`scripts/`): © 2026 Sebastián Padilla Castaño. Todos los derechos reservados. Puedes leerlo y ejecutarlo para revisar el análisis, pero no reutilizarlo ni redistribuirlo sin autorización.
- **Datos, tablas y gráficos:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es). Los datos de `datos/`, las tablas y los gráficos combinan una fuente CC BY-SA 4.0 (Dinámica Empresarial) y una CC BY 4.0 (proyecciones de población). Por eso se comparten bajo CC BY-SA 4.0.
- Ver `LICENSE.md`.

---
Parte de **Sebas Padilla Lab** · De los datos a las decisiones.

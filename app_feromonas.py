
import streamlit as st
import math
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

# Logo y cabecera
st.image("logo_care.jpg", width=300)
st.title("CARE - Simulador de Cobertura de Feromonas")
st.markdown("Departamento Técnico - Viticultura")

# Entradas de usuario
st.subheader("📥 Parámetros de la parcela y colocación")

ancho_parcela = st.number_input("Ancho de la parcela (m)", value=100.0)
largo_parcela = st.number_input("Largo de la parcela (m)", value=100.0)
distancia_cepas = st.number_input("Distancia entre cepas en la fila (m)", value=1.2)
distancia_filas = st.number_input("Distancia entre filas (m)", value=2.5)
patron_colocacion = st.number_input("Patrón de colocación (1 sí / X no)", min_value=0, max_value=10, value=1)
total_feromonas = st.number_input("Número total de feromonas en la parcela", min_value=1, value=100)
radio_manual = math.sqrt(st.number_input("Área cubierta por cada feromona (m²)", value=40.0) / math.pi)

# Cálculos básicos
num_filas = int(largo_parcela / distancia_filas)
cepas_por_fila = int(ancho_parcela / distancia_cepas)
filas_con_feromona = num_filas // (patron_colocacion + 1)

intervalo_cepas_teorico = cepas_por_fila / (total_feromonas / filas_con_feromona)
intervalo_cepas = round(intervalo_cepas_teorico * 2) / 2

feromonas_por_fila = cepas_por_fila / intervalo_cepas
total_feromonas_ajustadas = int(filas_con_feromona * feromonas_por_fila)
area_por_feromona = math.pi * radio_manual**2

# Mostrar resultados
st.subheader("🔢 Resultados de Parámetros")
st.write(f"**Filas totales:** {num_filas}")
st.write(f"**Cepas por fila:** {cepas_por_fila}")
st.write(f"**Filas con feromona:** {filas_con_feromona}")
st.write(f"**Feromonas por fila:** {feromonas_por_fila:.2f}")
st.write(f"**Intervalo entre feromonas (ajustado a 0.5):** {intervalo_cepas:.2f} cepas")
st.write(f"**Total feromonas utilizadas (ajustado):** {total_feromonas_ajustadas}")
st.write(f"**Área por feromona (definida):** {area_por_feromona:.2f} m²")
st.write(f"**Radio calculado:** {radio_manual:.2f} m")

# Cobertura real
parcela = Polygon([(0, 0), (ancho_parcela, 0), (ancho_parcela, largo_parcela), (0, largo_parcela)])
feromonas = []

fila_indices = range(0, num_filas, patron_colocacion + 1)
for fila in fila_indices:
    y = fila * distancia_filas + distancia_filas / 2
    for j in range(int(feromonas_por_fila)):
        x = (j + 0.5) * intervalo_cepas * distancia_cepas
        if x < ancho_parcela:
            feromonas.append(Point(x, y))

coberturas = [f.buffer(radio_manual) for f in feromonas]
coberturas_dentro = [c.intersection(parcela) for c in coberturas]
union_coberturas = unary_union(coberturas_dentro)
area_cubierta_real = union_coberturas.area
porcentaje_cobertura = (area_cubierta_real / parcela.area) * 100

# Resultados visuales
st.subheader("🟦 Cobertura Real Calculada")
st.markdown(f"<h2 style='color:#004080;'>🔵 Porcentaje de cobertura: <b>{porcentaje_cobertura:.2f}%</b></h2>", unsafe_allow_html=True)
st.write(f"**Área cubierta efectiva:** {area_cubierta_real:.2f} m²")

fig, ax = plt.subplots(figsize=(8, 8))
x, y = parcela.exterior.xy
ax.plot(x, y, 'black', linewidth=2, label="Parcela")

for c in coberturas_dentro:
    if not c.is_empty:
        x, y = c.exterior.xy
        ax.fill(x, y, alpha=0.3, color='blue')

x_fero = [f.x for f in feromonas]
y_fero = [f.y for f in feromonas]
ax.scatter(x_fero, y_fero, color='red', s=10, label="Feromonas")

ax.set_title("Distribución y Cobertura de Feromonas")
ax.set_xlabel("m")
ax.set_ylabel("m")
ax.axis("equal")
ax.grid(True)
ax.legend()
st.pyplot(fig)

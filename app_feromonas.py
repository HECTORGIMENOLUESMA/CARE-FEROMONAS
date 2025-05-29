
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

# Mostrar logo y título
st.image("logo_care.jpg", width=300)
st.title("CARE - Simulador de Cobertura de Feromonas")
st.markdown("Departamento Técnico - Viticultura")

uploaded_file = st.file_uploader("📥 Sube tu archivo Excel con parámetros", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Simulador", header=None)

        total_feromonas = int(df.iloc[7, 1])
        ancho_parcela = float(df.iloc[8, 1])
        largo_parcela = float(df.iloc[9, 1])
        distancia_filas = float(df.iloc[10, 1])
        distancia_cepas = float(df.iloc[11, 1])
        patron_colocacion = int(df.iloc[12, 1])

        num_filas = int(largo_parcela / distancia_filas)
        cepas_por_fila = int(ancho_parcela / distancia_cepas)
        filas_con_feromona = num_filas // (patron_colocacion + 1)
        feromonas_por_fila = total_feromonas / filas_con_feromona
        intervalo_cepas = cepas_por_fila / feromonas_por_fila
        area_por_feromona = 10000 / total_feromonas
        radio_por_feromona = math.sqrt(area_por_feromona / math.pi)

        st.subheader("🔢 Resultados de Parámetros")
        st.write(f"**Filas totales:** {num_filas}")
        st.write(f"**Cepas por fila:** {cepas_por_fila}")
        st.write(f"**Filas con feromona:** {filas_con_feromona}")
        st.write(f"**Feromonas por fila:** {feromonas_por_fila:.2f}")
        st.write(f"**Intervalo entre feromonas (cepas):** {intervalo_cepas:.2f}")
        st.write(f"**Área por feromona:** {area_por_feromona:.2f} m²")
        st.write(f"**Radio teórico:** {radio_por_feromona:.2f} m")

        parcela = Polygon([(0, 0), (ancho_parcela, 0), (ancho_parcela, largo_parcela), (0, largo_parcela)])
        feromonas = []

        fila_indices = range(0, num_filas, patron_colocacion + 1)
        for fila in fila_indices:
            y = fila * distancia_filas + distancia_filas / 2
            for j in range(int(feromonas_por_fila)):
                x = (j + 0.5) * intervalo_cepas * distancia_cepas
                if x < ancho_parcela:
                    feromonas.append(Point(x, y))

        coberturas = [f.buffer(radio_por_feromona) for f in feromonas]
        coberturas_dentro = [c.intersection(parcela) for c in coberturas]
        union_coberturas = unary_union(coberturas_dentro)
        area_cubierta_real = union_coberturas.area
        porcentaje_cobertura = (area_cubierta_real / parcela.area) * 100

        st.subheader("🟦 Cobertura Real Calculada")
        st.write(f"**Área cubierta efectiva:** {area_cubierta_real:.2f} m²")
        st.write(f"**Porcentaje de cobertura:** {porcentaje_cobertura:.2f} %")

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

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

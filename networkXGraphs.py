import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import joblib
from pathlib import Path


# ============================================================
# RUTAS PROFESIONALES
# ============================================================
# Se usa Pathlib para que las rutas funcionen en cualquier sistema
BASE_DIR = Path(__file__).resolve().parent

csv_path = BASE_DIR / "datasets" / "combined_external_sleepmind.csv"
model_path = BASE_DIR / "model" / "sleepmind_randomforest_v2.pkl"

# Cargar dataset y modelo entrenado
df = pd.read_csv(csv_path)
model = joblib.load(model_path)


def grafo_correlaciones_radial(df):


    # Solo tomar columnas numéricas para correlación
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()

    G = nx.Graph()

    # Añadir nodos por cada variable numérica
    for col in corr.columns:
        G.add_node(col)

    # Crear conexiones según la fuerza de correlación
    for i in corr.columns:
        for j in corr.columns:
            if i != j:
                weight = corr.loc[i, j]

                # Colores futuristas según intensidad
                if abs(weight) > 0.6:
                    color = '#00eaff' if weight > 0 else '#ff2ce6'  # conexión muy fuerte
                elif abs(weight) > 0.3:
                    color = '#417dff' if weight > 0 else '#c63cff'  # conexión media
                else:
                    color = '#707b9f'                                # conexión débil

                # Añadir arista al grafo
                G.add_edge(i, j, weight=abs(weight), color=color)

    # Crear figura con fondo oscuro forzado (sin blanco)
    fig = plt.figure(figsize=(13, 11), facecolor='#0E0F23')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0E0F23')

    # Rectángulo para asegurar fondo oscuro
    ax.add_patch(plt.Rectangle(
        (-1, -1), 2, 2,
        transform=ax.transAxes,
        color='#0E0F23',
        zorder=-1000
    ))

    # Posicionamiento radial
    pos = nx.shell_layout(G)

    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    widths = [G[u][v]['weight'] * 6 for u, v in edges]

    # Dibujar grafo
    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_color='#1F2947',     # nodos futuristas visibles
        edge_color=colors,
        width=widths,
        node_size=5200,
        font_size=14,
        font_color='#FFFFFF',
        font_weight='bold'
    )

    # Título
    ax.set_title(
        "Radial Graph of Correlations - SleepMind",
        fontsize=18,
        fontweight='bold',
        color='#FFFFFF'
    )

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.patch.set_edgecolor('#0E0F23')
    fig.patch.set_facecolor('#0E0F23')
    ax.patch.set_facecolor('#0E0F23')
    plt.tight_layout()
    return fig

def grafo_importancia_radial(model):

    feature_cols = ["age", "hours_slept", "exercise",
                    "caffeine", "stress_general", "screen_time"]

    importances = model.feature_importances_

    G = nx.DiGraph()
    G.add_node("SleepMind_Model")  # nodo central

    # Crear conexiones desde cada variable hacia el modelo
    for feat, imp in zip(feature_cols, importances):

        # Asignar color según importancia
        if imp > 0.15:
            color = '#00eaff'   # muy importante
        elif imp > 0.08:
            color = '#7e42ff'   # importancia media
        else:
            color = '#615e8c'   # importancia baja

        G.add_edge(feat, "SleepMind_Model", weight=imp, color=color)

    # Figura oscura garantizada
    fig = plt.figure(figsize=(13, 11), facecolor='#0E0F23')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0E0F23')

    # Parche para eliminar fondo blanco
    ax.add_patch(plt.Rectangle(
        (-1, -1), 2, 2,
        transform=ax.transAxes,
        color='#0E0F23',
        zorder=-1000
    ))

    pos = nx.shell_layout(G)

    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    widths = [G[u][v]['weight'] * 15 for u, v in edges]  # grosor proporcional

    nx.draw(
        G,
        pos,
        ax=ax,
        with_labels=True,
        node_color='#1F2947',   # nodos futuristas
        edge_color=colors,
        width=widths,
        node_size=5200,
        font_size=14,
        font_color='#FFFFFF',
        font_weight='bold'
    )

    ax.set_title(
        "Radial Graph of Importance - SleepMind",
        fontsize=18,
        fontweight='bold',
        color='#FFFFFF'
    )
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.patch.set_edgecolor('#0E0F23')
    fig.patch.set_facecolor('#0E0F23')
    ax.patch.set_facecolor('#0E0F23')
    plt.tight_layout()
    return fig



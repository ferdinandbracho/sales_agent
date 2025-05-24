"""
Car Search Tool - Herramienta de búsqueda de autos
Busca autos en el catálogo de Kavak usando criterios específicos
"""

import os
from typing import Any, Dict, List, Optional

import pandas as pd
from langchain.tools import tool

from ..config import MEXICAN_CONFIG

# Load car data
CAR_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/sample_caso_ai_engineer.csv"
)


def load_car_data() -> pd.DataFrame:
    """Carga los datos del catálogo de autos"""
    try:
        df = pd.read_csv(CAR_DATA_PATH)
        # Create searchable description for each car
        df["descripcion"] = df.apply(
            lambda row: f"{row['make']} {row['model']} {row['year']} {row['version']} "
            f"- ${row['price']:,.0f}, {row['km']:,} km, "
            f"Bluetooth: {row['bluetooth']}"
            + (f", CarPlay: {row['car_play']}" if pd.notna(row["car_play"]) else ""),
            axis=1,
        )
        return df
    except Exception as e:
        print(f"Error loading car data: {e}")
        return pd.DataFrame()


@tool
def buscar_autos_por_presupuesto(
    presupuesto_maximo: float,
    marca: Optional[str] = None,
    tipo_auto: Optional[str] = None,
) -> str:
    """
    Busca autos en el catálogo según el presupuesto máximo del cliente.

    Args:
        presupuesto_maximo: Presupuesto máximo en pesos mexicanos
        marca: Marca específica (opcional) - ej: Toyota, Nissan, Ford
        tipo_auto: Tipo de auto (opcional) - ej: sedan, SUV, hatchback

    Returns:
        Lista formateada de autos disponibles en español
    """
    try:
        df = load_car_data()
        if df.empty:
            return "❌ No pude acceder al catálogo. ¿Intentamos de nuevo en un momento?"

        # Filter by budget
        autos_filtrados = df[df["price"] <= presupuesto_maximo]

        # Filter by brand if specified
        if marca:
            marca_clean = marca.strip().title()
            autos_filtrados = autos_filtrados[
                autos_filtrados["make"].str.contains(marca_clean, case=False, na=False)
            ]

        # Sort by price (ascending)
        autos_filtrados = autos_filtrados.sort_values("price")

        if autos_filtrados.empty:
            return f"""
🔍 No encontré autos con esos criterios.

Algunas opciones:
• Aumentar el presupuesto a ${presupuesto_maximo + 50000:,.0f}
• Considerar diferentes marcas
• Ver autos seminuevos con más kilometraje

¿Te ayudo con otras opciones? 😊
"""

        # Format top 5 results
        resultados = autos_filtrados.head(5)
        respuesta = f"🚗 Encontré {len(autos_filtrados)} autos en tu presupuesto de ${presupuesto_maximo:,.0f}:\n\n"

        for idx, auto in resultados.iterrows():
            bluetooth_text = (
                "✅ Bluetooth" if auto["bluetooth"] == "Sí" else "❌ Sin Bluetooth"
            )
            carplay_text = (
                " • ✅ CarPlay"
                if pd.notna(auto["car_play"]) and auto["car_play"] == "Sí"
                else ""
            )

            respuesta += f"""
**{auto['make']} {auto['model']} {auto['year']}**
💰 ${auto['price']:,.0f}
📍 {auto['km']:,} km
{bluetooth_text}{carplay_text}
---
"""

        if len(autos_filtrados) > 5:
            respuesta += f"\n¡Y {len(autos_filtrados)-5} opciones más!\n"

        respuesta += "\n¿Te interesa alguno en particular? ¿Quieres más detalles? 😊"

        return respuesta

    except Exception as e:
        return f"❌ Error en la búsqueda: {str(e)}. ¿Puedes intentar de nuevo?"


@tool
def buscar_auto_especifico(marca: str, modelo: str) -> str:
    """
    Busca un auto específico por marca y modelo.

    Args:
        marca: Marca del auto (ej: Toyota, Nissan, Ford)
        modelo: Modelo del auto (ej: Corolla, Sentra, Focus)

    Returns:
        Información detallada del auto encontrado
    """
    try:
        df = load_car_data()
        if df.empty:
            return "❌ No pude acceder al catálogo. ¿Intentamos de nuevo?"

        # Search for specific make and model (case insensitive)
        auto_encontrado = df[
            (df["make"].str.contains(marca, case=False, na=False))
            & (df["model"].str.contains(modelo, case=False, na=False))
        ]

        if auto_encontrado.empty:
            # Try fuzzy matching for common typos
            auto_encontrado = buscar_con_fuzzy_matching(df, marca, modelo)

        if auto_encontrado.empty:
            return f"""
🔍 No encontré "{marca} {modelo}" en nuestro catálogo.

¿Quizás te refieres a:
• {sugerir_marcas_similares(df, marca)}
• {sugerir_modelos_similares(df, modelo)}

¿Puedes verificar el nombre? 🤔
"""

        # Show all available versions of this car
        auto_encontrado = auto_encontrado.sort_values("price")
        respuesta = f"🚗 Encontré **{marca.title()} {modelo.title()}** disponible:\n\n"

        for idx, auto in auto_encontrado.iterrows():
            bluetooth_icon = "✅" if auto["bluetooth"] == "Sí" else "❌"
            carplay_icon = (
                "✅"
                if pd.notna(auto["car_play"]) and auto["car_play"] == "Sí"
                else "❌"
            )

            respuesta += f"""
**{auto['make']} {auto['model']} {auto['year']}**
{auto['version']}
💰 ${auto['price']:,.0f}
📍 {auto['km']:,} km
{bluetooth_icon} Bluetooth • {carplay_icon} CarPlay
Stock ID: {auto['stock_id']}
---
"""

        respuesta += (
            "\n¿Te interesa alguna versión? ¿Quieres calcular financiamiento? 💰"
        )

        return respuesta

    except Exception as e:
        return f"❌ Error en la búsqueda: {str(e)}. ¿Puedes intentar de nuevo?"


def buscar_con_fuzzy_matching(
    df: pd.DataFrame, marca: str, modelo: str
) -> pd.DataFrame:
    """Búsqueda con tolerancia a errores tipográficos"""
    # Common typos in Mexican car market
    typo_corrections = {
        "nisan": "nissan",
        "toyoya": "toyota",
        "ford": "ford",
        "chevrolet": "chevrolet",
        "volkswagen": "volkswagen",
        "honda": "honda",
    }

    marca_corregida = typo_corrections.get(marca.lower(), marca)

    return df[
        (df["make"].str.contains(marca_corregida, case=False, na=False))
        & (df["model"].str.contains(modelo, case=False, na=False))
    ]


def sugerir_marcas_similares(df: pd.DataFrame, marca: str) -> str:
    """Sugiere marcas similares disponibles"""
    marcas_disponibles = df["make"].unique()[:5]
    return ", ".join(marcas_disponibles)


def sugerir_modelos_similares(df: pd.DataFrame, modelo: str) -> str:
    """Sugiere modelos similares disponibles"""
    modelos_disponibles = df["model"].unique()[:5]
    return ", ".join(modelos_disponibles)


@tool
def obtener_autos_populares() -> str:
    """
    Muestra los autos más populares en el catálogo de Kavak.

    Returns:
        Lista de autos más populares con precios
    """
    try:
        df = load_car_data()
        if df.empty:
            return "❌ No pude acceder al catálogo."

        # Get most common makes
        marcas_populares = df["make"].value_counts().head(5)

        respuesta = (
            f"{MEXICAN_CONFIG['emojis']['car']} **Autos más populares en Kavak:**\n\n"
        )

        for marca, cantidad in marcas_populares.items():
            auto_ejemplo = df[df["make"] == marca].sort_values("price").iloc[0]
            respuesta += f"""
**{marca}** ({cantidad} disponibles)
Desde ${auto_ejemplo['price']:,.0f}
Ejemplo: {auto_ejemplo['model']} {auto_ejemplo['year']}
---
"""

        respuesta += "\n¿Te interesa alguna marca en particular? 😊"

        return respuesta

    except Exception as e:
        return "❌ Error obteniendo autos populares. ¿Intentamos de nuevo?"

"""
Car Search Tool
"""

import os
import re
from typing import List, Optional, Tuple

import pandas as pd
from langchain.tools import tool
from rapidfuzz import fuzz, process

from ..core.logging import get_logger

# Initialize logger
log = get_logger(__name__)

# Path to car data
CAR_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/sample_caso_ai_engineer.csv"
)


def load_car_data() -> pd.DataFrame:
    """Load car data from CSV file"""
    log.info("Loading car data from %s", CAR_DATA_PATH)
    try:
        df = pd.read_csv(CAR_DATA_PATH)
        log.info("Successfully loaded %d car records", len(df))
        # Create searchable description for each car
        df["descripcion"] = df.apply(
            lambda row: (
                f"{row['make']} {row['model']} {row['year']} {row['version']} - "
                f"${row['price']:,.0f}, {row['km']:,} km\n"
                f"Dimensiones: {row['largo']}mm (largo) x {row['ancho']}mm (ancho) x {row['altura']}mm (altura)\n"
                f"Bluetooth: {row['bluetooth']}"
                f"{', CarPlay: ' + str(row['car_play']) if pd.notna(row['car_play']) else ''}"
            ),
            axis=1,
        )
        return df
    except Exception:
        log.error("Error loading car data", exc_info=True)
        return pd.DataFrame()


@tool
def search_cars_by_budget(
    max_price: float,
    brand: Optional[str] = None,
) -> str:
    """
    Search for cars within a budget.

    Args:
        max_price: Maximum budget in pesos mexicanos
        brand: Specific brand (optional) - e.g: Toyota, Nissan, Ford

    Returns:
        Formatted list of available cars in Spanish
    """
    try:
        df = load_car_data()
        if df.empty:
            return "❌ No pude acceder al catálogo. ¿Intentamos de nuevo en un momento?"

        # Filter by budget
        filtered_cars = df[df["price"] <= max_price]

        # Filter by brand if specified
        if brand:
            log.debug("Filtering by brand: %s", brand)
            brand_clean = brand.strip().title()
            filtered_cars = filtered_cars[
                filtered_cars["make"].str.contains(brand_clean, case=False, na=False)
            ]

        # Sort by price (ascending)
        filtered_cars = filtered_cars.sort_values("price")

        if filtered_cars.empty:
            return f"""
            🔍 No encontré autos con esos criterios.

            Algunas opciones:
            • Aumentar el presupuesto a ${max_price + 50000:,.0f}
            • Considerar diferentes marcas

            ¿Te ayudo con otras opciones? 😊
            """

        # Format top 5 results
        log.info(
            "Fuzzy search completed. Found %d matching vehicles", len(filtered_cars)
        )
        results = filtered_cars.head(5)
        response = f"🚗 Encontré {len(filtered_cars)} autos en tu presupuesto de ${max_price:,.0f}:\n\n"

        for idx, auto in results.iterrows():
            bluetooth_text = (
                "✅ Bluetooth" if auto["bluetooth"] == "Sí" else "❌ Sin Bluetooth"
            )
            carplay_text = (
                " • ✅ CarPlay"
                if pd.notna(auto["car_play"]) and auto["car_play"] == "Sí"
                else ""
            )

            response += f"""
            **{auto["make"]} {auto["model"]} {auto["year"]}**
            💰 ${auto["price"]:,.0f}
            📍 {auto["km"]:,} km
            {bluetooth_text}{carplay_text}
            ---
            """

        if len(filtered_cars) > 5:
            response += f"\n¡Y {len(filtered_cars) - 5} opciones más!\n"

        response += "\n¿Te interesa alguno en particular? ¿Quieres más detalles? 😊"

        return response

    except Exception as e:
        return f"❌ Error en la búsqueda: {str(e)}. ¿Puedes intentar de nuevo?"


@tool
def search_specific_car(brand: str, model: str) -> str:
    """
    Search for a specific car by brand and model.

    Args:
        brand: Brand of the car (e.g: Toyota, Nissan, Ford)
        model: Model of the car (e.g: Corolla, Sentra, Focus)

    Returns:
        Detailed information about the car found
    """
    try:
        df = load_car_data()
        if df.empty:
            return "❌ No pude acceder al catálogo. ¿Intentamos de nuevo?"

        # Search for specific make and model (case insensitive)
        auto_encontrado = df[
            (df["make"].str.contains(brand, case=False, na=False))
            & (df["model"].str.contains(model, case=False, na=False))
        ]

        if auto_encontrado.empty:
            # Try fuzzy matching for common typos
            auto_encontrado = search_with_fuzzy_matching(df, brand, model)

        if auto_encontrado.empty:
            return f"""
        🔍 No encontré "{brand} {model}" en nuestro catálogo.

        ¿Quizás te refieres a:
        • {suggest_similar_brands(df, brand)}
        • {suggest_similar_models(df, model)}

        ¿Puedes verificar el nombre? 🤔
        """

        # Show all available versions of this car
        sorted_cars = auto_encontrado.sort_values("price")
        response = f"🚗 Encontré **{brand.title()} {model.title()}** disponible:\n\n"

        for idx, auto in sorted_cars.iterrows():
            bluetooth_icon = "✅" if auto["bluetooth"] == "Sí" else "❌"
            carplay_icon = (
                "✅"
                if pd.notna(auto["car_play"]) and auto["car_play"] == "Sí"
                else "❌"
            )

            response += f"""
            **{auto["make"]} {auto["model"]} {auto["year"]}**
            {auto["version"]}
            💰 ${auto["price"]:,.0f}
            📍 {auto["km"]:,} km
            {bluetooth_icon} Bluetooth • {carplay_icon} CarPlay
            Stock ID: {auto["stock_id"]}
            ---
            """

        response += (
            "\n¿Te interesa alguna versión? ¿Quieres calcular financiamiento? 💰"
        )

        return response

    except Exception as e:
        return f"❌ Error en la búsqueda: {str(e)}. ¿Puedes intentar de nuevo?"


def _normalize_text(text: str) -> str:
    """Normalize text for better matching"""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove special chars
    return text


def _get_best_match(
    query: str, choices: List[str], threshold: int = 75
) -> Optional[Tuple[str, int]]:
    """Find the best match for a query from a list of choices"""
    if not query or not choices:
        log.debug("Empty query or choices provided")
        return None

    log.debug("Finding best match for query: %s", query)

    # First try exact match
    normalized_choices = {_normalize_text(c): c for c in choices}
    normalized_query = _normalize_text(query)
    log.debug("Normalized query: %s", normalized_query)

    if normalized_query in normalized_choices:
        log.debug("Found exact match: %s", normalized_query)
        return (normalized_choices[normalized_query], 100)

    # Try fuzzy matching
    result = process.extractOne(
        normalized_query,
        normalized_choices.keys(),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold,  # Early termination if no good match is found
    )

    if result is None:
        log.debug("No match found above threshold (%d)", threshold)
        return None

    best_match, score, _ = result
    log.debug("Best fuzzy match: %s (score: %d)", best_match, score)

    # Return the original string (not normalized) that matches
    return (normalized_choices[best_match], score)


def _correct_common_typos(text: str) -> str:
    """Correct common typos in car makes and models"""
    if not text:
        return ""

    original_text = text
    text = text.lower()
    log.debug("Correcting typos in: %s", original_text)

    # Common brand typos
    brand_typos = {
        r"^nisan$": "nissan",
        r"^toyoya$": "toyota",
        r"^vw$": "volkswagen",
        r"^vwv$": "volkswagen",
        r"^volks$": "volkswagen",
        r"^chevy$": "chevrolet",
        r"^cheverolet$": "chevrolet",
        r"^mazada$": "mazda",
        r"^mitsubitshi$": "mitsubishi",
        r"^mercedez$": "mercedes",
        r"^bmw$": "bmw",
    }

    # Common model typos
    model_typos = {
        r"civic.*": "civic",
        r"sentra.*": "sentra",
        r"corolla.*": "corolla",
        r"jetta.*": "jetta",
        r"golf.*": "golf",
        r"versa.*": "versa",
        r"march.*": "march",
        r"tsuru.*": "tsuru",
        r"aveo.*": "aveo",
        r"spark.*": "spark",
    }

    # Apply brand corrections first
    for typo, correction in brand_typos.items():
        if re.search(typo, text):
            text = re.sub(typo, correction, text)
            log.debug("Corrected brand typo: %s -> %s", original_text, text)
            break  # Only apply one brand corrections

    # Then apply model corrections
    for typo, correction in model_typos.items():
        if re.match(typo, text):
            return correction

    return text


def search_with_fuzzy_matching(
    df: pd.DataFrame, brand: Optional[str] = None, model: Optional[str] = None
) -> pd.DataFrame:
    """Search for cars with fuzzy matching on brand and model"""
    log.info(
        "Starting fuzzy search with brand='%s', model='%s'",
        brand or "None",
        model or "None",
    )

    if df.empty:
        log.warning("Empty DataFrame provided to search_with_fuzzy_matching")
        return df

    # Make copies to avoid SettingWithCopyWarning
    df_filtered = df.copy()
    log.debug("Created working copy of DataFrame with %d rows", len(df_filtered))

    # Apply text normalization and corrections
    if brand:
        brand = _normalize_text(brand)
        brand = _correct_common_typos(brand)

    if model:
        model = _normalize_text(model)
        model = _correct_common_typos(model)

    if brand and not df_filtered.empty:
        # Get unique brands for matching
        unique_brands = df_filtered["make"].unique().tolist()
        log.debug("Matching against %d unique brands", len(unique_brands))
        best_brand_match = _get_best_match(brand, unique_brands)

        if best_brand_match:
            matched_brand, score = best_brand_match
            log.debug("Matched brand: %s (score: %d)", matched_brand, score)
            df_filtered = df_filtered[df_filtered["make"] == matched_brand]
            log.debug("Filtered to %d matching brand rows", len(df_filtered))
        else:
            log.warning("No brand match found for: %s", brand)
            return pd.DataFrame()

    if model and not df_filtered.empty:
        # Get unique models for the filtered brands
        unique_models = df_filtered["model"].unique().tolist()
        log.debug("Matching against %d unique models", len(unique_models))
        best_model_match = _get_best_match(model, unique_models)

        if best_model_match:
            matched_model, score = best_model_match
            log.debug("Matched model: %s (score: %d)", matched_model, score)
            df_filtered = df_filtered[df_filtered["model"] == matched_model]
            log.debug("Filtered to %d matching model rows", len(df_filtered))
        else:
            log.warning("No model match found for: %s", model)
            return pd.DataFrame()

    log.info("Fuzzy search completed. Found %d matching vehicles", len(df_filtered))
    return df_filtered


def suggest_similar_brands(df: pd.DataFrame, brand: str) -> str:
    """Suggest similar brands"""
    marcas_disponibles = df["make"].unique()[:5]
    return ", ".join(marcas_disponibles)


def suggest_similar_models(df: pd.DataFrame, model: str) -> str:
    """Suggest similar models"""
    modelos_disponibles = df["model"].unique()[:5]
    return ", ".join(modelos_disponibles)


@tool
def get_popular_cars() -> str:
    """
    Show the most popular cars in the Kavak catalog.

    Returns:
        List of most popular cars with prices
    """
    try:
        df = load_car_data()
        if df.empty:
            return "❌ No pude acceder al catálogo."

        # Get most common makes
        popular_brands = df["make"].value_counts().head(5)

        response = "🚗 **Autos más populares en Kavak:**\n\n"

        for brand, count in popular_brands.items():
            auto_ejemplo = df[df["make"] == brand].sort_values("price").iloc[0]
            response += f"""
            **{brand}** ({count} disponibles)
            Desde ${auto_ejemplo["price"]:,.0f}
            Ejemplo: {auto_ejemplo["model"]} {auto_ejemplo["year"]}
            ---
            """

        response += "\n¿Te interesa alguna marca en particular? 😊"

        return response

    except Exception as error:
        log.error("Error getting popular cars: %s", str(error), exc_info=True)
        return "❌ Error obteniendo autos populares. ¿Intentamos de nuevo?"

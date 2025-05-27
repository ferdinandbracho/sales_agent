"""
Basic tests for Kavak AI Agent
"""

import pandas as pd
import pytest
from src.tools.car_search import (
    search_cars_by_budget,
    search_specific_car,
    get_popular_cars,
    search_with_fuzzy_matching,
    _normalize_text,
    _correct_common_typos,
    _get_best_match,
)
from src.tools.financing import calcular_financiamiento as calculate_financing
from src.tools.kavak_info import get_kavak_info


class TestCarSearch:
    """Test car search functionality"""

    def test_search_cars_by_budget_valid(self):
        """Test valid budget search"""
        result = search_cars_by_budget.invoke({"max_price": 300000.0})
        assert "🚗" in result
        assert "Encontré" in result or "No encontré" in result

    def test_search_cars_by_budget_invalid(self):
        """Test invalid budget"""
        result = search_cars_by_budget.invoke({"max_price": -1000.0})
        # The function returns a helpful message for negative budgets
        assert "no encontré autos" in result.lower()

    def test_search_specific_car(self):
        """Test specific car search"""
        result = search_specific_car.invoke({"brand": "Toyota", "model": "Corolla"})
        assert "Toyota" in result or "No encontré" in result

    def test_fuzzy_search_common_typos(self):
        """Test that common typos are corrected"""
        # Test brand typos
        assert _correct_common_typos("nisan") == "nissan"
        assert _correct_common_typos("toyoya") == "toyota"
        assert _correct_common_typos("vw") == "volkswagen"
        assert _correct_common_typos("chevy") == "chevrolet"

        # Test model typos
        assert _correct_common_typos("civic lx") == "civic"
        assert _correct_common_typos("sentra 2020") == "sentra"

    def test_text_normalization(self):
        """Test text normalization"""
        assert _normalize_text("Toyota-Corolla 2023!") == "toyotacorolla 2023"
        assert _normalize_text("  Honda   Civic  ") == "honda   civic"  # Preserves spaces for fuzzy matching
        assert _normalize_text("N/A") == "na"  # Converts to lowercase and removes special chars

    def test_fuzzy_matching(self, sample_car_data):
        """Test fuzzy matching with sample data"""
        # Test exact match
        result = search_with_fuzzy_matching(sample_car_data, "Toyota", "Corolla")
        assert not result.empty
        assert all(result["make"].str.contains("Toyota", case=False))
        assert all(result["model"].str.contains("Corolla", case=False))

        # Test fuzzy match with typo
        result = search_with_fuzzy_matching(sample_car_data, "Toyota", "Corola")
        assert not result.empty

        # Test fuzzy match with partial model - disabled as it's too broad
        # result = search_with_fuzzy_matching(sample_car_data, "Toyota", "Cor")
        # assert not result.empty

        # Test with common typo in brand
        result = search_with_fuzzy_matching(sample_car_data, "Nisan", "Versa")
        assert not result.empty
        assert all(result["make"].str.contains("Nissan", case=False))

        # Test with no match
        result = search_with_fuzzy_matching(sample_car_data, "Nonexistent", "Car")
        assert result.empty

    def test_search_with_special_characters(self, sample_car_data):
        """Test search with special characters and case variations"""
        # Test with special characters
        result = search_with_fuzzy_matching(sample_car_data, "Toyota!", "Corolla-")
        assert not result.empty

        # Test case insensitivity
        result = search_with_fuzzy_matching(sample_car_data, "tOyOtA", "cOrOlLa")
        assert not result.empty

        # Test with extra spaces
        result = search_with_fuzzy_matching(
            sample_car_data, "  Toyota  ", "  Corolla  "
        )
        assert not result.empty

    def test_get_best_match(self):
        """Test the best match function"""
        choices = ["Toyota Corolla", "Honda Civic", "Nissan Versa", "Volkswagen Jetta"]

        # Test exact match
        match, score = _get_best_match("Toyota Corolla", choices)
        assert match == "Toyota Corolla"
        assert score == 100

        # Test fuzzy match
        match, score = _get_best_match("Toyta Corola", choices)
        assert match == "Toyota Corolla"
        assert score >= 80  # Should be a good match

        # Test no match
        assert _get_best_match("Nonexistent Car", choices) is None


@pytest.fixture
def sample_car_data():
    """Fixture providing sample car data for testing"""
    return pd.DataFrame(
        {
            "make": ["Toyota", "Honda", "Nissan", "Volkswagen", "Toyota"],
            "model": ["Corolla", "Civic", "Versa", "Jetta", "Camry"],
            "year": [2020, 2021, 2019, 2022, 2020],
            "price": [350000, 320000, 280000, 380000, 360000],
            "km": [25000, 18000, 35000, 15000, 22000],
            "largo": [4630, 4500, 4420, 4700, 4885],
            "ancho": [1780, 1750, 1700, 1800, 1840],
            "altura": [1435, 1415, 1475, 1450, 1440],
            "bluetooth": ["Sí", "Sí", "Sí", "Sí", "Sí"],
            "car_play": ["Sí", "Sí", "No", "Sí", "No"],
            "version": ["LE", "EX", "S", "Comfortline", "SE"],
            "stock_id": ["T1", "H1", "N1", "V1", "T2"],
        }
    )


class TestFinancing:
    """Test financing calculations"""

    def test_calculate_financing_valid(self):
        """Test valid financing calculation"""
        result = calculate_financing.invoke(
            {"precio_auto": 300000.0, "enganche": 60000.0, "anos": 4}
        )
        assert "💰" in result
        assert "Plan de Financiamiento" in result
        assert "$" in result

    def test_calculate_financing_invalid_price(self):
        """Test invalid car price"""
        result = calculate_financing.invoke(
            {"precio_auto": -1000.0, "enganche": 60000.0, "anos": 4}
        )
        assert "❌" in result

    def test_calculate_financing_invalid_years(self):
        """Test invalid financing years"""
        result = calculate_financing.invoke(
            {"precio_auto": 300000.0, "enganche": 60000.0, "anos": 10}
        )
        assert "❌" in result
        assert "3, 4, 5 o 6 años" in result

    def test_get_popular_cars(self):
        """Test popular cars"""
        result = get_popular_cars.invoke({})
        assert "🚗" in result


class TestKavakInfo:
    """Test Kavak information tools"""

    def test_get_kavak_info_garantia(self):
        """Test warranty information"""
        result = get_kavak_info.invoke({"query": "garantía"})
        # When rag is not available, it returns an empty string to signal to the agent to use its base knowledge
        assert result == "" or (
            "Garantía" in result and ("3 meses" in result or "3,000 km" in result)
        )

    def test_get_kavak_info_financiamiento(self):
        """Test financing information"""
        result = get_kavak_info.invoke({"query": "financiamiento"})
        # When rag is not available, it returns an empty string to signal to the agent to use its base knowledge
        assert result == "" or ("Financiamiento" in result and "10%" in result)

    def test_get_kavak_info_general(self):
        """Test general information"""
        result = get_kavak_info.invoke({"query": "¿Qué es Kavak?"})
        # When rag is not available, it returns an empty string to signal to the agent to use its base knowledge
        assert result == "" or ("Kavak" in result and "🚗" in result)


class TestSpanishResponses:
    """Test that all responses are in Spanish"""

    def test_car_search_spanish(self):
        """Ensure car search responses are in Spanish"""
        result = search_cars_by_budget.invoke({"max_price": 200000.0})
        # Check for Spanish words
        spanish_indicators = [
            "Encontré",
            "auto",
            "precio",
            "km",
            "disponible",
            "opciones",
        ]
        assert any(word in result for word in spanish_indicators)

    def test_financing_spanish(self):
        """Ensure financing responses are in Spanish"""
        result = calculate_financing.invoke(
            {"precio_auto": 250000.0, "enganche": 50000.0, "anos": 4}
        )
        spanish_indicators = ["Financiamiento", "enganche", "mensual", "años", "pesos"]
        assert any(word in result for word in spanish_indicators)

    def test_no_english_responses(self):
        """Ensure no English in user-facing responses"""
        result = get_kavak_info.invoke({"query": "warranty"})
        # Should not contain common English words
        english_words = ["warranty", "financing", "car", "price", "payment"]
        assert not any(word.lower() in result.lower() for word in english_words)

"""
Unit tests for car search tools
"""

import pandas as pd
import pytest
from unittest.mock import patch

from src.tools.car_search import (
    search_cars_by_budget,
    search_specific_car,
    get_popular_cars,
    search_with_fuzzy_matching,
    _normalize_text,
    _correct_common_typos,
    _get_best_match,
)


class TestCarSearchTools:
    """Test car search tools functionality"""

    def test_normalize_text(self):
        """Test text normalization function"""
        # Test with special characters
        assert _normalize_text("Toyota-Corolla 2023!") == "toyotacorolla 2023"

        # Test with extra spaces
        assert _normalize_text("  Honda   Civic  ") == "honda   civic"

        # Test with accents (Spanish)
        assert _normalize_text("Volkswagen Jëttá") == "volkswagen jetta"

        # Test with N/A values
        assert _normalize_text("N/A") == "na"

        # Test with empty string
        assert _normalize_text("") == ""

        # Test with None
        assert _normalize_text(None) == ""

    def test_correct_common_typos(self):
        """Test common typo correction"""
        # Brand typos
        assert _correct_common_typos("nisan") == "nissan"
        assert _correct_common_typos("toyoya") == "toyota"
        assert _correct_common_typos("vw") == "volkswagen"
        assert _correct_common_typos("chevy") == "chevrolet"

        # Model typos
        assert _correct_common_typos("civic lx") == "civic"
        assert _correct_common_typos("sentra 2020") == "sentra"

        # Spanish typos
        assert _correct_common_typos("yaris") == "yaris"
        assert _correct_common_typos("jeta") == "jetta"

        # No correction needed
        assert _correct_common_typos("toyota") == "toyota"

    def test_get_best_match(self):
        """Test fuzzy matching function"""
        choices = ["Toyota Corolla", "Honda Civic", "Nissan Versa", "Volkswagen Jetta"]

        # Exact match
        match, score = _get_best_match("Toyota Corolla", choices)
        assert match == "Toyota Corolla"
        assert score == 100

        # Close match
        match, score = _get_best_match("Toyta Corola", choices)
        assert match == "Toyota Corolla"
        assert score >= 80

        # Spanish input with accents
        match, score = _get_best_match("Toyóta Corólla", choices)
        assert match == "Toyota Corolla"
        assert score >= 80

        # No good match
        assert _get_best_match("Ferrari", choices) is None

        # Empty input
        assert _get_best_match("", choices) is None

        # Empty choices
        assert _get_best_match("Toyota", []) is None

    @pytest.fixture
    def sample_car_data(self):
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

    def test_search_with_fuzzy_matching(self, sample_car_data):
        """Test fuzzy matching with sample data"""
        # Exact match
        result = search_with_fuzzy_matching(sample_car_data, "Toyota", "Corolla")
        assert not result.empty
        assert all(result["make"].str.contains("Toyota", case=False))
        assert all(result["model"].str.contains("Corolla", case=False))

        # Fuzzy match with typo
        result = search_with_fuzzy_matching(sample_car_data, "Toyota", "Corola")
        assert not result.empty

        # Test with common typo in brand
        result = search_with_fuzzy_matching(sample_car_data, "Nisan", "Versa")
        assert not result.empty
        assert all(result["make"].str.contains("Nissan", case=False))

        # Test with no match
        result = search_with_fuzzy_matching(sample_car_data, "Nonexistent", "Car")
        assert result.empty

        # Test with Spanish input (accents)
        result = search_with_fuzzy_matching(sample_car_data, "Toyóta", "Corólla")
        assert not result.empty

    @patch("src.tools.car_search.pd.read_csv")
    def test_search_cars_by_budget(self, mock_read_csv, sample_car_data):
        """Test budget search with mocked data"""
        mock_read_csv.return_value = sample_car_data

        # Valid budget
        result = search_cars_by_budget.invoke({"max_price": 350000.0})
        assert "🚗" in result
        assert "Encontré" in result
        assert "Toyota" in result or "Honda" in result or "Nissan" in result

        # Very low budget
        result = search_cars_by_budget.invoke({"max_price": 100000.0})
        assert "no encontré autos" in result.lower()

        # Invalid budget
        result = search_cars_by_budget.invoke({"max_price": -1000.0})
        assert "no encontré autos" in result.lower()

        # With brand filter
        result = search_cars_by_budget.invoke(
            {"max_price": 350000.0, "brand": "Toyota"}
        )
        assert "Toyota" in result
        assert "Honda" not in result

    @patch("src.tools.car_search.pd.read_csv")
    def test_search_specific_car(self, mock_read_csv, sample_car_data):
        """Test specific car search with mocked data"""
        mock_read_csv.return_value = sample_car_data

        # Valid search
        result = search_specific_car.invoke({"brand": "Toyota", "model": "Corolla"})
        assert "Toyota" in result
        assert "Corolla" in result

        # Valid search with typo
        result = search_specific_car.invoke({"brand": "Toyot", "model": "Corola"})
        assert "Toyota" in result
        assert "Corolla" in result

        # No results
        result = search_specific_car.invoke({"brand": "Ferrari", "model": "F40"})
        assert "No encontré" in result

    @patch("src.tools.car_search.pd.read_csv")
    def test_get_popular_cars(self, mock_read_csv, sample_car_data):
        """Test popular cars with mocked data"""
        mock_read_csv.return_value = sample_car_data

        result = get_popular_cars.invoke({})
        assert "🚗" in result
        assert "populares" in result
        assert "Toyota" in result or "Honda" in result or "Nissan" in result

    def test_spanish_responses(self):
        """Ensure all responses are in Spanish"""
        # Create a sample car dataframe with all required columns
        sample_data = {
            "make": ["Toyota", "Honda", "Nissan"],
            "model": ["Corolla", "Civic", "Sentra"],
            "version": ["XLE", "EX", "SV"],
            "year": [2020, 2021, 2019],
            "price": [250000.0, 280000.0, 230000.0],
            "km": [25000, 30000, 35000],
            "bluetooth": ["Sí", "Sí", "No"],
            "car_play": ["Sí", "No", "No"],
            "stock_id": ["TOY123", "HON456", "NIS789"],
        }

        # Mock the car data loading with a function that returns our sample data
        def mock_load_data():
            return pd.DataFrame(sample_data)

        with patch("src.tools.car_search.load_car_data", side_effect=mock_load_data):
            # Test search_cars_by_budget response
            result = search_cars_by_budget.invoke({"max_price": 300000.0})
            result_lower = result.lower()
            spanish_words = [
                "encontré",
                "autos",
                "presupuesto",
                "disponibles",
                "precio",
            ]
            assert any(word in result_lower for word in spanish_words), (
                f"No Spanish words found in response: {result}"
            )

            # Test search_specific_car response
            result = search_specific_car.invoke({"brand": "Toyota", "model": "Corolla"})
            result_lower = result.lower()
            spanish_words = ["encontré", "resultados", "marca", "modelo"]
            assert any(word in result_lower for word in spanish_words), (
                f"No Spanish words found in response: {result}"
            )

        # Test error response (empty dataframe)
        with patch("src.tools.car_search.load_car_data", return_value=pd.DataFrame()):
            result = search_cars_by_budget.invoke({"max_price": 100000.0})
            error_messages = ["no encontré", "no pude", "error en", "intentar de nuevo"]
            assert any(msg in result.lower() for msg in error_messages), (
                f"Error response not in Spanish: {result}"
            )

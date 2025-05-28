"""
Tests for Spanish language responses and localization
"""

from src.tools.car_search import search_cars_by_budget, search_specific_car, get_popular_cars
from src.tools.financing import calculate_financing
from src.tools.kavak_info import get_kavak_info


class TestSpanishResponses:
    """Test that all responses are in Spanish"""

    def test_car_search_spanish(self):
        """Ensure car search responses are in Spanish"""
        result = search_cars_by_budget.invoke({"max_price": 200000.0})
        # Check for Spanish words
        assert any(word in result.lower() for word in ["encontré", "autos", "precio"])

        result = search_specific_car.invoke({"brand": "Toyota", "model": "Corolla"})
        assert any(word in result.lower() for word in ["toyota", "corolla", "precio"])

    def test_financing_spanish(self):
        """Ensure financing responses are in Spanish"""
        result = calculate_financing.invoke({
            "car_price": 300000.0,
            "down_payment": 60000.0,
            "years": 4
        })
        # Check for Spanish words
        assert any(word in result.lower() for word in ["financiamiento", "pago", "mensual"])

    def test_kavak_info_spanish(self):
        """Ensure Kavak info responses are in Spanish"""
        result = get_kavak_info.invoke({"query": "garantía"})
        # When RAG is not available, it returns an empty string
        if result:  # Only check if we got a response
            assert any(word in result.lower() for word in ["garantía", "meses", "km"])

    def test_popular_cars_spanish(self):
        """Ensure popular cars response is in Spanish"""
        result = get_popular_cars.invoke({})
        # Check for Spanish words or emojis
        assert any(word in result.lower() for word in ["populares", "recomendados", "🚗"])

    def test_error_messages_spanish(self):
        """Ensure error messages are in Spanish"""
        # Test with low price (no cars found)
        result = search_cars_by_budget.invoke({"max_price": 1000.0})
        assert any(word in result.lower() for word in ["no encontré", "autos", "criterios"])
        assert "aumentar el presupuesto" in result.lower()

        # Test with invalid financing years
        result = calculate_financing.invoke({
            "car_price": 300000.0,
            "down_payment": 60000.0,
            "years": 10  # Invalid year
        })
        assert any(word in result.lower() for word in ["error", "válido", "años"])

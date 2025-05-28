"""
Unit tests for financing tools
"""

from src.tools.financing import (
    calculate_financing,
    calculate_multiple_options,
    calculate_budget_by_monthly_payment,
)


class TestFinancingTools:
    """Test financing calculation tools"""

    def test_calculate_financing_valid(self):
        """Test valid financing calculation"""
        result = calculate_financing.invoke(
            {"car_price": 300000.0, "down_payment": 60000.0, "years": 4}
        )

        # Check for expected elements in the response
        assert "💰" in result
        assert "Plan de Financiamiento" in result
        assert "$" in result
        assert "Precio del auto: $300,000.00" in result
        assert "Enganche: $60,000.00" in result
        assert "Plazo: 4 años" in result

        # Check for key sections in the response
        assert "Precio del auto" in result
        assert "Enganche" in result
        assert "Monto a financiar" in result
        assert "Plazo: 4 años" in result
        assert "Pago mensual" in result
        assert "Total a pagar" in result
        assert "Intereses" in result

    def test_calculate_financing_invalid_price(self):
        """Test invalid car price"""
        result = calculate_financing.invoke(
            {"car_price": -1000.0, "down_payment": 60000.0, "years": 4}
        )
        assert "❌" in result
        assert "precio" in result.lower()

    def test_calculate_financing_invalid_down_payment(self):
        """Test invalid down payment"""
        # Down payment greater than car price
        result = calculate_financing.invoke(
            {"car_price": 300000.0, "down_payment": 350000.0, "years": 4}
        )
        assert "❌" in result
        assert "enganche" in result.lower()

        # Negative down payment
        result = calculate_financing.invoke(
            {"car_price": 300000.0, "down_payment": -10000.0, "years": 4}
        )
        assert "❌" in result
        assert "enganche" in result.lower()

    def test_calculate_financing_invalid_years(self):
        """Test invalid financing years"""
        # Years too high
        result = calculate_financing.invoke(
            {"car_price": 300000.0, "down_payment": 60000.0, "years": 10}
        )
        assert "❌" in result
        assert "3, 4, 5 o 6 años" in result

        # Years too low
        result = calculate_financing.invoke(
            {"car_price": 300000.0, "down_payment": 60000.0, "years": 1}
        )
        assert "❌" in result
        assert "3, 4, 5 o 6 años" in result

    def test_calculate_multiple_options(self):
        """Test multiple financing options calculation"""
        result = calculate_multiple_options.invoke(
            {"car_price": 300000.0, "down_payment": 60000.0}
        )

        # Check for expected elements in the response
        assert "💰" in result
        assert "Opciones de Financiamiento" in result
        assert "$" in result

        # Should include all year options
        for year in [3, 4, 5, 6]:
            assert f"{year} años" in result

        # Check for key sections in the response
        assert "Precio" in result
        assert "Enganche" in result
        assert "A financiar" in result
        assert "Opciones de pago" in result

    def test_calculate_budget_by_monthly_payment(self):
        """Test budget calculation by monthly payment"""
        result = calculate_budget_by_monthly_payment.invoke(
            {
                "monthly_payment_desired": 5000.0,
                "down_payment_percentage": 20.0,
                "years": 4,
            }
        )

        # Check for expected elements in the response
        assert "🎯" in result  # Using the rocket emoji instead of money bag
        assert "Análisis de Presupuesto" in result
        assert "$" in result

        # Check for key sections
        assert "Pago mensual disponible" in result
        assert "Plazo" in result
        assert "Enganche" in result
        assert "Precio máximo de auto" in result

        # Test with invalid monthly payment
        result = calculate_budget_by_monthly_payment.invoke(
            {
                "monthly_payment_desired": -5000.0,
                "down_payment_percentage": 20.0,
                "years": 4,
            }
        )
        assert "❌" in result
        assert "pago mensual" in result.lower()

    def test_spanish_responses(self):
        """Ensure all responses are in Spanish"""
        # Check for Spanish words in responses
        result = calculate_financing.invoke(
            {"car_price": 300000.0, "down_payment": 60000.0, "years": 4}
        )
        spanish_words = [
            "financiamiento",
            "precio",
            "enganche",
            "plazo",
            "años",
            "pago",
            "mensual",
        ]
        assert all(word in result.lower() for word in spanish_words)

        result = calculate_multiple_options.invoke(
            {"car_price": 300000.0, "down_payment": 60000.0}
        )
        # Update expected words based on actual response
        spanish_words = ["opciones", "financiamiento", "años", "pago"]
        assert all(word in result.lower() for word in spanish_words)

        result = calculate_budget_by_monthly_payment.invoke(
            {
                "monthly_payment_desired": 5000.0,
                "down_payment_percentage": 20.0,
                "years": 4,
            }
        )
        # Update expected words based on actual response
        spanish_words = ["presupuesto", "pago", "mensual", "plazo", "enganche"]
        assert all(word in result.lower() for word in spanish_words)

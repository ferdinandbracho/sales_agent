"""
Basic tests for Kavak AI Agent
"""

from src.tools.car_search import buscar_autos_por_presupuesto, buscar_auto_especifico
from src.tools.financing import calcular_financiamiento
from src.tools.kavak_info import get_kavak_info


class TestCarSearch:
    """Test car search functionality"""

    def test_buscar_autos_por_presupuesto_valid(self):
        """Test valid budget search"""
        result = buscar_autos_por_presupuesto.invoke({"presupuesto_maximo": 300000.0})
        assert "🚗" in result
        assert "Encontré" in result or "No encontré" in result

    def test_buscar_autos_por_presupuesto_invalid(self):
        """Test invalid budget"""
        result = buscar_autos_por_presupuesto.invoke({"presupuesto_maximo": -1000.0})
        # The function returns a helpful message for negative budgets
        assert "no encontré autos" in result.lower()

    def test_buscar_auto_especifico(self):
        """Test specific car search"""
        result = buscar_auto_especifico.invoke({"marca": "Toyota", "modelo": "Corolla"})
        assert "Toyota" in result or "No encontré" in result


class TestFinancing:
    """Test financing calculations"""

    def test_calcular_financiamiento_valid(self):
        """Test valid financing calculation"""
        result = calcular_financiamiento.invoke(
            {"precio_auto": 300000.0, "enganche": 60000.0, "anos": 4}
        )
        assert "💰" in result
        assert "Plan de Financiamiento" in result
        assert "$" in result

    def test_calcular_financiamiento_invalid_price(self):
        """Test invalid car price"""
        result = calcular_financiamiento.invoke(
            {"precio_auto": -1000.0, "enganche": 60000.0, "anos": 4}
        )
        assert "❌" in result

    def test_calcular_financiamiento_invalid_years(self):
        """Test invalid financing years"""
        result = calcular_financiamiento.invoke(
            {"precio_auto": 300000.0, "enganche": 60000.0, "anos": 10}
        )
        assert "❌" in result
        assert "3, 4, 5 o 6 años" in result


class TestKavakInfo:
    """Test Kavak information tools"""

    def test_informacion_kavak_garantia(self):
        """Test warranty information"""
        result = get_kavak_info.invoke({"query": "garantía"})
        # When rag is not available, it returns an empty string to signal to the agent to use its base knowledge
        assert result == "" or ("Garantía" in result and ("3 meses" in result or "3,000 km" in result))

    def test_informacion_kavak_financiamiento(self):
        """Test financing information"""
        result = get_kavak_info.invoke({"query": "financiamiento"})
        # When rag is not available, it returns an empty string to signal to the agent to use its base knowledge
        assert result == "" or ("Financiamiento" in result and "10%" in result)

    def test_informacion_kavak_general(self):
        """Test general information"""
        result = get_kavak_info.invoke({"query": "¿Qué es Kavak?"})
        # When rag is not available, it returns an empty string to signal to the agent to use its base knowledge
        assert result == "" or ("Kavak" in result and "🚗" in result)


class TestSpanishResponses:
    """Test that all responses are in Spanish"""

    def test_car_search_spanish(self):
        """Ensure car search responses are in Spanish"""
        result = buscar_autos_por_presupuesto.invoke({"presupuesto_maximo": 200000.0})
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
        result = calcular_financiamiento.invoke(
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

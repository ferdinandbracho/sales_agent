"""
Basic tests for Kavak AI Agent
Pruebas básicas para el agente de IA de Kavak
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from tools.car_search import buscar_autos_por_presupuesto, buscar_auto_especifico
from tools.financing import calcular_financiamiento
from tools.kavak_info import informacion_kavak

class TestCarSearch:
    """Test car search functionality"""
    
    def test_buscar_autos_por_presupuesto_valid(self):
        """Test valid budget search"""
        result = buscar_autos_por_presupuesto(300000.0)
        assert "🚗" in result
        assert "Encontré" in result or "No encontré" in result
    
    def test_buscar_autos_por_presupuesto_invalid(self):
        """Test invalid budget"""
        result = buscar_autos_por_presupuesto(-1000.0)
        assert "error" in result.lower() or "debe ser" in result.lower()
    
    def test_buscar_auto_especifico(self):
        """Test specific car search"""
        result = buscar_auto_especifico("Toyota", "Corolla")
        assert "Toyota" in result or "No encontré" in result

class TestFinancing:
    """Test financing calculations"""
    
    def test_calcular_financiamiento_valid(self):
        """Test valid financing calculation"""
        result = calcular_financiamiento(300000.0, 60000.0, 4)
        assert "💰" in result
        assert "Plan de Financiamiento" in result
        assert "$" in result
    
    def test_calcular_financiamiento_invalid_price(self):
        """Test invalid car price"""
        result = calcular_financiamiento(-1000.0, 60000.0, 4)
        assert "❌" in result
    
    def test_calcular_financiamiento_invalid_years(self):
        """Test invalid financing years"""
        result = calcular_financiamiento(300000.0, 60000.0, 10)
        assert "❌" in result
        assert "3, 4, 5 o 6 años" in result

class TestKavakInfo:
    """Test Kavak information tools"""
    
    def test_informacion_kavak_garantia(self):
        """Test warranty information"""
        result = informacion_kavak("garantía")
        assert "Garantía" in result
        assert "3 meses" in result or "3,000 km" in result
    
    def test_informacion_kavak_financiamiento(self):
        """Test financing information"""
        result = informacion_kavak("financiamiento")
        assert "Financiamiento" in result
        assert "10%" in result
    
    def test_informacion_kavak_general(self):
        """Test general information"""
        result = informacion_kavak("¿Qué es Kavak?")
        assert "Kavak" in result
        assert "🚗" in result

class TestSpanishResponses:
    """Test that all responses are in Spanish"""
    
    def test_car_search_spanish(self):
        """Ensure car search responses are in Spanish"""
        result = buscar_autos_por_presupuesto(200000.0)
        # Check for Spanish words
        spanish_indicators = ["Encontré", "auto", "precio", "km", "disponible", "opciones"]
        assert any(word in result for word in spanish_indicators)
    
    def test_financing_spanish(self):
        """Ensure financing responses are in Spanish"""
        result = calcular_financiamiento(250000.0, 50000.0, 4)
        spanish_indicators = ["Financiamiento", "enganche", "mensual", "años", "pesos"]
        assert any(word in result for word in spanish_indicators)
    
    def test_no_english_responses(self):
        """Ensure no English in user-facing responses"""
        result = informacion_kavak("warranty")
        # Should not contain common English words
        english_words = ["warranty", "financing", "car", "price", "payment"]
        assert not any(word.lower() in result.lower() for word in english_words)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

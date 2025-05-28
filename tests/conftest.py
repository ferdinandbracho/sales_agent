"""
Test configuration for Kavak AI Sales Agent
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import MagicMock

# Add the project root to the path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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


@pytest.fixture
def mock_knowledge_base():
    """Fixture providing a mocked knowledge base"""
    mock_kb = MagicMock()
    mock_kb.is_ready = True
    mock_kb.search_knowledge.return_value = [
        {
            "content": "Kavak ofrece garantía de 3 meses o 3,000 km en todos sus vehículos.",
            "metadata": {"category": "warranty"},
            "distance": 0.1
        }
    ]
    return mock_kb


@pytest.fixture
def mock_llm():
    """Fixture providing a mocked LLM"""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Respuesta simulada del agente")
    mock.ainvoke.return_value = MagicMock(content="Respuesta simulada del agente")
    return mock

"""
Demo Test Script for Kavak AI Agent
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from src.tools.car_search import search_cars_by_budget, search_specific_car
from src.tools.financing import calcular_financiamiento as calculate_financing, calcular_multiples_opciones as calculate_multiple_options
from src.tools.kavak_info import get_kavak_info


async def demo_car_search():
    """Demo de búsqueda de autos"""
    print("🚗 DEMO: Búsqueda de Autos")
    print("=" * 50)

    # Test 1: Budget search
    print("\n1. Búsqueda por presupuesto (300,000 pesos)")
    result = search_cars_by_budget.invoke({"max_price": 300000.0})
    print(result)

    # Test 2: Specific car search
    print("\n2. Búsqueda específica (Toyota Corolla)")
    result = search_specific_car.invoke({"brand": "Toyota", "model": "Corolla"})
    print(result)

    # Test 3: Brand search
    print("\n3. Búsqueda por marca (Nissan, presupuesto 250k)")
    result = search_cars_by_budget.invoke(
        {"max_price": 250000.0, "brand": "Nissan"}
    )
    print(result)


async def demo_financing():
    """Demo de cálculos de financiamiento"""
    print("\n\n💰 DEMO: Financiamiento")
    print("=" * 50)

    # Test 1: Basic financing calculation
    print("\n1. Financiamiento básico (Auto $300k, enganche $60k, 4 años)")
    result = calculate_financing.invoke(
        {"precio_auto": 300000.0, "enganche": 60000.0, "anos": 4}
    )
    print(result)

    # Test 2: Multiple options
    print("\n2. Múltiples opciones (Auto $250k, enganche 20%)")
    result = calculate_multiple_options.invoke(
        {"precio_auto": 250000.0, "porcentaje_enganche": 20.0}
    )
    print(result)


async def demo_kavak_info():
    """Demo de información de Kavak"""
    print("\n\n🏢 DEMO: Información de Kavak")
    print("=" * 50)

    # Test 1: General info
    print("\n1. Información general sobre Kavak")
    result = get_kavak_info.invoke({"query": "¿Qué es Kavak?"})
    print(result)

    # Test 2: Warranty info
    print("\n2. Información sobre garantías")
    result = get_kavak_info.invoke({"query": "garantía"})
    print(result)

    # Test 3: Financing info
    print("\n3. Información sobre financiamiento")
    result = get_kavak_info.invoke({"query": "financiamiento"})
    print(result)


async def demo_conversation_flow():
    """Demo de flujo completo de conversación"""
    print("\n\n🎭 DEMO: Flujo de Conversación Completa")
    print("=" * 50)

    conversation = [
        "Hola, busco un auto usado",
        "Mi presupuesto es de 300 mil pesos",
        "Me interesa un Toyota",
        "¿Cómo funciona el financiamiento?",
        "Quiero calcular mensualidades para un auto de 280 mil",
    ]

    print("Simulando conversación típica:")
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. Usuario: {message}")

        # Simple response simulation based on message content
        if "hola" in message.lower():
            print(
                "   Agente: ¡Hola! Soy tu agente de Kavak 🚗 ¿En qué te puedo ayudar?"
            )
        elif "presupuesto" in message.lower():
            result = search_cars_by_budget.invoke(
                {"max_price": 300000.0}
            )
            print(f"   Agente: {result[:200]}...")
        elif "toyota" in message.lower():
            result = search_specific_car.invoke(
                {"brand": "Toyota", "model": "Corolla"}
            )
            print(f"   Agente: {result[:200]}...")
        elif "financiamiento" in message.lower():
            result = get_kavak_info.invoke({"query": "financiamiento"})
            print(f"   Agente: {result[:200]}...")
        elif "calcular" in message.lower():
            result = calculate_financing.invoke(
                {"precio_auto": 280000.0, "enganche": 280000 * 0.2, "anos": 4}
            )
            print(f"   Agente: {result[:200]}...")


async def main():
    """Run all demo scenarios"""
    print("🚗 KAVAK AI AGENT - DEMO SCENARIOS")
    print("=" * 60)
    print("Testing agent tools and conversation flows...")

    try:
        await demo_car_search()
        await demo_financing()
        await demo_kavak_info()
        await demo_conversation_flow()

        print("\n\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🎯 Next steps:")
        print("1. Configure ngrok to expose your local server")
        print("2. Set up Twilio webhook with your ngrok URL")
        print("3. Run 'make dev' to start the API server")
        print("4. Test WhatsApp integration with Twilio")

    except Exception as e:
        print(f"\n❌ DEMO FAILED: {e}")
        print("Please check the configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main())

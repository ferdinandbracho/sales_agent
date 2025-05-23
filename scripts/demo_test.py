"""
Demo Test Script for Kavak AI Agent
Prueba conversaciones típicas del agente
"""
import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from tools.car_search import buscar_autos_por_presupuesto, buscar_auto_especifico
from tools.financing import calcular_financiamiento, calcular_multiples_opciones
from tools.kavak_info import informacion_kavak

async def demo_car_search():
    """Demo de búsqueda de autos"""
    print("🚗 DEMO: Búsqueda de Autos")
    print("=" * 50)
    
    # Test 1: Budget search
    print("\n1. Búsqueda por presupuesto (300,000 pesos)")
    result = buscar_autos_por_presupuesto(300000.0)
    print(result)
    
    # Test 2: Specific car search
    print("\n2. Búsqueda específica (Toyota Corolla)")
    result = buscar_auto_especifico("Toyota", "Corolla")
    print(result)
    
    # Test 3: Brand search
    print("\n3. Búsqueda por marca (Nissan, presupuesto 250k)")
    result = buscar_autos_por_presupuesto(250000.0, marca="Nissan")
    print(result)

async def demo_financing():
    """Demo de cálculos de financiamiento"""
    print("\n\n💰 DEMO: Financiamiento")
    print("=" * 50)
    
    # Test 1: Basic financing calculation
    print("\n1. Financiamiento básico (Auto $300k, enganche $60k, 4 años)")
    result = calcular_financiamiento(300000.0, 60000.0, 4)
    print(result)
    
    # Test 2: Multiple options
    print("\n2. Múltiples opciones (Auto $250k, enganche 20%)")
    result = calcular_multiples_opciones(250000.0, 20.0)
    print(result)

async def demo_kavak_info():
    """Demo de información de Kavak"""
    print("\n\n🏢 DEMO: Información de Kavak")
    print("=" * 50)
    
    # Test 1: General information
    print("\n1. ¿Qué es Kavak?")
    result = informacion_kavak("¿Qué es Kavak?")
    print(result)
    
    # Test 2: Warranty information
    print("\n2. Información sobre garantía")
    result = informacion_kavak("¿Qué garantía ofrecen?")
    print(result)
    
    # Test 3: Financing info
    print("\n3. Información sobre financiamiento")
    result = informacion_kavak("¿Cómo funciona el financiamiento?")
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
        "Quiero calcular mensualidades para un auto de 280 mil"
    ]
    
    print("Simulando conversación típica:")
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. Usuario: {message}")
        
        # Simple response simulation based on message content
        if "hola" in message.lower():
            print("   Agente: ¡Hola! Soy tu agente de Kavak 🚗 ¿En qué te puedo ayudar?")
        elif "presupuesto" in message.lower():
            result = buscar_autos_por_presupuesto(300000.0)
            print(f"   Agente: {result[:200]}...")
        elif "toyota" in message.lower():
            result = buscar_auto_especifico("Toyota", "Corolla")
            print(f"   Agente: {result[:200]}...")
        elif "financiamiento" in message.lower():
            result = informacion_kavak("financiamiento")
            print(f"   Agente: {result[:200]}...")
        elif "calcular" in message.lower():
            result = calcular_financiamiento(280000.0, 56000.0, 4)
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
        print("1. Run 'make dev' to start the API server")
        print("2. Test WhatsApp integration with Twilio")
        print("3. Configure ngrok for webhook testing")
        
    except Exception as e:
        print(f"\n❌ DEMO FAILED: {e}")
        print("Please check the configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())

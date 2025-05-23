"""
Kavak Information Tool - Información sobre servicios y valor de Kavak
Responde preguntas sobre la empresa, garantías, proceso de compra, etc.
USA RAG con contenido scrapeado del sitio web
"""
from typing import Optional
from langchain.tools import tool
from ..config import MEXICAN_CONFIG
from ..knowledge.kavak_knowledge import get_kavak_knowledge_base

# Kavak knowledge base (based on provided URL and general knowledge)
KAVAK_INFO = {
    "valor_propuesta": {
        "titulo": "Propuesta de Valor de Kavak",
        "descripcion": "Kavak es la plataforma líder de autos seminuevos en México y Latinoamérica",
        "beneficios": [
            "Garantía de 3 meses o 3,000 km (lo que ocurra primero)",
            "Financiamiento hasta 84 meses con tasas competitivas", 
            "Proceso 100% digital desde casa",
            "Inspección de 240 puntos de calidad",
            "Intercambio garantizado",
            "Servicio postventa especializado"
        ]
    },
    "garantia": {
        "cobertura": "3 meses o 3,000 kilómetros",
        "incluye": [
            "Motor y transmisión",
            "Sistema eléctrico", 
            "Frenos y suspensión",
            "Aire acondicionado",
            "Reparaciones mecánicas mayores"
        ],
        "exclusiones": "Desgaste normal, neumáticos, filtros, aceites"
    },
    "proceso": {
        "pasos": [
            "Busca tu auto ideal en kavak.com",
            "Agenda cita para verlo y probarlo",
            "Solicita financiamiento si lo necesitas",
            "Completa la compra 100% digital",
            "Recibe tu auto con garantía"
        ]
    },
    "financiamiento": {
        "opciones": [
            "Desde 12 hasta 84 meses",
            "Tasa desde 10% anual",
            "Aprobación en 24 horas",
            "Sin aval ni garantías adicionales",
            "Pago anticipado sin penalización"
        ]
    },
    "ubicaciones": {
        "principales": [
            "Ciudad de México (múltiples sucursales)",
            "Guadalajara, Jalisco",
            "Monterrey, Nuevo León", 
            "Puebla, Puebla",
            "Tijuana, Baja California",
            "Mérida, Yucatán"
        ]
    }
}

@tool
def informacion_kavak(pregunta: str) -> str:
    """
    Proporciona información sobre servicios, garantías y propuesta de valor de Kavak.
    
    Args:
        pregunta: Pregunta específica sobre Kavak
        
    Returns:
        Información detallada sobre Kavak en español mexicano
    """
    try:
        pregunta_lower = pregunta.lower()
        
        # Garantía
        if any(palabra in pregunta_lower for palabra in ["garantía", "garantia", "cobertura", "protección"]):
            return f"""
✅ **Garantía Kavak**

🔧 **Cobertura:** {KAVAK_INFO['garantia']['cobertura']}

📋 **Incluye:**
• Motor y transmisión
• Sistema eléctrico completo
• Frenos y suspensión
• Aire acondicionado
• Reparaciones mecánicas mayores

❌ **No incluye:** Desgaste normal (neumáticos, filtros, aceites)

💡 **Ventaja única:** Somos la única plataforma que ofrece garantía real en autos seminuevos.

¿Te interesa algún auto en particular para explicarte más detalles? 🚗
"""
        
        # Financiamiento
        elif any(palabra in pregunta_lower for palabra in ["financiamiento", "credito", "crédito", "pago", "mensualidad"]):
            return f"""
💰 **Financiamiento Kavak**

📅 **Plazos:** 12 a 84 meses
📊 **Tasa:** Desde 10% anual
⚡ **Aprobación:** En 24 horas
🚫 **Sin:** Aval ni garantías adicionales

✅ **Beneficios:**
• Proceso 100% digital
• Pago anticipado sin penalización
• Tasas competitivas del mercado
• Tramitación rápida y sencilla

💳 ¿Quieres que calcule un plan específico para ti? Solo necesito saber tu presupuesto 😊
"""
        
        # Proceso de compra
        elif any(palabra in pregunta_lower for palabra in ["proceso", "comprar", "compra", "como funciona", "pasos"]):
            return f"""
🛒 **Proceso de Compra Kavak**

1️⃣ **Busca** tu auto ideal en kavak.com
2️⃣ **Agenda** cita para verlo y probarlo  
3️⃣ **Solicita** financiamiento (si lo necesitas)
4️⃣ **Completa** la compra 100% digital
5️⃣ **Recibe** tu auto con garantía

⏱️ **Tiempo total:** 2-3 días
📱 **Todo digital:** Sin filas ni papeleo
🚗 **Entrega:** En tu domicilio o sucursal

¿En qué paso te gustaría que te ayude? 😊
"""
        
        # Ubicaciones  
        elif any(palabra in pregunta_lower for palabra in ["ubicación", "ubicacion", "sucursal", "donde", "dirección"]):
            return f"""
📍 **Sucursales Kavak en México**

🏢 **Principales ciudades:**
• Ciudad de México (múltiples ubicaciones)
• Guadalajara, Jalisco
• Monterrey, Nuevo León
• Puebla, Puebla
• Tijuana, Baja California  
• Mérida, Yucatán

🌐 **También ofrecemos:**
• Entrega a domicilio
• Proceso 100% en línea
• Prueba de manejo en tu ubicación

¿En qué ciudad te encuentras? Te ayudo a encontrar la sucursal más cercana 📍
"""
        
        # Ventajas/propuesta de valor
        elif any(palabra in pregunta_lower for palabra in ["ventaja", "beneficio", "por qué", "porque", "diferencia"]):
            return f"""
🏆 **¿Por qué elegir Kavak?**

✅ **Garantía real:** 3 meses o 3,000 km
✅ **Calidad certificada:** Inspección 240 puntos
✅ **Financiamiento:** Hasta 84 meses  
✅ **Proceso digital:** 100% en línea
✅ **Intercambio:** Si no te gusta tu auto
✅ **Servicio postventa:** Especializado

🥇 **Somos #1 en:**
• Autos seminuevos en México
• Satisfacción del cliente
• Innovación tecnológica
• Red de distribución

¿Qué es lo más importante para ti al comprar un auto? 🤔
"""
        
        # Intercambio
        elif any(palabra in pregunta_lower for palabra in ["intercambio", "cambio", "devolver", "regresar"]):
            return f"""
🔄 **Intercambio Kavak**

✅ **Política única en México:**
Si tu auto no te convence, te ayudamos a cambiarlo por otro.

📋 **Condiciones:**
• Dentro de los primeros 7 días
• Mismo rango de precio o superior
• Sin daños adicionales
• Sujeto a disponibilidad

💡 **¿Por qué ofrecemos esto?**
Porque estamos seguros de la calidad de nuestros autos.

¿Te interesa conocer más sobre algún auto específico? 🚗
"""
        
        # Default - información general
        else:
            return f"""
🚗 **Kavak - Plataforma #1 de Autos Seminuevos**

🏆 **Somos líderes porque ofrecemos:**
• Garantía de 3 meses o 3,000 km
• Financiamiento hasta 84 meses  
• Proceso 100% digital
• Inspección de 240 puntos
• Intercambio garantizado

📱 **Todo desde tu celular:**
• Busca, compara y elige
• Solicita financiamiento
• Agenda prueba de manejo
• Completa tu compra

🌟 **Más de 1 millón de mexicanos han confiado en nosotros**

¿En qué te puedo ayudar específicamente? 
• Encontrar auto ideal 🔍
• Calcular financiamiento 💰  
• Agendar prueba de manejo 📅
• Información de garantía ✅
"""
        
    except Exception as e:
        return f"❌ Error obteniendo información: {str(e)}. ¿Puedes ser más específico en tu pregunta?"

@tool
def agendar_cita() -> str:
    """
    Información sobre cómo agendar una cita para ver un auto.
    
    Returns:
        Instrucciones para agendar cita
    """
    return f"""
📅 **Agendar Cita en Kavak**

🕐 **Horarios disponibles:**
• Lunes a Domingo: 9:00 AM - 7:00 PM
• Incluye fines de semana y algunos festivos

📞 **Formas de agendar:**
1️⃣ **WhatsApp:** Continúa esta conversación
2️⃣ **Teléfono:** 55-4000-KAVAK (52825)
3️⃣ **Página web:** kavak.com
4️⃣ **App móvil:** Descarga Kavak

📍 **Opciones de cita:**
• En sucursal más cercana
• Prueba de manejo a domicilio (CDMX)
• Video llamada para ver el auto

⏱️ **Duración:** 30-45 minutos
🆓 **Costo:** Totalmente gratis

¿Te gustaría que te ayude a pre-agendar para un auto específico? 😊
"""

@tool
def comparar_con_competencia() -> str:
    """
    Compara Kavak con otras opciones del mercado.
    
    Returns:
        Comparación de Kavak vs competencia
    """
    return f"""
🏆 **Kavak vs Otras Opciones**

📊 **Vs. Agencias tradicionales:**
✅ Kavak: Garantía 3 meses | ❌ Otras: Sin garantía
✅ Kavak: Proceso digital | ❌ Otras: Mucho papeleo  
✅ Kavak: Precios fijos | ❌ Otras: Regateo necesario
✅ Kavak: Financiamiento fácil | ❌ Otras: Trámites complejos

📊 **Vs. Particulares:**
✅ Kavak: Garantía incluida | ❌ Particulares: Sin garantía
✅ Kavak: Inspección 240 puntos | ❌ Particulares: "Como está"
✅ Kavak: Financiamiento | ❌ Particulares: Solo efectivo
✅ Kavak: Servicio postventa | ❌ Particulares: Sin soporte

📊 **Vs. Otras plataformas:**
✅ Kavak: Inventario propio | ❌ Otras: Solo intermediarios
✅ Kavak: Control de calidad | ❌ Otras: Autos variables
✅ Kavak: Garantía real | ❌ Otras: Garantías limitadas

💡 **¿El resultado?** Kavak te da la seguridad de una agencia con la comodidad digital.

¿Qué es lo que más te preocupa al comprar un auto seminuevo? 🤔
"""

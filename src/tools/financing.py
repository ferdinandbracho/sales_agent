"""
Financing Tool - Herramienta de cálculo de financiamiento
Calcula planes de pago para autos con tasa del 10% anual
"""

import math
from typing import Dict, List, Optional

from langchain.tools import tool

from ..config import MEXICAN_CONFIG


@tool
def calcular_financiamiento(precio_auto: float, enganche: float, anos: int = 4) -> str:
    """
    Calcula el financiamiento para un auto con tasa del 10% anual.

    Args:
        precio_auto: Precio total del vehículo en pesos
        enganche: Monto del enganche en pesos
        anos: Años de financiamiento (3-6 años disponibles)

    Returns:
        Plan de financiamiento detallado en español
    """
    try:
        # Validate inputs
        if precio_auto <= 0:
            return "❌ El precio del auto debe ser mayor a $0. ¿Puedes verificar?"

        if enganche < 0 or enganche >= precio_auto:
            return "❌ El enganche debe ser entre $0 y menor al precio del auto. ¿Puedes verificar?"

        if anos not in [3, 4, 5, 6]:
            return "❌ Los plazos disponibles son: 3, 4, 5 o 6 años. ¿Cuál prefieres?"

        # Calculate financing
        monto_financiar = precio_auto - enganche
        tasa_anual = 0.10  # 10% as specified
        tasa_mensual = tasa_anual / 12
        meses = anos * 12

        if monto_financiar <= 0:
            return f"""
✅ ¡Excelente! Con un enganche de ${enganche:,.2f} pagas el auto completo.
No necesitas financiamiento. 

¿Te ayudo con los trámites de compra? 🚗
"""

        # Monthly payment formula
        pago_mensual = (
            monto_financiar
            * (tasa_mensual * (1 + tasa_mensual) ** meses)
            / ((1 + tasa_mensual) ** meses - 1)
        )
        total_pagar = pago_mensual * meses
        intereses_totales = total_pagar - monto_financiar

        respuesta = f"""
💰 **Plan de Financiamiento Kavak**

🚗 Precio del auto: ${precio_auto:,.2f}
💵 Enganche: ${enganche:,.2f} ({(enganche/precio_auto)*100:.1f}%)
📊 Monto a financiar: ${monto_financiar:,.2f}

⏱️ **Plazo: {anos} años**
📅 Pago mensual: ${pago_mensual:,.2f}
💳 Total a pagar: ${total_pagar:,.2f}
📈 Intereses: ${intereses_totales:,.2f}

✅ Tasa de interés: 10% anual
✅ Sin penalización por pago anticipado
✅ Proceso 100% digital
"""

        # Add comparison with other terms
        if anos != 4:  # Show alternative if not default
            alt_anos = 4
            alt_meses = alt_anos * 12
            alt_pago = (
                monto_financiar
                * (tasa_mensual * (1 + tasa_mensual) ** alt_meses)
                / ((1 + tasa_mensual) ** alt_meses - 1)
            )
            respuesta += f"\n💡 En {alt_anos} años serían ${alt_pago:,.2f}/mes"

        respuesta += (
            "\n\n¿Te funciona este plan? ¿Quieres ver otras opciones de enganche? 😊"
        )

        return respuesta

    except Exception as e:
        return f"❌ Error calculando financiamiento: {str(e)}. ¿Puedes verificar los números?"


@tool
def calcular_multiples_opciones(
    precio_auto: float, porcentaje_enganche: float = 20.0
) -> str:
    """
    Calcula múltiples opciones de financiamiento para diferentes plazos.

    Args:
        precio_auto: Precio del vehículo
        porcentaje_enganche: Porcentaje de enganche (default 20%)

    Returns:
        Tabla comparativa de opciones de financiamiento
    """
    try:
        if precio_auto <= 0:
            return "❌ El precio debe ser mayor a $0"

        if porcentaje_enganche < 0 or porcentaje_enganche > 100:
            return "❌ El porcentaje de enganche debe estar entre 0% y 100%"

        enganche = precio_auto * (porcentaje_enganche / 100)
        monto_financiar = precio_auto - enganche
        tasa_mensual = 0.10 / 12  # 10% anual

        respuesta = f"""
💰 **Opciones de Financiamiento Kavak**

🚗 Precio: ${precio_auto:,.2f}
💵 Enganche ({porcentaje_enganche:.0f}%): ${enganche:,.2f}
📊 A financiar: ${monto_financiar:,.2f}

**Opciones de pago:**
"""

        for anos in [3, 4, 5, 6]:
            meses = anos * 12
            pago_mensual = (
                monto_financiar
                * (tasa_mensual * (1 + tasa_mensual) ** meses)
                / ((1 + tasa_mensual) ** meses - 1)
            )
            total_pagar = pago_mensual * meses

            respuesta += f"""
📅 **{anos} años:** ${pago_mensual:,.2f}/mes (Total: ${total_pagar:,.2f})
"""

        respuesta += f"""
✅ Tasa: 10% anual fija
✅ Sin comisiones ocultas
✅ Aprobación en 24 horas

¿Cuál plazo te conviene más? 😊"""

        return respuesta

    except Exception as e:
        return f"❌ Error en cálculos: {str(e)}"


@tool
def calcular_presupuesto_por_mensualidad(
    pago_mensual_deseado: float, anos: int = 4, porcentaje_enganche: float = 20.0
) -> str:
    """
    Calcula qué precio de auto puede permitirse con una mensualidad específica.

    Args:
        pago_mensual_deseado: Pago mensual que puede permitirse
        anos: Años de financiamiento
        porcentaje_enganche: Porcentaje de enganche

    Returns:
        Precio máximo de auto que puede comprar
    """
    try:
        if pago_mensual_deseado <= 0:
            return "❌ El pago mensual debe ser mayor a $0"

        if anos not in [3, 4, 5, 6]:
            return "❌ Los plazos disponibles son: 3, 4, 5 o 6 años"

        tasa_mensual = 0.10 / 12
        meses = anos * 12

        # Calculate maximum loan amount from desired payment
        monto_max_financiar = (
            pago_mensual_deseado
            * ((1 + tasa_mensual) ** meses - 1)
            / (tasa_mensual * (1 + tasa_mensual) ** meses)
        )

        # Calculate total car price including down payment
        precio_max_auto = monto_max_financiar / (1 - porcentaje_enganche / 100)
        enganche_necesario = precio_max_auto * (porcentaje_enganche / 100)

        respuesta = f"""
🎯 **Análisis de Presupuesto**

💳 Pago mensual disponible: ${pago_mensual_deseado:,.2f}
⏱️ Plazo: {anos} años
💵 Enganche ({porcentaje_enganche:.0f}%): ${enganche_necesario:,.2f}

🚗 **Precio máximo de auto: ${precio_max_auto:,.2f}**

📊 Desglose:
• Monto a financiar: ${monto_max_financiar:,.2f}
• Enganche requerido: ${enganche_necesario:,.2f}
• Total del auto: ${precio_max_auto:,.2f}

✅ Con este presupuesto tienes excelentes opciones en Kavak.

¿Quieres ver autos disponibles en este rango? 🚗"""

        return respuesta

    except Exception as e:
        return f"❌ Error calculando presupuesto: {str(e)}"


@tool
def comparar_enganche_vs_mensualidad(precio_auto: float) -> str:
    """
    Compara diferentes opciones de enganche y su impacto en la mensualidad.

    Args:
        precio_auto: Precio del vehículo

    Returns:
        Comparación de opciones de enganche
    """
    try:
        if precio_auto <= 0:
            return "❌ El precio debe ser mayor a $0"

        tasa_mensual = 0.10 / 12
        anos = 4  # Default term
        meses = anos * 12

        respuesta = f"""
🔄 **Comparación de Opciones de Enganche**
🚗 Auto: ${precio_auto:,.2f}

"""

        porcentajes_enganche = [10, 20, 30, 40, 50]

        for porcentaje in porcentajes_enganche:
            enganche = precio_auto * (porcentaje / 100)
            monto_financiar = precio_auto - enganche

            if monto_financiar > 0:
                pago_mensual = (
                    monto_financiar
                    * (tasa_mensual * (1 + tasa_mensual) ** meses)
                    / ((1 + tasa_mensual) ** meses - 1)
                )
                respuesta += f"💰 {porcentaje}% enganche: ${enganche:,.0f} → ${pago_mensual:,.0f}/mes\n"
            else:
                respuesta += f"💰 {porcentaje}% enganche: ${enganche:,.0f} → Auto pagado completo\n"

        respuesta += f"""
💡 **Recomendación:** 
Mayor enganche = menor mensualidad = menos intereses totales

¿Qué porcentaje de enganche te conviene más? 😊"""

        return respuesta

    except Exception as e:
        return f"❌ Error en comparación: {str(e)}"

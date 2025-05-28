"""
Financing Tool

This module provides tools for calculating car financing options with Kavak.
"""

from langchain.tools import tool

from src.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


@tool
def calculate_financing(car_price: float, down_payment: float, years: int = 4) -> str:
    """
    Calculates car financing with a 10% annual interest rate.

    The response will be in Spanish to match the user's language.

    Args:
        car_price: Total vehicle price in MXN
        down_payment: Down payment amount in MXN
        years: Financing term in years (3-6 years available)

    Returns:
        Detailed financing plan in Spanish
    """
    logger.info(
        "Calculating financing",
        extra={
            "car_price": car_price,
            "down_payment": down_payment,
            "years": years,
        },
    )

    try:
        # Validate inputs
        if car_price <= 0:
            error_msg = "El precio del auto debe ser mayor a $0"
            logger.warning(error_msg, extra={"car_price": car_price})
            return f"❌ {error_msg}. ¿Puedes verificar?"

        if down_payment < 0 or down_payment >= car_price:
            error_msg = "El enganche debe ser entre $0 y menor al precio del auto"
            logger.warning(
                error_msg, extra={"down_payment": down_payment, "car_price": car_price}
            )
            return f"❌ {error_msg}. ¿Puedes verificar?"

        if years not in [3, 4, 5, 6]:
            error_msg = f"Plazo no válido: {years}. Los plazos disponibles son: 3, 4, 5 o 6 años"
            logger.warning(error_msg)
            return f"❌ {error_msg}. ¿Cuál prefieres?"

        # Calculate financing
        amount_to_financier = car_price - down_payment
        annual_interest_rate = 0.10  # 10% as specified
        monthly_interest_rate = annual_interest_rate / 12
        months = years * 12

        if amount_to_financier <= 0:
            logger.info(
                "No financing needed - down payment covers full car price",
                extra={"down_payment": down_payment, "car_price": car_price},
            )
            return f"""
            ✅ ¡Excelente! Con un enganche de ${down_payment:,.2f} pagas el auto completo.
            No necesitas financiamiento. 

            ¿Te ayudo con los trámites de compra? 🚗
            """

        # Monthly payment formula
        # General formula for a fixed-rate mortgage/loan: P = (PV * r * (1 + r)^n) / ((1 + r)^n - 1)
        monthly_payment = (
            amount_to_financier
            * (monthly_interest_rate * (1 + monthly_interest_rate) ** months)
            / ((1 + monthly_interest_rate) ** months - 1)
        )
        total_amount = monthly_payment * months
        total_interests = total_amount - amount_to_financier

        # Log successful calculation
        logger.info(
            "Financing calculation successful",
            extra={
                "monthly_payment": monthly_payment,
                "total_amount": total_amount,
                "total_interests": total_interests,
                "years": years,
            },
        )

        response = f"""
        💰 **Plan de Financiamiento Kavak**

        🚗 Precio del auto: ${car_price:,.2f}
        💵 Enganche: ${down_payment:,.2f} ({(down_payment / car_price) * 100:.1f}%)
        📊 Monto a financiar: ${amount_to_financier:,.2f}

        ⏱️ **Plazo: {years} años**
        📅 Pago mensual: ${monthly_payment:,.2f}
        💳 Total a pagar: ${total_amount:,.2f}
        📈 Intereses: ${total_interests:,.2f}

        ✅ Tasa de interés: 10% anual
        ✅ Sin penalización por pago anticipado
        ✅ Proceso 100% digital
        """

        # Add comparison with other terms
        if years != 4:  # Show alternative if not default
            alt_years = 4
            alt_months = alt_years * 12
            alt_payment = (
                amount_to_financier
                * (monthly_interest_rate * (1 + monthly_interest_rate) ** alt_months)
                / ((1 + monthly_interest_rate) ** alt_months - 1)
            )
            response += f"\n💡 En {alt_years} años serían ${alt_payment:,.2f}/mes"

        response += (
            "\n\n¿Te funciona este plan? ¿Quieres ver otras opciones de enganche? 😊"
        )

        return response

    except Exception as e:
        logger.error(
            "Error calculating financing",
            exc_info=True,
            extra={
                "car_price": car_price,
                "down_payment": down_payment,
                "years": years,
                "error": str(e),
            },
        )
        return f"❌ Error calculando financiamiento: {str(e)}. ¿Puedes verificar los números?"


@tool
def calculate_multiple_options(
    car_price: float, down_payment_percentage: float = 20.0
) -> str:
    """
    Calculate multiple financing options for different terms.

    Args:
        car_price: Vehicle price in MXN
        down_payment_percentage: Down payment percentage (default 20%)

    Returns:
        Comparison table of financing options in Spanish
    """
    logger.info(
        "Calculating multiple financing options",
        extra={
            "car_price": car_price,
            "down_payment_percentage": down_payment_percentage,
        },
    )
    """
    Calculate multiple financing options for different terms.

    Args:
        car_price: Vehicle price
        down_payment_percentage: Down payment percentage (default 20%)

    Returns:
        Comparison table of financing options
    """
    try:
        if car_price <= 0:
            error_msg = "El precio del auto debe ser mayor a $0"
            logger.warning(error_msg, extra={"car_price": car_price})
            return f"❌ {error_msg}"

        if down_payment_percentage < 0 or down_payment_percentage > 100:
            error_msg = "El porcentaje de enganche debe estar entre 0% y 100%"
            logger.warning(
                error_msg, extra={"down_payment_percentage": down_payment_percentage}
            )
            return f"❌ {error_msg}"

        down_payment = car_price * (down_payment_percentage / 100)
        amount_to_financier = car_price - down_payment
        monthly_interest_rate = 0.10 / 12  # 10% anual

        logger.info(
            "Multiple options calculation successful",
            extra={
                "amount_to_financier": amount_to_financier,
                "down_payment": down_payment,
            },
        )

        response = f"""
        💰 **Opciones de Financiamiento Kavak**

        🚗 Precio: ${car_price:,.2f}
        💵 Enganche ({down_payment_percentage:.0f}%): ${down_payment:,.2f}
        📊 A financiar: ${amount_to_financier:,.2f}

        **Opciones de pago:**
        """

        for years in [3, 4, 5, 6]:
            months = years * 12
            monthly_payment = (
                amount_to_financier
                * (monthly_interest_rate * (1 + monthly_interest_rate) ** months)
                / ((1 + monthly_interest_rate) ** months - 1)
            )
            total_amount = monthly_payment * months

            response += f"""
            📅 **{years} años:** ${monthly_payment:,.2f}/mes (Total: ${total_amount:,.2f})
            """

        response += f"""
        ✅ Tasa: 10% anual fija
        ✅ Sin comisiones ocultas
        ✅ Aprobación en 24 horas

        ¿Cuál plazo te conviene más? 😊"""

        return response

    except Exception as e:
        logger.error(
            "Error calculating multiple options",
            exc_info=True,
            extra={
                "car_price": car_price,
                "down_payment_percentage": down_payment_percentage,
                "error": str(e),
            },
        )
        return f"❌ Error en cálculos: {str(e)}"


@tool
def calculate_budget_by_monthly_payment(
    monthly_payment_desired: float,
    years: int = 4,
    down_payment_percentage: float = 20.0,
) -> str:
    """
    Calculate the maximum car price that can be afforded with a specific monthly payment.

    Args:
        monthly_payment_desired: Monthly payment that can be afforded in MXN
        years: Financing term in years (default: 4)
        down_payment_percentage: Down payment percentage (default: 20%)

    Returns:
        Maximum car price that can be afforded with the given parameters
    """
    logger.info(
        "Calculating budget by monthly payment",
        extra={
            "monthly_payment_desired": monthly_payment_desired,
            "years": years,
            "down_payment_percentage": down_payment_percentage,
        },
    )
    """
    Calculate the maximum car price that can be afforded with a specific monthly payment.

    Args:
        monthly_payment_desired: Monthly payment that can be afforded
        years: Financing term in years
        down_payment_percentage: Down payment percentage

    Returns:
        Maximum car price that can be afforded
    """
    try:
        if monthly_payment_desired <= 0:
            error_msg = "El pago mensual debe ser mayor a $0"
            logger.warning(
                error_msg, extra={"monthly_payment_desired": monthly_payment_desired}
            )
            return f"❌ {error_msg}"

        if years not in [3, 4, 5, 6]:
            error_msg = f"Plazo no válido: {years}. Los plazos disponibles son: 3, 4, 5 o 6 años"
            logger.warning(error_msg, extra={"years": years})
            return f"❌ {error_msg}"

        monthly_interest_rate = 0.10 / 12
        months = years * 12

        # Calculate maximum loan amount from desired payment
        max_amount_to_financier = (
            monthly_payment_desired
            * ((1 + monthly_interest_rate) ** months - 1)
            / (monthly_interest_rate * (1 + monthly_interest_rate) ** months)
        )

        # Calculate total car price including down payment
        max_car_price = max_amount_to_financier / (1 - down_payment_percentage / 100)
        down_payment = max_car_price * (down_payment_percentage / 100)

        logger.info(
            "Budget calculation successful",
            extra={
                "max_car_price": max_car_price,
                "down_payment": down_payment,
                "monthly_payment_desired": monthly_payment_desired,
                "years": years,
            },
        )

        response = f"""
        🎯 **Análisis de Presupuesto**

        💳 Pago mensual disponible: ${monthly_payment_desired:,.2f}
        ⏱️ Plazo: {years} años
        💵 Enganche ({down_payment_percentage:.0f}%): ${down_payment:,.2f}

        🚗 **Precio máximo de auto: ${max_car_price:,.2f}**

        📊 Desglose:
        • Monto a financiar: ${max_amount_to_financier:,.2f}
        • Enganche requerido: ${down_payment:,.2f}
        • Total del auto: ${max_car_price:,.2f}

        ✅ Con este presupuesto tienes excelentes opciones en Kavak.

        ¿Quieres ver autos disponibles en este rango? 🚗"""

        return response

    except Exception as e:
        logger.error(
            "Error calculating budget by monthly payment",
            exc_info=True,
            extra={
                "monthly_payment_desired": monthly_payment_desired,
                "years": years,
                "down_payment_percentage": down_payment_percentage,
                "error": str(e),
            },
        )
        return f"❌ Error en el cálculo: {str(e)}"

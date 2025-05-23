# 🚗 Kavak AI Sales Agent

Un agente comercial inteligente para Kavak México que opera via WhatsApp, capaz de recomendar autos, calcular financiamiento y responder preguntas sobre los servicios de Kavak.

## 🎯 Características

- **Búsqueda de Autos**: Búsqueda inteligente por presupuesto, marca y preferencias
- **Calculadora de Financiamiento**: Planes de pago con tasa del 10% anual (3-6 años)
- **Información de Kavak**: Garantías, proceso de compra y servicios
- **Integración WhatsApp**: Chat en vivo via Twilio
- **Procesamiento en Español**: Agente 100% en español mexicano
- **Memoria Conversacional**: Mantiene contexto durante toda la conversación

## 🚀 Inicio Rápido (5 minutos)

### Prerrequisitos
- Python 3.11+
- UV package manager
- Cuenta de OpenAI (API key proporcionada)
- Cuenta de Twilio (sandbox gratuito)

### Instalación

1. **Clonar el repositorio**
```bash
cd /Users/ferdinandbracho/code/projects/kavak_challenge/commercial_agent
```

2. **Configuración inicial**
```bash
make setup
```

3. **Configurar variables de entorno**
Editar `.env` con tus credenciales:
```bash
# API Keys
OPENAI_API_KEY=tu_clave_openai_aqui
TWILIO_ACCOUNT_SID=tu_twilio_sid
TWILIO_AUTH_TOKEN=tu_twilio_token

# Opcional para webhooks locales
NGROK_AUTHTOKEN=tu_ngrok_token
```

4. **Iniciar la aplicación**
```bash
make dev
```

¡Listo! 🎉 El agente estará disponible en `http://localhost:8000`

## 📱 Uso y Demo

### Conversaciones de Ejemplo

**Búsqueda de Auto:**
```
Usuario: Hola, busco un auto usado
Agente: ¡Hola! Soy tu agente comercial de Kavak 🚗 ¿Cuál es tu presupuesto?
Usuario: Unos 300 mil pesos
Agente: Perfecto, encontré 15 autos en tu rango...
```

**Cálculo de Financiamiento:**
```
Usuario: ¿Cuánto pagaría mensualmente por un auto de 280mil?
Agente: 💰 Plan de Financiamiento:
Precio: $280,000
Enganche (20%): $56,000  
Pago mensual: $5,690 (4 años)
```

### Comandos de Demo
```bash
make demo         # Ejecutar escenarios de demostración
make test-tools   # Probar herramientas individuales
make logs         # Ver logs de la aplicación
```

## 🏗️ Arquitectura

### Componentes Principales
- **FastAPI**: API principal y manejo de webhooks
- **LangChain**: Orquestación del agente y herramientas
- **OpenAI GPT-4o**: Modelo de lenguaje principal
- **Pandas**: Procesamiento del catálogo de autos
- **Twilio**: Integración con WhatsApp

### Flujo de Datos
```
Usuario WhatsApp → Twilio → FastAPI → Agente AI → Herramientas → Respuesta → WhatsApp
```

### Herramientas del Agente
1. **buscar_autos_por_presupuesto**: Búsqueda por rango de precio
2. **buscar_auto_especifico**: Búsqueda por marca/modelo específico
3. **calcular_financiamiento**: Cálculo de mensualidades
4. **informacion_kavak**: Información de la empresa
5. **agendar_cita**: Proceso de agendamiento
6. **comparar_con_competencia**: Ventajas de Kavak

## 📊 Datos

El sistema utiliza `sample_caso_ai_engineer.csv` con 100 vehículos de muestra incluyendo:
- Marca, modelo, año, versión
- Precio, kilometraje, dimensiones  
- Características (Bluetooth, CarPlay)

## 🛠️ Desarrollo

### Estructura del Proyecto
```
src/
├── main.py              # Aplicación FastAPI principal
├── config.py            # Configuración y settings
├── agent/               # Lógica del agente de IA
│   ├── kavak_agent.py   # Clase principal del agente
│   └── prompts.py       # Prompts en español mexicano
├── tools/               # Herramientas del agente
│   ├── car_search.py    # Búsqueda de autos
│   ├── financing.py     # Cálculos de financiamiento
│   └── kavak_info.py    # Información de Kavak
├── webhook/             # Integración WhatsApp
│   └── twilio_handler.py # Manejo de webhooks de Twilio
└── models/              # Modelos de datos
```

### Comandos de Desarrollo
```bash
make install-deps    # Instalar/actualizar dependencias
make format         # Formatear código con Black
make lint           # Verificar calidad del código
make test           # Ejecutar pruebas
make clean          # Limpiar archivos temporales
```

### Agregar Nuevas Características
1. Crear nueva herramienta en `src/tools/`
2. Registrar herramienta en el agente
3. Agregar pruebas en `tests/`
4. Actualizar documentación

## 🧪 Pruebas

### Ejecución de Pruebas
```bash
make test           # Todas las pruebas
make test-tools     # Solo herramientas
make demo           # Escenarios de demostración
```

### Prueba de Integración WhatsApp
1. Configurar webhook de Twilio: `https://tu-ngrok-url.ngrok.io/webhook/whatsapp`
2. Enviar mensaje a número sandbox de Twilio
3. Verificar respuesta del agente

## 🚀 Despliegue

### Desarrollo Local
```bash
make dev  # Servidor local con recarga automática
```

### Producción (Docker)
```bash
docker-compose --profile full up -d  # Con Redis y ChromaDB
```

### Servicios en la Nube
- **API**: Railway, Render o AWS ECS
- **Base de Datos**: Supabase PostgreSQL
- **Cache**: Redis Cloud
- **Frontend Demo**: Vercel

## 🔧 Configuración de WhatsApp

### 1. Configurar Twilio Sandbox
1. Crear cuenta en [Twilio](https://console.twilio.com)
2. Ir a Messaging → Try it out → Send a WhatsApp message
3. Enviar `join [sandbox-name]` a +1 415 523 8886

### 2. Configurar Webhook
1. Iniciar aplicación: `make dev`
2. Obtener URL pública con ngrok
3. En Twilio Console → WhatsApp Sandbox Settings
4. Webhook URL: `https://tu-ngrok-url.ngrok.io/webhook/whatsapp`

### 3. Probar Integración
Enviar mensaje a tu número sandbox de Twilio y recibir respuesta del agente.

## 📈 Roadmap de Producción

### Fase 1: Infraestructura (Semanas 1-2)
- Despliegue en la nube (AWS/GCP)
- Base de datos de producción
- Monitoreo y logging
- Implementación de seguridad

### Fase 2: Escalabilidad (Semanas 3-4)
- Balanceador de carga
- Capas de cache
- Limitación de API
- Optimización de rendimiento

### Fase 3: Características de Negocio (Semanas 5-8)
- Integración con CRM
- Calificación de leads
- Agendamiento de citas
- Análisis de ventas

### Marco de Evaluación
- **Precisión**: Recomendaciones correctas de autos (>85%)
- **Tiempo de Respuesta**: <3 segundos promedio
- **Conversión**: Tasa de demo a lead calificado
- **Satisfacción**: Tasa de finalización de conversación

## 🤝 Contribución

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear rama de característica
3. Hacer cambios con pruebas
4. Enviar pull request

### Estándares de Código
- Python 3.11+ con type hints
- Docstrings en español para lógica de negocio
- Cobertura de pruebas >80%
- Seguir convenciones de PEP 8

## 📞 Soporte

Para problemas o preguntas:
- Crear issue en GitHub
- Revisar documentación en `/docs`
- Consultar documentación de API en `/docs`

## 🏆 Logros Técnicos

### Arquitectura Moderna
- Agente de IA con herramientas especializadas
- Integración WhatsApp en tiempo real
- Memoria conversacional persistente
- Respuestas optimizadas para móvil

### Experiencia de Usuario
- Conversaciones 100% en español mexicano
- Manejo inteligente de errores tipográficos
- Cálculos financieros precisos
- Información actualizada de Kavak

### Calidad de Desarrollo
- Configuración reproducible con un comando
- Pruebas automatizadas
- Documentación completa
- Código limpio y mantenible

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

---

**Desarrollado con ❤️ para Kavak México 🇲🇽**

*Este proyecto demuestra capacidades modernas de ingeniería de IA, incluyendo agentes conversacionales, integración de APIs, y desarrollo de software profesional.*

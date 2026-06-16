# 🤖 Telegram Booking Agent for Small Businesses / Agente de Citas por Telegram

> **EN** — A robust, tested Telegram bot that answers customer questions and books
> appointments for any small business — **no API costs**: free Telegram Bot API, SQLite,
> fuzzy FAQ matching in pure Python, and an *optional* local LLM via Ollama. New client =
> new YAML file, no code changes.
>
> **ES** — Bot de Telegram robusto y probado que responde preguntas de clientes y
> agenda citas para cualquier negocio pequeño — **sin costos de API**: Bot API gratuita de
> Telegram, SQLite, matching difuso de FAQ en Python puro y LLM local *opcional* vía
> Ollama. Cliente nuevo = nuevo archivo YAML, sin tocar código.

![Python](https://img.shields.io/badge/python-3.11-blue) ![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4) ![tests](https://img.shields.io/badge/tests-11%20passing-brightgreen)

---

## 🇪🇸 Español

### El problema que resuelve

Los negocios pequeños pierden clientes por no contestar a tiempo. WhatsApp Business API
cobra por conversación; **la Bot API de Telegram es gratuita** y este bot hace el mismo trabajo:

- 💬 **Responde preguntas frecuentes** (precios, ubicación, horarios) al instante,
  con matching difuso que tolera acentos, mayúsculas y mensajes cortos ("precio?").
- 📅 **Agenda citas** con botones: servicio → horario libre → confirmación. Los
  horarios respetan días y horas de apertura y nunca se duplican (SQLite + UNIQUE).
- 🙋 **Escala a humano**: lo que no sabe responder se reenvía al chat del dueño.
- 🧠 **Opcional**: si instalas [Ollama](https://ollama.com) (gratis, local), las
  preguntas fuera del FAQ las responde un LLM usando solo la información del negocio.

### Instalación

```bash
pip install -r requirements.txt
# 1. Crea tu bot gratis con @BotFather en Telegram → copia el token
# 2. Configura el negocio
cp config.example.yaml config.yaml   # edita servicios, horarios y FAQ
# 3. Ejecuta
set TELEGRAM_BOT_TOKEN=123:abc       # Windows (export en Linux/Mac)
python scripts/run_bot.py
```

Para producción puede correr en cualquier máquina siempre encendida — una Raspberry Pi,
una PC vieja o el plan gratuito de [PythonAnywhere](https://www.pythonanywhere.com)/
[Railway](https://railway.app).

### Cada cliente es un YAML

```yaml
name: "Estética Luna"
services: ["Corte de cabello", "Tinte / color", "Manicure"]
opening_hour: 10
closing_hour: 19
slot_minutes: 60
days_open: [0, 1, 2, 3, 4, 5]
faq:
  - question: "¿Cuánto cuesta el corte?"
    answer: "Dama $250, caballero $150 💇"
    keywords: ["precio", "costo"]
```

---

## 🇬🇧 English

Small businesses lose customers to slow replies. WhatsApp Business API charges per
conversation; **Telegram is free** and this bot does the same job: instant FAQ answers
(accent/case-tolerant fuzzy matching), button-driven appointment booking on SQLite with
race-safe unique slots, human handoff for unknown questions, and an optional local LLM
(Ollama) for open-ended ones. Onboarding a new business is editing one YAML file.

```
proyecto-06-telegram-agent/
├── src/telegram_agent/   # config (YAML profile), faq, booking, bot
├── scripts/run_bot.py
├── config.example.yaml   # demo business profile
└── tests/                # 11 tests: matching, slots, double-booking, validation
```

**Architecture note**: all business logic (FAQ scoring, slot generation, booking store)
is framework-free and fully unit-tested; `bot.py` is a thin Telegram adapter — the same
core could ship a web widget or Discord bot without changes.

"""Telegram bot wiring: menus, FAQ replies, booking flow, human handoff."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .booking import BookingStore, generate_slots
from .config import BusinessProfile
from .faq import best_answer, ollama_answer

MAX_BUTTONS = 8


def _faq_context(profile: BusinessProfile) -> str:
    lines = [profile.description, "Servicios: " + ", ".join(profile.services)]
    lines += [f"P: {e.question} R: {e.answer}" for e in profile.faq]
    return "\n".join(lines)


def build_application(
    token: str, profile: BusinessProfile, db_path: Path | str
) -> Application:
    """Create the PTB application with all handlers registered."""
    store = BookingStore(db_path)

    async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            f"¡Hola! Soy el asistente de {profile.name} 🤖\n\n"
            f"{profile.description}\n\n"
            "Comandos:\n"
            "📅 /agendar — reservar una cita\n"
            "📋 /miscitas — ver o cancelar tus citas\n"
            "💬 O simplemente escríbeme tu pregunta."
        )

    async def agendar(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        buttons = [
            [InlineKeyboardButton(s, callback_data=f"svc|{s}")]
            for s in profile.services[:MAX_BUTTONS]
        ]
        await update.message.reply_text(
            "¿Qué servicio necesitas?", reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def pick_service(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        service = query.data.split("|", 1)[1]
        slots = generate_slots(
            profile, datetime.now(), taken=store.booked_slots(), max_slots=MAX_BUTTONS
        )
        if not slots:
            await query.edit_message_text(
                "No hay horarios disponibles esta semana 😔 Escríbenos y te ayudamos."
            )
            return
        buttons = [
            [InlineKeyboardButton(s, callback_data=f"slot|{service}|{s}")]
            for s in slots
        ]
        await query.edit_message_text(
            f"Horarios para *{service}*:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    async def pick_slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        _, service, slot = query.data.split("|", 2)
        user = query.from_user
        ok = store.book(query.message.chat_id, user.full_name, service, slot)
        if not ok:
            await query.edit_message_text(
                "Ese horario se acaba de ocupar 😅 Intenta con /agendar de nuevo."
            )
            return
        await query.edit_message_text(
            f"✅ Cita confirmada\n\n*{service}*\n🗓 {slot}\n\n"
            "Puedes verla o cancelarla con /miscitas",
            parse_mode="Markdown",
        )
        if profile.owner_chat_id:
            await context.bot.send_message(
                profile.owner_chat_id,
                f"📅 Nueva cita: {service} — {slot} — {user.full_name}",
            )

    async def miscitas(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        rows = store.bookings_for(update.message.chat_id)
        if not rows:
            await update.message.reply_text("No tienes citas próximas. Usa /agendar 📅")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    f"❌ Cancelar: {service} {slot}", callback_data=f"cancel|{bid}"
                )
            ]
            for bid, service, slot in rows[:MAX_BUTTONS]
        ]
        await update.message.reply_text(
            "Tus citas (toca para cancelar):",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    async def cancel(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        booking_id = int(query.data.split("|", 1)[1])
        if store.cancel(booking_id, query.message.chat_id):
            await query.edit_message_text("Cita cancelada ✅")
        else:
            await query.edit_message_text("Esa cita ya no existe.")

    async def answer_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        question = update.message.text
        answer = best_answer(question, profile.faq) or ollama_answer(
            question, _faq_context(profile)
        )
        if answer:
            await update.message.reply_text(answer)
            return
        await update.message.reply_text(
            "Buena pregunta 🤔 Se la paso a una persona del equipo y te "
            "responden por aquí. Mientras, puedes agendar con /agendar."
        )
        if profile.owner_chat_id:
            user = update.message.from_user
            await context.bot.send_message(
                profile.owner_chat_id,
                f"❓ Pregunta sin responder de {user.full_name} "
                f"(chat {update.message.chat_id}):\n{question}",
            )

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("agendar", agendar))
    app.add_handler(CommandHandler("miscitas", miscitas))
    app.add_handler(CallbackQueryHandler(pick_service, pattern=r"^svc\|"))
    app.add_handler(CallbackQueryHandler(pick_slot, pattern=r"^slot\|"))
    app.add_handler(CallbackQueryHandler(cancel, pattern=r"^cancel\|"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_text))
    return app

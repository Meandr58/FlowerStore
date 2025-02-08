from telegram import Update, Message, Chat, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext
from unittest import mock
import unittest
from telegram_bot.bot_handlers import start, help_command

class BotTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.update = mock.Mock(spec=Update)
        self.update.message = mock.Mock(spec=Message)
        self.update.message.chat = mock.Mock(spec=Chat)
        self.update.message.chat_id = 123456789

        self.context = mock.Mock(spec=CallbackContext)
        self.context.bot = mock.Mock()

    async def test_start_command(self):
        print("Running test_start_command")

        expected_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Повторить заказ"), KeyboardButton(text="Оставить отзыв")],
                [KeyboardButton(text="Статус заказа"), KeyboardButton(text="Аналитика")]
            ],
            resize_keyboard=True
        )

        await start(self.update, self.context)

        self.update.message.reply_text.assert_called_once_with(
            "Привет! Выберите действие:",
            reply_markup=expected_keyboard
        )

    async def test_help_command(self):
        print("Running test_help_command")

        await help_command(self.update, self.context)

        self.update.message.reply_text.assert_called_once_with(
            "Список команд:\n/start – начать\n/help – справка"
        )

if __name__ == "__main__":
    unittest.main()
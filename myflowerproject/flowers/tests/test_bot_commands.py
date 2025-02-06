from telegram import Update, Message, Chat
from telegram.ext import CallbackContext
from unittest import mock
import unittest
from telegram_bot.bot_handlers import start, help_command


class BotTestCase(unittest.TestCase):
    def setUp(self):
        # Создаем мок-объект для Update
        self.update = mock.Mock(spec=Update)
        self.update.message = mock.Mock(spec=Message)
        self.update.message.chat = mock.Mock(spec=Chat)
        self.update.message.chat_id = 123456789  # Пример chat_id

        # Создаем мок-объект для CallbackContext
        self.context = mock.Mock(spec=CallbackContext)
        self.context.bot = mock.Mock()

    @mock.patch("telegram.Bot.send_message")
    def test_start_command(self, mock_send_message):
        # Вызываем команду /start
        start(self.update, self.context)

        # Проверяем, что бот отправил сообщение
        mock_send_message.assert_called_with(
            chat_id=self.update.message.chat_id,
            text="Привет! Я бот."
        )

    @mock.patch("telegram.Bot.send_message")
    def test_help_command(self, mock_send_message):
        # Вызываем команду /help
        help_command(self.update, self.context)  # Исправлено: передаем update и context

        # Проверяем, что бот отправил сообщение
        mock_send_message.assert_called_with(
            chat_id=self.update.message.chat_id,
            text="Помощь: /start /help"
        )
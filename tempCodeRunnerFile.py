import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandHelp
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import openai

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
openai.api_key = getenv("OPENAI_API_KEY")

class Reference:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        return self.messages
            
reference = Reference()
MODEL_NAME = "gpt-3.5-turbo"


# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())

async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

@dp.message(CommandHelp())

async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer("MOFO help message ")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    """ try:
        # Send a copy of the received message
        print(message.text)
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!") """ 
    print(f"USER: \n{message.text}")
    reference.add_message("user", message.text)
    messages_for_gpt = reference.get_messages()
    response=openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
             {"role":"assistant","content":messages_for_gpt},
             {"role":"user","content":message.text}
        ]
    )
    reply=response['choices'][0]['message']['content']
    reference.add_message("assistant", reply)
    #print(f"chatGPT:\n{reference.response}")

    print(reference)
    await message.answer(text=f'{reply}')


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
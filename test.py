import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandHelp, CommandFinalise
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import openai

TOKEN = getenv("BOT_TOKEN")
openai.api_key = getenv("OPENAI_API_KEY")
global timetable
class Reference:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        return self.messages
    
    def clear_messages(self):
        self.messages = []
    
reference = Reference()
MODEL_NAME = "gpt-4-turbo-preview"


# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())

async def command_start_handler(message: Message) -> None:
    #add google sign in logic here @ matthew
    reference.clear_messages()
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}! \nI am your personal assistant.\nI can help you with your daily schedule.\nJust type in your activities.\nEither in \n{hbold('Fixed format')}:\nI have a dinner at 7pm\nOr {hbold('Duration format')}:\nI have a 2 hours dinner\nYou can keep chatting with me to update and tweak the schedule.\nType /finalise to finalise your schedule and update your google calender. Type /help for help")


@dp.message(CommandFinalise())

async def command_finalise_handler(message: Message) -> None:
    #matthew your part!!!!!!!!!!!!!!
    #be it a api call or direct code
    #pass it to the logic to push json file into into calender
    reference.clear_messages()
    await message.answer(text=f'{timetable}')

@dp.message(CommandHelp())

async def command_help_handler(message: Message) -> None:
    #matthew your part!!!!!!!!!!!!!!
    #be it a api call or direct code
    #pass it to the logic to push json file into into calender
    await message.answer(text='"/start" - Start the bot\n"/finalise" - Finalise the timetable and send it to your google calender, this will also clear conversation context')

@dp.message()
async def ai(message: types.Message) -> None:
    global timetable

    print(f"USER: \n{message.text}")
    reference.add_message("user", message.text)
    messages_for_gpt = reference.get_messages()
    messages = []
    for msg in messages_for_gpt:
        messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the current user message
    usermessage = message.text + "When adding or editing actitvites, remember user inputed timings for previous activities and do not change them unless told by the user.Remember to add essentials like breakfast,lunch,dinner, wash-up and sleep timings, default 30 mins for travelling time for the activities stated. Sorted in time order. Print resulting schedule in JSON format, for example.{'schedule': [{'time': '9:00am', 'activity': 'Breakfast'},]}"

    messages.append({"role": "user", "content": usermessage})
    response = openai.ChatCompletion.create(
    model=MODEL_NAME,
    response_format={ "type": "json_object" },
    messages=messages
    )
    intermediatereply=response['choices'][0]['message']['content']
    reference.add_message("assistant", intermediatereply)

    usermessage = intermediatereply
    timetable=intermediatereply
    response = openai.ChatCompletion.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "You are a assistant that parse JSON timetable data and reply it in human readable format."},
        {"role": "user", "content": intermediatereply}
    ]
    )

    reply=response['choices'][0]['message']['content']

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
import asyncio
import logging
import sys
from os import getenv

import google.generativeai as genai
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from google.api_core import exceptions, retry
from yarl import URL

from src.scraper import Indexer, ScrapConfig, scrap

# --- CONFIG --- #

config = ScrapConfig(
    root=URL("https://eduwiki.innopolis.university/index.php/Main_Page"),
    host="eduwiki.innopolis.university",
)

# --- DOTENV --- #

load_dotenv()

TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
TELEGRAM_ADMIN = getenv("TELEGRAM_ADMIN")
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set")
if not TELEGRAM_ADMIN:
    raise ValueError("TELEGRAM_ADMIN is not set")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set")

# --- GEMINI --- #

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


@retry.Retry(predicate=retry.if_exception_type(exceptions.ResourceExhausted))
def generate_answer(query: str, indexer: Indexer) -> str:
    pages = indexer.search(query, 5)

    if not pages:
        return "I'm sorry, I couldn't find any relevant information."

    prompt = """You are an Eduwiki intellectual assistant at Innopolis University. Your task is to analyze user queries based on the context provided. The context includes fragments of pages and their sources (URLs). You have to:

1.	Read the highlighted context between CONTEXT START and CONTEXT END.
2.	Find relevant information to answer the user's query using only the pages provided.
3.	Provide a concise and clear answer to the query.
4.	If no relevant information is found in the context, respond: “I'm sorry, I couldn't find any relevant information.”
5.	Cite sources using the format "Source(s): "

CONTEXT START"""

    for page in pages:
        prompt += f"\n\nSource: {page[0]}\n\n{page[1]}"

    prompt += f"\n\nCONTEXT END\n\nQuestion: {query}"

    response = gemini_model.generate_content(prompt)

    return response.text


# --- TELEGRAM BOT --- #

dp = Dispatcher()


@dp.message(CommandStart())
async def _(message: Message) -> None:
    await message.answer("""Hello, I am your intellectual Eduwiki assistant from Innopolis University. I will help you find answers to your questions using information from the University's knowledge base.

Just ask a question and I will try to give you an accurate and clear answer with references to relevant sources. If the information you need is not available, I will tell you honestly.

How can I help you? 😊""")


@dp.message()
async def _(message: Message, indexer: Indexer) -> None:
    if message.text:
        answer = generate_answer(message.text, indexer)
        await message.answer(answer, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Ask me something")


# --- LAUNCH --- #


class IndexerMiddleware(BaseMiddleware):
    def __init__(self, indexer):
        self.indexer = indexer

    async def __call__(self, handler, event, data):
        data["indexer"] = self.indexer
        return await handler(event, data)


async def setup(bot: Bot, admin: str) -> None:
    indexer = await scrap(config)

    dp.message.middleware(IndexerMiddleware(indexer))

    await bot.send_message(
        chat_id=admin,
        text="Knowledge base has been indexed and the bot is ready to answer your questions.",
    )


async def main(token: str, admin: str) -> None:
    bot = Bot(token)

    await setup(bot, admin)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, stream=sys.stdout)
    asyncio.run(main(TELEGRAM_TOKEN, TELEGRAM_ADMIN))

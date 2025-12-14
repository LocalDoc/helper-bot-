import asyncio
from app import core, handlers

async def main():
    print("Бот запускается...")
    await core.dp.start_polling(core.bot)

if __name__ == "__main__":
    asyncio.run(main())
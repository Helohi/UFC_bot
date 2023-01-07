from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler

from distributor import answer
from buttons import button_answer


if __name__ == "__main__":
    TOKEN = "001.2084803440.4154868764:1008049923"
    bot = Bot(token=TOKEN)

    bot.dispatcher.add_handler(MessageHandler(callback=answer))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_answer   ))
    bot.start_polling()

    print("Start idle")
    bot.idle()

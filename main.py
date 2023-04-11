# This code is realy related to site ufcstats.com, and just parse data from it, every change in site might raise an
# error or missunderstand in code. Every change in site should also be changed here
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler

from distributor import answer
from buttons import button_answer
from functions import log


if __name__ == "__main__":
    # Creating bot
    TOKEN = "001.3884702224.2511578187:1008622729"
    bot = Bot(token=TOKEN)

    # Adding handlers
    bot.dispatcher.add_handler(MessageHandler(callback=answer))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_answer))
    bot.start_polling()

    # Start to work
    log("Start idle")
    bot.idle()

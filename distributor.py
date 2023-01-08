from bot.bot import Bot
from bot.event import Event
from functions import print_bot, past_matches, future_matches, print_bot_button, log, into_thread


def answer(bot: Bot, event: Event):
    # if event.from_chat != "705079793":  # Security
    #     print_bot("Бот не готов! Пожалуйста, попробуйте  позже!", bot, event.from_chat)

    # Info about user using bot
    log(f"Got message: id={event.from_chat}, "
        f"name={event.data['from']['name'] if 'name' in event.data['from'] else None}, "
        f"nick={event.data['from']['nick'] if 'nick' in event.data['from'] else None}")

    if (is_past := "/past_table" in event.text) or "/future_table" in event.text:
        return tables(bot, event, is_past)
    else:
        print_bot(f"Я не понял ваш: {event.text}.\nДа поможет вам /help", bot, event.from_chat)


@into_thread
def tables(bot: Bot, event: Event, is_past: bool):
    table = past_matches() if is_past else future_matches()
    for num, match in enumerate(table):
        if num > 5:  # Not spamming
            break
        match = match.split(';')
        text = f"<b>Бой</b>: <i>{match[0]}</i>" + f"\n<b>Дата</b>: <i>{match[1]}</i>"
        # Buttons
        buttons = {"info": f"info:{match[2]}"}
        if ":" not in match[0]:
            continue
        # Sending
        print_bot_button(text=text, user_id=event.from_chat, bot=bot, buttons=buttons, in_row=1)
    return


if __name__ == "__main__":
    pass
# Event(type='EventType.NEW_MESSAGE', data='{'chat': {'chatId': '705079793', 'type': 'private'}, 'from': {'firstName':
# 'Helo_hi', 'nick': 'tm_team.', 'userId': '705079793'}, 'msgId': '7184755677980524644', 'text': 'hello', 'timestamp':
# 1672831289}')

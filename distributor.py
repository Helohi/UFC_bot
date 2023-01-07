from bot.bot import Bot
from bot.event import Event
from functions import print_bot, past_matches, future_matches, print_bot_button, log


def answer(bot: Bot, event: Event):
    # if event.from_chat != "705079793":  # Security
    #     print_bot("Bot not ready! Please come later!", bot, event.from_chat)
    #
    log(f"Got message: id={event.from_chat}, "
        f"name={event.data['from']['name'] if 'name' in event.data['from'] else None}, "
        f"nick={event.data['from']['nick'] if 'nick' in event.data['from'] else None}")
    if (is_past := "/past_table" in event.text) or "/future_table" in event.text:
        table = past_matches() if is_past else future_matches()
        for num, match in enumerate(table):
            if num > 5:  # Not spamming
                break
            match = match.split(';')
            text = f"<b>Match</b>: <i>{match[0]}</i>" + f"\n<b>Date</b>: <i>{match[1]}</i>"
            # Buttons
            buttons = {"info": f"info:{match[2]}"}
            if ":" in match[0]:
                buttons[match[0].split()[-1]] = "fighter:"+match[0].split()[-1]
                buttons[match[0].split()[-3]] = "fighter:"+match[0].split()[-3]
            # Sending
            print_bot_button(text=text, user_id=event.from_chat, bot=bot, buttons=buttons, in_row=1)
    else:
        print_bot(f"I do not understand {event.text}", bot, event.from_chat)


if __name__ == "__main__":
    pass
# Event(type='EventType.NEW_MESSAGE', data='{'chat': {'chatId': '705079793', 'type': 'private'}, 'from': {'firstName':
# 'Helo_hi', 'nick': 'tm_team.', 'userId': '705079793'}, 'msgId': '7184755677980524644', 'text': 'hello', 'timestamp':
# 1672831289}')

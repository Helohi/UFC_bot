from bot.bot import Bot
from bot.event import Event
from functions import (print_bot, past_matches, future_matches, print_bot_button, log, into_thread, parse_st_info,
                       get_html, parse_sf_info)


def answer(bot: Bot, event: Event):
    """ Main function for answering to some questions """
    # Info about user using bot
    log(f"Got message: id={event.from_chat}, "
        f"name={event.data['from']['name'] if 'name' in event.data['from'] else None}, "
        f"nick={event.data['from']['nick'] if 'nick' in event.data['from'] else None}, "
        f"text={event.text}")

    if (is_past := "/past_table" in event.text) or "/future_table" in event.text:  # tables
        return tables(bot, event, is_past)

    elif "/st" in event.text:  # search for tournment
        return st(bot, event)

    elif "/sf" in event.text:  # search for fighter
        return sf(bot, event)

    else:  # misunderstand
        print_bot(f"Я не понял ваш: {event.text}.\nДа поможет вам /help", bot, event.from_chat)


@into_thread
def tables(bot: Bot, event: Event, is_past: bool):
    """ Showing past and future tables """
    table = past_matches() if is_past else future_matches()
    for num, match in enumerate(table):
        if num > 5:  # Not spamming
            break
        match = match.split(';')
        text = f"<b>Турнир</b>: <i>{match[0]}</i>" + f"\n<b>Дата</b>: <i>{match[1]}</i>"
        # Buttons
        buttons = {"info": f"info:{match[2]}"}
        if ":" not in match[0]:
            continue
        # Sending
        print_bot_button(text=text, user_id=event.from_chat, bot=bot, buttons=buttons, in_row=1)
    return


@into_thread
def st(bot: Bot, event: Event):
    """ Searhing tournaments """
    query = event.text.replace("/st", '').strip()
    if not query:
        print_bot("Вы должны написать название тура! ( /st *название* )", bot, event.from_chat)
        return None
    text, buttons = parse_st_info(get_html(f"http://www.ufcstats.com/statistics/events/search?query="
                                           f"{'+'.join(query.split())}&page=all"),
                                  f"http://www.ufcstats.com/statistics/events/search?query="
                                  f"{'+'.join(query.split())}&page=all")
    return print_bot_button(bot, event.from_chat, text, in_row=3, buttons=buttons)


@into_thread
def sf(bot: Bot, event: Event):
    """ Searching for fighters """
    query = event.text.lstrip("/sf").strip()
    if not query:
        print_bot("Вы должны написать имя/фамилию бойца! ( /st *название* )", bot, event.from_chat)
        return
    text, buttons = parse_sf_info(get_html(f"http://ufcstats.com/statistics/fighters/search?query="
                                           f"{'+'.join(query.split())}"),
                                  f"http://ufcstats.com/statistics/fighters/search?query="
                                  f"{'+'.join(query.split())}")
    return print_bot_button(bot, event.from_chat, text, in_row=3, buttons=buttons)

# Event(type='EventType.NEW_MESSAGE', data='{'chat': {'chatId': '705079793', 'type': 'private'}, 'from': {'firstName':
# 'Helo_hi', 'nick': 'tm_team.', 'userId': '705079793'}, 'msgId': '7184755677980524644', 'text': 'hello', 'timestamp':
# 1672831289}')

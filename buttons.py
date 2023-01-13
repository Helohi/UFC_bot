from bot.bot import Bot
from bot.event import Event
from functions import (parse_info_matches, print_bot, log, into_thread, print_bot_button, parse_fighter_info, get_html,
                       parse_se_info, parse_event_detail)
from To_do_class import ToDo

to_do = ToDo()


def button_answer(bot: Bot, event: Event):
    bot.answer_callback_query(event.data['queryId'], text='Got it')

    log(f"Button was pressed by: id={event.from_chat}, "
        f"name={event.data['from']['firstName'] if 'firstName' in event.data['from'] else None}, "
        f"nick={event.data['from']['nick'] if 'nick' in event.data['from'] else None}, "
        f"callback_data={event.callback_query.split(':')[0]}")

    if "dinfo:" in event.callback_query:  # detailed info from parse_event
        to_do.append(dinfo=(bot, event,))
        return

    elif "info:" in event.callback_query:  # info -> listing matches in event
        to_do.append(info=(bot, event,))
        return

    elif "more:" in event.callback_query:  # more in search
        to_do.append(more=(bot, event,))
        return

    elif "fighter:" in event.callback_query:  # info about fighter
        to_do.append(fighter=(bot, event,))
        return

    else:  # If some info that do not need to be preapred
        print_bot(event.callback_query, bot, event.from_chat)
        return


@into_thread
def info(bot: Bot, event: Event):
    site_url = event.callback_query.lstrip("info:")
    text, buttons = parse_event_detail(get_html(site_url), site_url)
    return print_bot_button(bot, event.from_chat, text, buttons=buttons, in_row=5)


@into_thread
def dinfo(bot: Bot, event: Event):
    which, url = event.callback_query.lstrip("dinfo:").split(";;;")

    text, buttons = parse_info_matches(get_html(url), int(which))

    print_bot_button(text=text, bot=bot, user_id=event.from_chat, buttons=buttons, in_row=1)
    return


@into_thread
def fighter(bot: Bot, event: Event):
    fighter_url = event.callback_query.replace('fighter:', '').strip()

    # Prepairing text that have to be sent
    text = parse_fighter_info(get_html(fighter_url))

    return print_bot(text, bot, event.from_chat)


@into_thread
def more(bot: Bot, event: Event):
    start, html = event.callback_query.lstrip("more:").split(";;;")
    text, buttons = parse_se_info(html, int(start))
    return print_bot_button(bot, event.from_chat, text, in_row=3, buttons=buttons)


def doer_of_list(dict_of_events: ToDo):
    for func in dict_of_events.copy():
        eval(func)(*dict_of_events[func])
        del dict_of_events[func]


to_do.append_function(doer_of_list)
if __name__ == "__main__":
    pass
# Event(type='EventType.CALLBACK_QUERY', data='{'callbackData': 'info', 'from': {'firstName': 'Helo_hi',
# 'nick': 'tm_team.', 'userId': '705079793'}, 'message': {'chat': {'chatId': '705079793', 'type': 'private'},
# 'from': {'firstName': 'ultramma_bot', 'nick': 'ultramma_bot', 'userId': '1008049923'}, 'msgId':
# '7184754642893406968', 'parts': [{'payload': [[{'callbackData': 'info', 'text': 'info'}]],
# 'type': 'inlineKeyboardMarkup'}], 'text': 'UFC Fight Night: Imavov vs. Gastelum\nWill be: January 14, 2023',
# 'timestamp': 1672831048}, 'queryId': 'SVR:705079793:1008049923:1672831050939294:43938-1672831051'}')

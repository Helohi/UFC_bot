from bot.bot import Bot
from bot.event import Event
from functions import (parse_info_matches, print_bot, log, into_thread, print_bot_button, parse_fighter_info, get_html,
                       parse_st_info, parse_event_detail, parse_sf_info, parse_all_fights, news_info_parser,
                       news_parser)
from To_do_class import ToDo

to_do = ToDo()


def button_answer(bot: Bot, event: Event):
    """ Main function for answering to sth that was writen """
    bot.answer_callback_query(event.data['queryId'], text='Got it')

    log(f"Button was pressed by: id={event.from_chat}, "
        f"name={event.data['from']['firstName'] if 'firstName' in event.data['from'] else None}, "
        f"nick={event.data['from']['nick'] if 'nick' in event.data['from'] else None}, "
        f"callback_data={event.callback_query.split(' ')[0]}")

    if "news_more" in event.callback_query:
        to_do.append(news_more=(bot, event,))
        return

    elif "news_info:" in event.callback_query:
        to_do.append(news_info=(bot, event,))
        return

    elif "dinfo:" in event.callback_query:  # detailed info from parse_event
        to_do.append(dinfo=(bot, event,))
        return

    elif "info:" in event.callback_query:  # info -> listing matches in event
        to_do.append(info=(bot, event,))
        return

    elif "moret:" in event.callback_query:  # more in search
        to_do.append(moret=(bot, event,))
        return

    elif "moref:" in event.callback_query:
        to_do.append(moref=(bot, event,))
        return

    elif "fighter:" in event.callback_query:  # info about fighter
        to_do.append(fighter=(bot, event,))
        return

    elif "ffights:" in event.callback_query:
        to_do.append(ffights=(bot, event,))
        return

    else:  # If some info that do not need to be preapred
        print_bot(event.callback_query, bot, event.from_chat)
        return


@into_thread
def info(bot: Bot, event: Event):
    """ Showing fights in event """
    site_url = event.callback_query.lstrip("info:")
    text, buttons = parse_event_detail(get_html(site_url), site_url)
    return print_bot_button(bot, event.from_chat, text, buttons=buttons, in_row=5, last_ones=3,
                            url=[False for _ in range(len(buttons) - 2)] + [True, True])


@into_thread
def dinfo(bot: Bot, event: Event):
    """ Showing fight's details """
    which, *is_event, url = event.callback_query.lstrip("dinfo:").split(";;;")

    text, buttons, is_past = parse_info_matches(get_html(url), int(which), True if is_event else False)

    print_bot_button(text=text, bot=bot, user_id=event.from_chat, buttons=buttons, in_row=2,
                     url=False if is_past else [False, False, True, True])
    return


@into_thread
def fighter(bot: Bot, event: Event):
    """ Showing properties of fighter """
    fighter_url = event.callback_query.replace('fighter:', '').strip()

    # Prepairing text that have to be sent
    text, buttons = parse_fighter_info(get_html(fighter_url), fighter_url)

    return print_bot_button(bot, event.from_chat, text, in_row=1, buttons=buttons)


@into_thread
def ffights(bot: Bot, event: Event):
    url = event.callback_query.replace("ffights:", "").strip()

    text, buttons = parse_all_fights(get_html(url), url)
    return print_bot_button(bot, event.from_chat, text, in_row=3, buttons=buttons)


@into_thread
def moret(bot: Bot, event: Event):
    """ Showing more tours in search """
    start, url = event.callback_query.lstrip("moret:").split(";;;")
    text, buttons = parse_st_info(get_html(url), url, int(start))
    return print_bot_button(bot, event.from_chat, text, in_row=3, buttons=buttons)


@into_thread
def moref(bot: Bot, event: Event):
    """ Showing more fighters in search """
    start, url = event.callback_query.lstrip('moref:').split(";;;")
    text, buttons = parse_sf_info(get_html(url), url, int(start))
    return print_bot_button(bot, event.from_chat, text, in_row=3, buttons=buttons)


@into_thread
def news_info(bot: Bot, event: Event):
    """ Parse each news in list and that was pressed """
    link = event.callback_query.replace("news_info:", '').strip()
    text = news_info_parser(get_html("https://www.championat.com/" + link))
    return print_bot(text, bot, event.from_chat)


@into_thread
def news_more(bot: Bot, event: Event):
    """ More news button answer """
    starter = event.callback_query.replace("news_more:", '')
    text, buttons = news_parser(get_html("https://www.championat.com/boxing/_ufc.html"), int(starter))
    return print_bot_button(bot, event.from_chat, text, in_row=5, buttons=buttons)


def doer_of_list(dict_of_events: ToDo):
    """ Distribute work between functions """
    for func in dict_of_events.copy():
        eval(func)(*dict_of_events[func])
        del dict_of_events[func]


to_do.append_function(doer_of_list)
# Event(type='EventType.CALLBACK_QUERY', data='{'callbackData': 'info', 'from': {'firstName': 'Helo_hi',
# 'nick': 'tm_team.', 'userId': '705079793'}, 'message': {'chat': {'chatId': '705079793', 'type': 'private'},
# 'from': {'firstName': 'ultramma_bot', 'nick': 'ultramma_bot', 'userId': '1008049923'}, 'msgId':
# '7184754642893406968', 'parts': [{'payload': [[{'callbackData': 'info', 'text': 'info'}]],
# 'type': 'inlineKeyboardMarkup'}], 'text': 'UFC Fight Night: Imavov vs. Gastelum\nWill be: January 14, 2023',
# 'timestamp': 1672831048}, 'queryId': 'SVR:705079793:1008049923:1672831050939294:43938-1672831051'}')

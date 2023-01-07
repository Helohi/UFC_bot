from bot.bot import Bot
from bot.event import Event
from requests import get
from functions import parse_info_matches, print_bot, log, into_thread
from To_do_class import ToDo

to_do = ToDo()


def button_answer(bot: Bot, event: Event):
    bot.answer_callback_query(event.data['queryId'], text='Got it')

    log("Button pressed")
    event.text = event.callback_query  # For easy usage
    if "info:" in event.text:
        return to_do.append(info=(bot, event,))


@into_thread
def info(bot, event):
    event.text = event.text.lstrip("info:")
    ans = get(event.text)  # Getting html of info site
    if str(ans.status_code) != "200":  # Checking status code
        raise ConnectionError(f"We get {ans.status_code}, but expected 200")
    text = parse_info_matches(ans.text)
    print_bot(text, bot, event.from_chat)
    return


def doer_of_list(dict_of_events: ToDo):
    for func in dict_of_events:
        eval(func)(*dict_of_events[func])


to_do.append_function(doer_of_list)
if __name__ == "__main__":
    pass
# Event(type='EventType.CALLBACK_QUERY', data='{'callbackData': 'info', 'from': {'firstName': 'Helo_hi',
# 'nick': 'tm_team.', 'userId': '705079793'}, 'message': {'chat': {'chatId': '705079793', 'type': 'private'},
# 'from': {'firstName': 'ultramma_bot', 'nick': 'ultramma_bot', 'userId': '1008049923'}, 'msgId':
# '7184754642893406968', 'parts': [{'payload': [[{'callbackData': 'info', 'text': 'info'}]],
# 'type': 'inlineKeyboardMarkup'}], 'text': 'UFC Fight Night: Imavov vs. Gastelum\nWill be: January 14, 2023',
# 'timestamp': 1672831048}, 'queryId': 'SVR:705079793:1008049923:1672831050939294:43938-1672831051'}')

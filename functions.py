from bot.bot import Bot
import json
import logging
import requests
from bs4 import BeautifulSoup
from threading import Thread
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - " %(message)s "', datefmt='%H:%M:%S')


def into_thread(func):
    """ Running function in thread """
    def run(*args, **kwargs):
        proc = Thread(target=func, args=args if args else tuple(), kwargs=kwargs if kwargs else dict())
        proc.start()
        return

    return run


@into_thread
def print_bot(text: str, bot: Bot, user_id: str) -> None:
    """ Easier way to write sth to user """
    while True:
        try:
            sent_text_params = bot.send_text(
                chat_id=user_id, text=text, parse_mode='HTML')
        except Exception:
            continue
        else:
            return sent_text_params
    return


@into_thread
def print_bot_button(bot, user_id: str = '705079793', text: str = 'Buttons:', url=False,
                     buttons: dict = None, in_row: int = 8, last_ones: int = None, is_admin: bool = False, **kwargs):
    """ Print message to bot with buttons """
    if not buttons:
        buttons = kwargs
    keyboard = [[]]
    if isinstance(url, bool):
        action_type = "url" if url else "callbackData"

        for btn_text in buttons.copy():
            if len(buttons) == last_ones:
                break
            if len(keyboard[-1]) >= in_row:
                keyboard.append([])
            if is_admin and not url:  # Admin addition
                buttons[btn_text] += ' -admin-'
                print(buttons[btn_text])

            keyboard[-1].append({"text": btn_text,
                                 action_type: buttons[btn_text]})
            del buttons[btn_text]

        if last_ones:
            for btn_text in buttons:
                keyboard.append([{"text": btn_text, action_type: buttons[btn_text]}])

    elif hasattr(url, '__iter__'):
        if len(url) == len(buttons):
            for btn_text, is_url in zip(buttons.copy(), url.copy()):
                if len(buttons) == last_ones:
                    break
                if len(keyboard[-1]) >= in_row:
                    keyboard.append([])
                if not is_url and is_admin:  # Admin addition
                    buttons[btn_text] = buttons[btn_text] + "-admin-"

                action_type = 'url' if is_url else "callbackData"
                keyboard[-1].append({"text": btn_text,
                                     action_type: buttons[btn_text]})
                del buttons[btn_text]
                url.pop(0)

            if last_ones:
                for btn_text, is_url in zip(buttons, url):
                    keyboard.append([{"text": btn_text, 'url' if is_url else "callbackData": buttons[btn_text]}])
        else:
            raise IndexError(
                'buttons and url have different sizes, plz check them!')
    else:
        print_bot(text, bot, user_id)
        return False

    while True:
        try:
            bot.send_text(chat_id=user_id, text=text, parse_mode='HTML',
                          inline_keyboard_markup="{}".format(json.dumps(keyboard)))
        except BaseException:
            continue
        else:
            break
    return True


def log(*message, show: bool = True):
    if show:
        logging.warning(' '.join(map(str, message)))


def past_matches():
    """ Return a lot of past matches in list
     Pattern of one element: match_name;match_date;link_to_match; """
    # Sending without first match becouse it is usually future match
    return parsing_table_of_matches(get_html("http://ufcstats.com/statistics/events/completed"))[1:]


def future_matches():
    """ Return a lot of past matches in list
     Pattern of one element: match_name;match_date;link_to_match; """
    # Sending table
    return parsing_table_of_matches(get_html("http://ufcstats.com/statistics/events/upcoming"))


def parsing_table_of_matches(html, lst_of_matches: list = None):
    """ Parse a table from ufcstats.com """
    # Checking variables
    if lst_of_matches is None:
        lst_of_matches = []

    soup = BeautifulSoup(html, 'lxml')
    matches = soup.find_all('i', {"class": "b-statistics__table-content"})
    # Preparing to send
    for match in matches:
        one_match = match.text.split()
        lst_of_matches.append(" ".join(one_match[:-3]) + ";" + " ".join(one_match[-3:]) + ';' + match.a['href'] + ';')
    return lst_of_matches


def parse_event_detail(html: str, url: str):
    """ Parse event in site and showing the fights in event """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("tbody", class_="b-fight-details__table-body")
    text_icq, buttons = "В иветне:\n", dict()
    # Get name values from table
    for num, el in enumerate(table.find_all("tr")):
        num += 1
        fighters = el.find_all("td")[1].text.split()
        text_icq += f"{num}. {' '.join(fighters[:2])} vs. {(' '.join(fighters[2:]))}\n\n"
        buttons[f"{num}"] = f"dinfo:{num - 1};;;{url}"

    date = datetime.strptime(soup.find('li', class_='b-list__box-list-item').text.replace("Date:", "").strip(),
                             '%B %d, %Y')
    if date < datetime.now():
        buttons['Смотреть бои'] = f"video:{date.strftime('%d.%m.%Y')}"
    else:
        buttons['Где смотреть?'] = f"Бой можно посмотреть по <b>Матч Тв</b> и <b>Матч Боец!</b>"
    to_bet_buttons(buttons)
    return text_icq, buttons


def parse_info_matches(html: str, which: int = 0, is_event: bool = False):
    """ Parse information table from ufcstats.com """

    soup = BeautifulSoup(html, "lxml")
    info = soup.find_all("tr", {
        "class": "b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click"})[which]
    fighters = info.find('td', {"class": "b-fight-details__table-col l-page_align_left"})
    prop = info.find_all('td', {"class": "b-fight-details__table-col"})[2:]
    prop = [el.text.split() for el in prop]

    # Buttons for users
    buttons = {'_'.join(fighters.text.split()[:2]).strip(): "fighter:" + fighters.find_all("a")[0]['href'],
               '_'.join(fighters.text.split()[2:]).strip(): "fighter:" + fighters.find_all("a")[1]['href']}

    if info.td.p:  # Past
        is_past = True
        # First fighter
        if info.td.p.text.strip() == 'win':  # Has winner
            text_icq, win = "<b>Победил</b>: ", True
        elif info.td.p.text.strip() == 'loss':  # Lost in fight (addition for parse_all_fights)
            text_icq, win = "<b>Проиграл</b>: ", False
        else:  # Draw
            text_icq, win = '<b>Ничья</b>: ', None

        text_icq += f"{'_'.join(fighters.text.split()[:2]).strip()}\nKD: {prop[0][0]}\nSTR: {prop[1][0]}\n" \
                    f"TD: {prop[2][0]}\nSUB: {prop[3][0]}\n\n"
        # Second fighter
        if win is None:  # no not as win can be false => it is lost
            text_icq += "<b>Ничья</b>: "
        else:
            text_icq += "<b>Проиграл</b>: " if win else "<b>Победил</b>: "

        text_icq += f"{'_'.join(fighters.text.split()[2:]).strip()}\nKD: {prop[0][1]}\nSTR: {prop[1][1]}\n" \
                    f"TD: {prop[2][1]}\nSUB: {prop[3][1]}\n\n"
        # Properties of Match:
        text_icq += f"<b>Характеристика матча</b>:\n{'Ивент' if is_event else 'Весовая категория'}: " \
                    f"{' '.join(prop[4])}\nМетод: {prop[5][0]}\nРаунд: {prop[6][0]}\nВремя: {prop[7][0]}"

    else:  # Future
        is_past = False
        text_icq = f"<b>Первый боец</b>: {'_'.join(fighters.text.split()[:2]).strip()}\n\n"  # First fighter
        text_icq += f"<b>Второй боец</b>: {'_'.join(fighters.text.split()[2:]).strip()}\n\n"  # Second fighter
        text_icq += f"<b>Весовая категория</b>: {' '.join(prop[4])}"  # Weight class
        to_bet_buttons(buttons)  # betting buttons

    if is_event:
        buttons['Ивент'] = f"info:{info.find_all('td')[6].p.a['href']}"
    return text_icq, buttons, is_past


def to_bet_buttons(buttons):
    # For making money by main admin
    buttons['Прогнозы'] = "https://icq.im/durdyevxt"
    buttons['Сделать ставку'] = "https://icq.im/durdyevxt"


def parse_fighter_info(html: str, url: str):
    """ Parse info about fighter from ufcstats.com """
    soup = BeautifulSoup(html, 'lxml')
    # Getting all needed inforamtion
    # Getting name
    name = soup.find("span", class_="b-content__title-highlight").text.strip()
    # Getting Nickname
    nick = soup.find("p", class_="b-content__Nickname").text.strip()
    # Getting Wins-Draws-Looses
    record = soup.find("span", class_="b-content__title-record").text.strip()
    record = record.replace("Record: ", "").split()[0].split('-')
    # Getting all other properties
    prop = soup.find("ul", {"class": "b-list__box-list"})
    prop = [el.strip() for el in prop.text.split("  ") if el.strip()]

    # Preparing text that have to be returned
    text_icq = f"<b>Полное имя</b>: {name}\n<b>Прозвище</b>: {nick if nick else 'Нет'}\n"
    text_icq += f"<b>Побед</b>: {record[0]}\n<b>Поражений</b>: {record[1]}\n<b>Ничей</b>: {record[2]}\n" \
                f"\n<b>Другие характеристики</b>:\n  <b>Высота</b>: {prop[1]}\n  <b>Веc</b>: {prop[3]}\n  " \
                f"<b>Охват</b>: {prop[5]}\n  <b>Позиция</b>: {prop[7]}\n  <b>Дата рождения</b>: {prop[-1]}"

    # Buttons for all fights
    buttons = {"Все матчи": f"ffights:{url}"}
    return text_icq, buttons


def parse_st_info(html: str, site: str, start: int = 1):
    """ Parsing the search for event """

    # Parsing with beautifulsoup
    soup = BeautifulSoup(html, "lxml")
    table_data = soup.find_all("td", class_="b-statistics__table-col")
    text_icq, buttons, num = "Результаты:\n", dict(), ((start - 1) // 2) + 1
    # Creaating text and buttons with design
    for el in table_data[(start - 1):(start + 16):2]:
        # print(el.text)
        if ':' not in el.text:
            continue
        text_icq += f"<b>{num}</b>: {' '.join(el.text.split()[:-3])}\n<i>Дата: {' '.join(el.text.split()[-3:])}</i>\n\n"
        buttons[str(num)] = f"info:{el.a['href']}"
        num += 1

    if len(table_data[start + 18::2]) > 0:  # Normal showing
        buttons[">>>"] = f"moret:{start + 18};;;{site}"

    if text_icq == "Результаты:\n":
        return "Ничего не найдено (больше)!", {"empty": "Не растраивайся, все еще впереди, возможно скоро мы это "
                                                        "найдем, ну  а пока, пойди, видео скачай какое-нибудь на "
                                                        "@DownloadTMbot что-ли"}
    else:
        return text_icq, buttons


def parse_sf_info(html: str, site: str, start: int = 1):
    """ Parse the search for fighters """

    soup = BeautifulSoup(html, 'lxml')
    table_data = soup.find_all("tr", class_="b-statistics__table-row")
    text_icq, buttons = "Результаты:\n", dict()
    for num, data in enumerate(table_data[start + 1:start + 11]):
        num += 1
        text_icq += f"{num}. {data.td.text.strip()} {data.find_all('td')[1].text.strip()}\n"
        buttons[str(num)] = f"fighter:{data.td.a['href']}"

    if len(table_data[start + 10:]) > 0:
        buttons['>>>'] = f"moref:{start + 10};;;{site}"

    if not buttons:
        return "Ничего не найдено (больше)!", {"Empty": "Не растраивайся, все еще впереди, возможно скоро мы это "
                                                        "найдем, ну  а пока, пойди, видео скачай какое-нибудь на "
                                                        "@DownloadTMbot что-ли"}
    else:
        return text_icq, buttons


def get_html(url: str):
    """ Showing the html by url """

    ans1 = requests.get(url)
    if str(ans1.status_code) != '200':
        raise Exception("Can't connect to site")
    return ans1.text


def parse_all_fights(html: str, url: str):
    soup = BeautifulSoup(html, 'lxml')
    table_data = soup.find_all("tr", class_="b-fight-details__table-row b-fight-details__table-row__hover "
                                            "js-fight-details-click")
    text_icq, buttons = "<b>Результаты</b>:\n", dict()
    for num, tr in enumerate(table_data):
        text_icq += f"{num + 1}."
        if tr.td.text.strip() == "win":
            text_icq += "<i>Победил</i>: "
        elif tr.td.text.strip() == "loss":
            text_icq += "<i>Проиграл</i>: "
        else:
            text_icq += "<i>Ничья</i>: "

        text_icq += f"{tr.find_all('td')[1].p.text.strip()} vs. {tr.find_all('td')[1].find_all('p')[1].text.strip()}\n"
        text_icq += f"<b><i>Дата</i></b>: {tr.find_all('td')[6].find_all('p')[1].text.strip()}\n\n"

        buttons[f"{num + 1}"] = f"dinfo:{num};;;1;;;{url}"

    if not buttons:
        return "Нмчего не найдено, печалька!", {"Empty": "Ты не видел моего брата в функции поиска по имени бойца?\n"
                                                         "Нет? Знаит он хорошо работает, а для поиска по бойцу введи:\n"
                                                         "/sf *фамлия_или_имя_бойца*"}
    return text_icq, buttons


def show_video_table(html: str, date: str, start: int = 0):
    # Beatifulsoup and parsing
    soup = BeautifulSoup(html, 'lxml')
    video_table = soup.find_all("a", class_="page-title")

    # Preparing variables
    text_icq, buttons = "Результаты:\n", dict()
    for post in video_table[start:start + 5]:
        if "Видео" in post.text:
            text_icq += f"<b>{start}</b>. {post.text}\n\n"
            buttons[f'{start}'] = f"video_info:{post['href']}"
            start += 1

    if buttons and len(video_table[start:]) > 0:
        buttons['>>>'] = f"video:{date};;;{start}"

    if not buttons:
        return "Нет результатов, но скоро будут! (возможно)", {"Empty": "Я 3 брат, остальных не думаю что ты "
                                                                        "встретишь\nЕсли из найдешь, скажи админу, "
                                                                        "хорошо? Но проверь что правельно все"
                                                                        "написал.\nА то мне сдесь очень скучно!🥲\n"
                                                                        "Пойду посмотрю видео на @DownloadTMbot"}
    return text_icq, buttons


if __name__ == "__main__":
    print(show_video_table("14.01.2023"))

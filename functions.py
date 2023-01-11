from bot.bot import Bot
import json
import logging
import requests
from bs4 import BeautifulSoup
from threading import Thread

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - " %(message)s "', datefmt='%H:%M:%S')


def into_thread(func):
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
                     buttons: dict = None, in_row: int = 8, is_admin: bool = False, **kwargs):
    """ Print message to bot with buttons """
    if not buttons:
        buttons = kwargs
    keyboard = [[]]
    if isinstance(url, bool):
        action_type = "url" if url else "callbackData"

        for btn_text in buttons:
            if len(keyboard[-1]) >= in_row:
                keyboard.append([])
            if is_admin and not url:  # Admin addition
                buttons[btn_text] += ' -admin-'
                print(buttons[btn_text])

            keyboard[-1].append({"text": btn_text,
                                 action_type: buttons[btn_text]})
    elif hasattr(url, '__iter__'):
        if len(url) == len(buttons):
            for btn_text, is_url in zip(buttons, url):
                if len(keyboard[-1]) >= in_row:
                    keyboard.append([])
                if not is_url and is_admin:  # Admin addition
                    buttons[btn_text] = buttons[btn_text] + "-admin-"

                action_type = 'url' if is_url else "callbackData"
                keyboard[-1].append({"text": btn_text,
                                     action_type: buttons[btn_text]})
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


def past_matches(lst_of_matches: list = None):
    """ Return a lot of past matches in list
     Pattern of one element: match_name;match_date;link_to_match; """

    # Checking variables
    if lst_of_matches is None:
        lst_of_matches = []

    # Sending wiithout first match becouse it is usually future match
    return parsing_table_of_matches(get_html("http://ufcstats.com/statistics/events/completed"), lst_of_matches)[1:]


def future_matches(lst_of_matches: list = None):
    """ Return a lot of past matches in list
     Pattern of one element: match_name;match_date;link_to_match; """
    # Checking vaiables
    if not lst_of_matches:
        lst_of_matches = []

    # Parsing
    return parsing_table_of_matches(get_html("http://ufcstats.com/statistics/events/upcoming"), lst_of_matches)


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


def parse_info_matches(html: str):
    """ Parse information table from ufcstats.com """

    soup = BeautifulSoup(html, "lxml")
    fst_info = soup.find("tr", {
        "class": "b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click"})
    fighters = fst_info.find('td', {"class": "b-fight-details__table-col l-page_align_left"})
    prop = fst_info.find_all('td', {"class": "b-fight-details__table-col"})[2:]
    prop = [el.text.split() for el in prop]

    if fst_info.td.p:  # Past
        if str(fst_info.td.p.text).strip() == 'win':  # Has winner
            winner = True
        else:  # Draw
            winner = False

        # First fighter
        text_icq = f"{'<b>Победил</b>' if winner else '<b>Ничья</b>'}: "
        text_icq += f"{'_'.join(fighters.text.split()[:2]).strip()}\nKD: {prop[0][0]}\nSTR: {prop[1][0]}\n" \
                    f"TD: {prop[2][0]}\nSUB: {prop[3][0]}\n\n"
        # Second fighter
        text_icq += f"{'<b>Проиграл</b>' if winner else '<b>Ничья</b>'}: "
        text_icq += f"{'_'.join(fighters.text.split()[2:]).strip()}\nKD: {prop[0][1]}\nSTR: {prop[1][1]}\n" \
                    f"TD: {prop[2][1]}\nSUB: {prop[3][1]}\n\n"
        # Properties of Match:
        text_icq += f"<b>Характеристика матча</b>:\nВесовая категория: {' '.join(prop[4])}\nМетод: {prop[5][0]}\n" \
                    f"Раунд: {prop[6][0]}\nВремя: {prop[7][0]}"

    else:  # Future
        text_icq = f"<b>Первый боец</b>: {'_'.join(fighters.text.split()[:2]).strip()}\n\n"  # First fighter
        text_icq += f"<b>Второй боец</b>: {'_'.join(fighters.text.split()[2:]).strip()}\n\n"  # Second fighter
        text_icq += f"<b>Весовая категория</b>: {' '.join(prop[4])}"  # Weight class

    # Buttons for users
    buttons = {'_'.join(fighters.text.split()[:2]).strip(): "fighter:" + fighters.find_all("a")[0]['href'],
               '_'.join(fighters.text.split()[2:]).strip(): "fighter:" + fighters.find_all("a")[1]['href']}
    return text_icq, buttons


def parse_fighter_info(html: str):
    """ Parse info about fighter from ufcstats.com """
    soup = BeautifulSoup(html, 'lxml')
    # Getting all needed inforamtion
    # Getting name
    name = soup.find("span", class_="b-content__title-highlight").text.strip()
    # Getting Nickname
    nick = soup.find("p", class_="b-content__Nickname").text.strip()
    # Getting Wins-Draws-Looses
    record = soup.find("span", class_="b-content__title-record").text.strip()
    record = record.replace("Record: ", "").split('-')
    # Getting all other properties
    prop = soup.find("ul", {"class": "b-list__box-list"})
    prop = [el.strip() for el in prop.text.split("  ") if el.strip()]

    # Preparing text that have to be returned
    text_icq = f"<b>Полное имя</b>: {name}\n<b>Прозвище</b>: {nick if nick else 'Нет'}\n"
    text_icq += f"<b>Побед</b>: {record[0]}\n<b>Поражений</b>: {record[1]}\n<b>Ничей</b>: {record[2]}\n" \
                f"\n<b>Другие характеристики</b>:\n  <b>Высота</b>: {prop[1]}\n  <b>Веc</b>: {prop[3]}\n  " \
                f"<b>Охват</b>: {prop[5]}\n  <b>Позиция</b>: {prop[7]}\n  <b>Дата рождения</b>: {prop[-1]}"

    return text_icq


def parse_se_info(html: str, start: int = 1):
    # Parsing with beautifulsoup
    soup = BeautifulSoup(html, "lxml")
    table_data = soup.find_all("td", class_="b-statistics__table-col")
    text_icq, buttons, num = "Результаты:\n", dict(), ((start-1)//2)+1
    # Creaating text and buttons with design
    for el in table_data[(start - 1):(start + 16):2]:
        # print(el.text)
        if ':' not in el.text:
            continue
        text_icq += f"<b>{num}</b>: {' '.join(el.text.split()[:-3])}\n<i>Дата: {' '.join(el.text.split()[-3:])}</i>\n\n"
        buttons[str(num)] = f"info:{el.a['href']}"
        num += 1

    if len(table_data[(start - 1):(start + 16):2]) < len(table_data[::2]):  # Normal showing
        buttons[">>>"] = f"more:{start + 18};;;{html}"

    if text_icq == "Результаты:\n":
        return "Ничего не найдено (больше)!", {"empty": "Да, не растраивайся, все еще впереди, возможно скоро мы это "
                                                        "найдем, ну  а пока, пойди, видео скачай какое-нибудь на "
                                                        "@DownloadTMbot что-ли"}
    else:
        return text_icq, buttons


def parse_tournament(html: str):
    pass


def get_html(url):
    ans1 = requests.get(url)
    if str(ans1.status_code) != '200':
        raise Exception("Can't connect to site")
    return ans1.text


if __name__ == "__main__":
    print(parse_se_info(get_html("http://www.ufcstats.com/statistics/events/search?query=UFC"), 19))

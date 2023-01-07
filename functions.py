from bot.bot import Bot
import json
import logging
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - " %(message)s "', datefmt='%H:%M:%S')


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

    # Getting html of site ufcstats.com
    ans = requests.get("http://ufcstats.com/statistics/events/completed")
    if str(ans.status_code) != "200":  # Checking for correctness
        raise Exception("Can't connect to site")

    # Parsing
    return parsing_table_of_matches(ans, lst_of_matches)


def future_matches(lst_of_matches: list = None):
    """ Return a lot of past matches in list
     Pattern of one element: match_name;match_date;link_to_match; """
    # Checking vaiables
    if not lst_of_matches:
        lst_of_matches = []

    # Getting html from site
    ans = requests.get("http://ufcstats.com/statistics/events/upcoming")
    if str(ans.status_code) != "200":  # Checking for correctness
        raise Exception("Can't connect to site")

    # Parsing
    return parsing_table_of_matches(ans, lst_of_matches)


def parsing_table_of_matches(html_var, lst_of_matches: list = None):
    """ Parse a table from ufcstats.com """
    # Checking variables
    if lst_of_matches is None:
        lst_of_matches = []

    soup = BeautifulSoup(html_var.text, 'lxml')
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
    if fst_info.td.p:  # Past
        if str(fst_info.td.p.text).strip() == 'win':  # Has winner
            winner = True
        else:  # Draw
            winner = False

        fighters = fst_info.find('td', {"class": "b-fight-details__table-col l-page_align_left"})
        prop = fst_info.find_all('td', {"class": "b-fight-details__table-col"})[2:]
        prop = [el.text.split() for el in prop]

        # First fighter
        text_icq = f"{'<b>Win</b>' if winner else '<b>Draw</b>'}: "
        text_icq += f"{'_'.join(fighters.text.split()[:2]).strip()}\nKD: {prop[0][0]}\nSTR: {prop[1][0]}\n" \
                    f"TD: {prop[2][0]}\nSUB: {prop[3][0]}\n\n"
        # Second fighter
        text_icq += f"{'<b>Lose</b>' if winner else '<b>Draw</b>'}: "
        text_icq += f"{'_'.join(fighters.text.split()[2:]).strip()}\nKD: {prop[0][1]}\nSTR: {prop[1][1]}\n" \
                    f"TD: {prop[2][1]}\nSUB: {prop[3][1]}\n\n"
        # Properties of Match:
        text_icq += f"<b>Properties of match</b>:\nWeight_class: {' '.join(prop[4])}\nMethode: {prop[5][0]}\n" \
                    f"Round: {prop[6][0]}\nTime: {prop[7][0]}"

        return text_icq
    else:  # Future
        pass


if __name__ == "__main__":
    ans1 = requests.get("http://ufcstats.com/event-details/56ec58954158966a")
    ans2 = requests.get("http://ufcstats.com/event-details/5717efc6f271cd52")
    print(parse_info_matches(ans1.text))
    # parse_info_matches(ans2.text)

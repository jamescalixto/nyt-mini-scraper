import config
from datetime import date, datetime
import requests
import time
import utils
from bs4 import BeautifulSoup as soup


def login():
    """Return the NYT-S cookie after logging in.
    Adapted from https://github.com/kyledeanreinford/NYT_Mini_Leaderboard_Scraper."""
    login_resp = requests.post(
        "https://myaccount.nytimes.com/svc/ios/v2/login",
        data={
            "login": config.username,
            "password": config.password,
        },
        headers={
            "User-Agent": "Crosswords/20191213190708 CFNetwork/1128.0.1 Darwin/19.6.0",
            "client_id": "ios.crosswords",
        },
    )
    login_resp.raise_for_status()
    for cookie in login_resp.json()["data"]["cookies"]:
        if cookie["name"] == "NYT-S":
            return cookie["cipheredValue"]
    raise ValueError("NYT-S cookie not found")


def get_leaderboard_times(cookie):
    """Get mini times from the leaderboard as name:seconds key-value pairs. Also return
    the date of the leaderboard.
    Adapted from https://github.com/kyledeanreinford/NYT_Mini_Leaderboard_Scraper."""
    url = "https://www.nytimes.com/puzzles/leaderboards"
    response = requests.get(
        url,
        cookies={
            "NYT-S": cookie,
        },
    )
    page = soup(response.content, features="html.parser")
    date_str = page.find_all("h3", class_="lbd-type__date")[0].text.strip()
    solvers = page.find_all("div", class_="lbd-score")

    times = {}
    for solver in solvers:
        name = solver.find("p", class_="lbd-score__name").text.strip()
        try:
            time = solver.find("p", class_="lbd-score__time").text.strip()
        except:
            time = None
        if name.endswith("(you)"):
            name_split = name.split()
            name = name_split[0]
        if (
            (config.included_usernames and name in config.included_usernames)
            or (config.excluded_usernames and name not in config.excluded_usernames)
            or (config.included_usernames is None and config.excluded_usernames is None)
        ):
            times[name] = utils.time_to_secs(time)
    return times, parse_leaderboard_date(date_str)


def parse_leaderboard_date(d):
    """Turns string of format '%A, %B %d, %Y' into a MM/DD/YYYY string. Used to convert
    the 'Saturday, March 19, 2022'-style header into the format for storing data."""
    return datetime.strptime(d, "%A, %B %d, %Y").date().strftime("%m/%d/%Y")


def write_to_file(times, date_str=utils.format_date()):
    """Write fetched mini times to a file."""
    obj = utils.file_to_object()
    obj[date_str] = times
    utils.object_to_file(obj)


def get_stored_times(date_str):
    """Get stored data for the given date string."""
    return utils.file_to_object()[date_str]


def merge_times(stored_data, new_data):
    """Merges stored data with new (live fetched) data. Allows for manually editing the
    file when the leaderboard breaks, without it being overwritten."""
    merged_data = {
        player: (
            stored_data[player]
            if stored_data.get(player, utils.BIG_NUMBER) != utils.BIG_NUMBER
            else time
        )  # if existing data has non-placeholder value, use that instead.
        for player, time in new_data.items()
    }
    return merged_data


def fetch_and_save_data():
    """Fetch today's mini times and write to file."""
    cookie = login()
    time.sleep(3)
    times, date_str = get_leaderboard_times(cookie)
    stored_times = get_stored_times(date_str)
    merged_times = merge_times(stored_times, times)
    write_to_file(merged_times, date_str)

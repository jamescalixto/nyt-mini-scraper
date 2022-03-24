from calendar import monthrange
from collections import Counter
from datetime import date, timedelta
import time
import utils


def is_last_day_of_week(d=date.today()):
    """Return True if it's the last day of the week."""
    return d.weekday() == 6


def is_last_day_of_month(d=date.today()):
    """Return True if it's the last day of the month."""
    return d.day == monthrange(d.year, d.month)[1]


def is_last_day_of_year(d=date.today()):
    """Return True if it's the last day of the year."""
    return d.month == 12 and d.day == 31


def generate_week_dates(d):
    """Given a date, generate the dates (as date objects) for the first day (Monday) and
    last day (Sunday) of the week including it."""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def generate_week_date_range(d=date.today()):
    """Given a date, generate the dates (as MM/DD/YYYY strings) for the Mon-Sun week
    including it."""
    monday, sunday = generate_week_dates(d)
    return [
        utils.format_date(monday + timedelta(days=i))
        for i in range((sunday - monday).days + 1)
    ]


def generate_month_dates(d):
    """Given a date, generate the dates (as date objects) for the first and last of the
    month including it."""
    first_day_of_month = d.replace(day=1)
    last_day_of_month = first_day_of_month + timedelta(
        days=monthrange(d.year, d.month)[1]
    )
    return first_day_of_month, last_day_of_month


def generate_month_date_range(d=date.today()):
    """Given a date, generate the dates (as MM/DD/YYYY strings) for the first and last
    of the month including it."""
    first_day_of_month, last_day_of_month = generate_month_dates(d)
    return [
        utils.format_date(first_day_of_month + timedelta(days=i))
        for i in range((last_day_of_month - first_day_of_month).days)
    ]


def generate_year_dates(d):
    """Given a date, generate the dates (as date objects) for Jan 1 to Dec 31 of the
    year including it."""
    first_day_of_year = d.replace(month=1, day=1)
    last_day_of_year = d.replace(month=12, day=31)
    return first_day_of_year, last_day_of_year


def generate_year_date_range(d=date.today()):
    """Given a date, generate the dates (as MM/DD/YYYY strings) for Jan 1 to Dec 31 of
    the year including it."""
    first_day_of_year, last_day_of_year = generate_year_dates(d)
    return [
        utils.format_date(first_day_of_year + timedelta(days=i))
        for i in range((last_day_of_year - first_day_of_year).days + 1)
    ]


def get_wins_over_dates(dates):
    """Get the number of wins for each player over the given dates."""
    wins = Counter()
    data = utils.file_to_object()
    for d in dates:
        if d in data:
            min_time = min(data[d].values())
            for name, time in data[d].items():
                if time == min_time:
                    wins[name] += 1
                else:
                    wins[name] += 0  # put name in wins, but with 0 wins.
    return wins


def get_most_recent_fetched_date():
    """Get the date object representing of the most recent fetched date in stored data."""
    obj = utils.file_to_object()
    dates = [utils.parse_date(d) for d in obj.keys()]
    return max(dates)


def day_message(d):
    """Post a message summarizing times for a single day."""
    data = utils.file_to_object()
    d_str = utils.format_date(d)
    if d_str in data:
        min_secs = min(data[d_str].values())
        day_data = sorted(
            [(name, secs) for name, secs in data[d_str].items()], key=lambda x: x[1]
        )
        lines = ["{} ({})".format(utils.format_date(d), d.strftime("%A"))]
        for name, secs in day_data:
            line = "{}  |  {}".format(utils.secs_to_time(secs), name)
            if secs == min_secs:
                line += "  🏆"
            lines.append(line)
        return "\n".join(lines)


def interval_message(lines, dates):
    """Post a message summarizing wins over the given interval. Takes in a lines
    parameter that it appends the summary to — so a header can be provided as needed."""
    wins = get_wins_over_dates(dates)
    wins = sorted(
        [(name, wins) for name, wins in wins.items()], key=lambda x: x[1], reverse=True
    )
    max_wins = max((x[1] for x in wins))
    for nw in wins:
        name, wins = nw
        line = "{}  |  {}".format(str(wins).rjust(4, " "), name)
        if wins == max_wins:
            line += "  👑"
        lines.append(line)
    return "\n".join(lines)


def build_and_post_messages(
    d=get_most_recent_fetched_date(),
    message_delay=360,  # time between posting messages, in seconds.
):
    """Post messages summarizing the given day, and possibly some intervals as well.
    Takes in an optional backfill parameter to delay the messages by 10 minutes to make
    Discord backfills look nicer. Also can set flags to determine which message(s) to
    print."""
    messages = [day_message(d)]  # messages to print.
    if is_last_day_of_week(d):
        lines = ["🎉 {} Weekly Champion 🎉".format(d.strftime("%b %-d"))]
        messages.append(interval_message(lines, generate_week_date_range(d)))
    if is_last_day_of_month(d):
        lines = ["🎉 {}'s Monthly Champion 🎉".format(d.strftime("%B"))]
        messages.append(interval_message(lines, generate_month_date_range(d)))
    if is_last_day_of_year(d):
        lines = ["🎉 {}'s Yearly Champion 🎉".format(d.strftime("%Y"))]
        messages.append(interval_message(lines, generate_year_date_range(d)))
    for index, message in enumerate(messages):
        utils.post_message(message)
        if index != len(messages) - 1:  # build in delay. Makes backfills look nicer.
            delay = message_delay
            time.sleep(delay)


def backfill_messages():
    """Posts messages for all days (in chronological order) that there is stored data
    for. Does this at an artificially slow rate to make the Discord backfills look
    nicer, as Discord automatically chunks close messages together and messes up the
    formatting."""
    BACKFILL_MESSAGE_DELAY = 360
    data = utils.file_to_object()
    for d_str in sorted(set(data.keys())):
        d = utils.parse_date(d_str)
        build_and_post_messages(d, message_delay=BACKFILL_MESSAGE_DELAY)

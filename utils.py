import config
from datetime import date
from discord_webhook import DiscordWebhook


filename = "data.csv"  # file to store historical mini data.
error_filename = "errors.txt"  # file to log errors.
BIG_NUMBER = 999  # used for number of seconds of uncompleted minis.


def get_date(current_date):
    """Get tuple of month, day, year from date."""
    month = str(current_date.strftime("%m"))
    day = str(current_date.strftime("%d"))
    year = str(current_date.strftime("%Y"))
    return month, day, year


def format_date(date=date.today()):
    """Formats date object as MM/DD/YYYY string."""
    month, day, year = get_date(date)
    return "{}/{}/{}".format(month, day, year)


def parse_date(date_str):
    """Turn MM/DD/YYYY date into a date object."""
    month, day, year = date_str.split("/")
    return date(int(year), int(month), int(day))


def time_to_secs(t):
    """Turn a time (string M:SS} into seconds."""
    try:
        secs = int(t.split(":")[0]) * 60 + int(t.split(":")[1])
        return secs
    except:
        return BIG_NUMBER


def secs_to_time(s):
    """Turn seconds into a time string (M:SS)."""
    if s == BIG_NUMBER:
        return "-----"
    else:
        mins = s // 60
        secs = s % 60
        return "{}:{}".format(mins, str(secs).zfill(2))


def file_to_object():
    """Read stored data and return an dict of date:time pairs, where the time values
    are also dicts of name:secs pairs."""
    obj = {}
    with open(filename, "r") as f:
        for line in f:
            date, *times = line.strip().split(",")
            times = {time.split("|")[1]: int(time.split("|")[0]) for time in times}
            obj[date] = times
    return obj


def object_to_file(obj):
    """Write dict of date:{name:secs} to file."""
    with open(filename, "w") as f:
        for date, times in obj.items():
            f.write(date + ",")
            f.write(",".join(str(time) + "|" + name for name, time in times.items()))
            f.write("\n")


def post_message(message):
    """Post message to Discord."""
    if message is not None:
        webhook = DiscordWebhook(
            url=config.discord_url,
            content=message,
        )
        return webhook.execute()


def log_error(error):
    """Log error to file."""
    with open("errors.txt", "a") as f:
        f.write("{}: {}".format(format_date(), str(error)))
        f.write("\n")

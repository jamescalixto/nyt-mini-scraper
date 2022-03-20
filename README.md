# nyt-mini-scraper

Scripts to scrape leaderboards from the New York Times mini crossword and output daily/weekly/monthly/yearly summaries to a Discord webhook.

## Acknowledgements

Credit to <https://github.com/kyledeanreinford/NYT_Mini_Leaderboard_Scraper> for the login and scraping code.

## Setup

1. In the main directory, set up a `config.py` file with the following variables:

    - `included_usernames`, names on the leaderboard to include in results. If this is set, then only names in this list will be recorded by the script. Overrides `excluded_usernames`.
    - `excluded_usernames`, names on the leaderboard to exclude in results. If this is set, then all names on the leaderboard will be recorded by the script, except for names on this list.
    - `username`, New York Times puzzle account username.
    - `password`, New York Times puzzle account password.
    - `discord_url`, the [Discord webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) to post to.

    So the file should look like:

    ```python
    # Players to include/exclude from scraping. Only one should be set.
    included_usernames = ["Alice", "Bob"]
    excluded_usernames = None

    # NYTimes account login credentials.
    username = "example@example.org"
    password = "password123"

    # Discord webhook URL.
    discord_url = "https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz"
    ```

2. Set up a cron job to fetch and post messages, using `python3 main.py --fetch --post` for the following:

    - `59 21 * * 1-5` weekdays at 9:59 PM, and
    - `59 17 * * 0,6` weekends at 5:59 PM.

    The mini updates at 10 PM on weekdays and 6 PM on weekends, so unless a player finishes the crossword at the literal last minute, then this should grab the final scores of the day.

    Alternatively, to make the display look nicer on mobile, you can do `python3 main.py --fetch` for:

    - `59 21 * * 1-5` weekdays at 9:59 PM, and
    - `59 17 * * 0,6` weekends at 5:59 PM,

    as well as `python3 main.py --post` for:

    - `59 23 * * *` daily at 11:59 PM.

    Mobile Discord chunks messages that are within ~5-10 minutes, which throws off formatting. Separating the fetch and post calls fixes this.

3. (optional) Set up a cron job to periodically fetch, using `python3 main.py --fetch`

    If something goes wrong with the scraping, then the day's data will be lost. To mitigate this risk, you can have the script fetch but not post messages throughout the day. The script will update the stored data file with the most up-to-date data.

    Note that the script will store the fetched times under the _puzzle_ date, not the calendar date; i.e., at 11 PM on Saturday, March 19, the puzzle on the website is actually Sunday, March 20's puzzle — the script will store it correctly under 03/20/2022.

## Usage and notes

### Functionality and arguments

Three actions are supported:

- _fetching_, set with the `--fetch` flag, which scrapes the mini site and records the results in the file for `utils.filename`.
- _posting_, set with the `--post` flag, which posts the daily summary as well as the week/month/year summary if it is the last day of the week/month/year respectively. The week is considered to start on Monday and end on Sunday.
- _backfilling_, set with the `--backfill` flag, which goes through every day with data in the file in `utils.filename` in chronological order and posts messages for each day. When done with a new Discord channel, this backfills all of the data into it at 10-minute intervals (so it looks nicer on mobile).

### What it looks like

Daily summary:

```text
mini-stats: 03/19/2022 (Saturday)
0:23  |  Quick Quail  🏆
0:23  |  Fast Frog  🏆
0:47  |  Average Antelope
3:18  |  Slow Sloth
----  |  Sleeping Shark
```

Weekly summary:

```text
mini-stats: 🎉 Mar 21 Weekly Champion 🎉
   4  |  Quick Quail  👑
   2  |  Fast Frog
   1  |  Average Antelope
   0  |  Slow Sloth
   0  |  Sleeping Shark
```

Monthly summary:

```text
mini-stats: 🎉 March's Monthly Champion 🎉
  17  |  Quick Quail  👑
   8  |  Fast Frog
   3  |  Average Antelope
   3  |  Slow Sloth
   0  |  Sleeping Shark
```

Yearly summary:

```text
mini-stats: 🎉 2022's Yearly Champion 🎉
 185  |  Quick Quail  👑
  99  |  Fast Frog
  56  |  Average Antelope
  24  |  Slow Sloth
   1  |  Sleeping Shark
```

### Scraping the site

Occasionally the New York Times changes their anti-bot security measures and this will fail. Caveat emptor.

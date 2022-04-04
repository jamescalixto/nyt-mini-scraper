from fetcher import fetch_and_save_data
import argparse
from poster import build_and_post_messages, backfill_messages
import utils


def get_args():
    """Set up command line parser and return args."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Fetch leaderboard data.")
    parser.add_argument("--post", action="store_true", help="Post summaries for today.")
    parser.add_argument("--date", type=str, help="Date to post summaries for.")
    parser.add_argument(
        "--backfill", action="store_true", help="Post summaries for all days stored."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    try:
        if args.fetch:
            fetch_and_save_data()
        if args.post:
            build_and_post_messages(utils.parse_date(args.date) if args.date else None)
        if args.backfill:
            backfill_messages()
    except Exception as e:
        utils.log_error(e)
        utils.post_message("Error!\n🚨🚨🚨 {} 🚨🚨🚨".format(e))

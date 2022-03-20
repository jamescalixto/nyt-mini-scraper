from datetime import date
import poster
import random
import utils

# This script generates fake data for an entire year, for testing and mockup purposes.
# Happy mocking!

filename = "fake_data.csv"  # file to store fake data in.

# Make each sample name have a different level of skill. Use gamma distribution.
NAMES = [
    "Quick Quagga",
    "Tricky Tapir",
    "Wiggly Wombat",
    "Plucky Pronghorn",
    "Brave Burro",
    "Dizzy Dormouse",
]
ALPHA_RANGE = (3, 5)  # range of the alpha parameter for gammavariate distribution.
BETA_RANGE = (5, 20)  # range of the beta parameter for gammavariate distribution.
FORFEIT_RANGE = (0.0, 0.1)  # range of probability of forfeit.
names_params = {
    name: (
        random.uniform(*ALPHA_RANGE),
        random.uniform(*BETA_RANGE),
        random.uniform(*FORFEIT_RANGE),
    )
    for name in NAMES
}  # generate random parameters for each character.

# Set up function to generate fake data, given a tuple of alpha, beta, forfeit params.
def generate_fake_time(params):
    alpha, beta, forfeit = params
    if random.random() < forfeit:
        return utils.BIG_NUMBER
    else:
        return int(random.gammavariate(alpha, beta))


# Set up date range to fake.
YEAR_TO_FAKE = 2017  # last day will trigger week/month/year summaries.
day_in_year = date(YEAR_TO_FAKE, 1, 1)  # make the first day of the year.
year_dates = poster.generate_year_date_range(day_in_year)  # get all dates in year.

# Generate fake data.
obj = {}
for d in year_dates:
    times = {name: generate_fake_time(names_params[name]) for name in NAMES}
    obj[d] = times
utils.object_to_file(obj, filename=filename)

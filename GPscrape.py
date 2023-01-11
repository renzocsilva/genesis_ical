import requests
import re
import pytz
import os
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime as dt
from datetime import timedelta, date, time
from pathlib import Path

# Web Scrapping
url = "https://www.airdrie.ca/index.cfm?serviceID=2166"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")
table = soup.find('table')

# Parameters
first_day = date(2023, 1, 3)
last_day = date(2023, 3, 31)
filename = "GP_group_fitness.ics"

# Find all rows in the table
rows = table.find_all('tr')

# Get the header row
header_row = rows[0]

# Get the cells in the header row
header_cells = header_row.find_all('th')

# Get the day of the week from the header row
days_of_week = [cell.text for cell in header_cells]

# Create a calendar object
cal = Calendar()
tzone = pytz.timezone('Canada/Mountain')
cal.add('VTIMEZONE', tzone)

# Set the calendar name and timezone
cal.add('prodid', '-//My calendar//mxm.dk//')
cal.add('version', '2.0')
cal.add('X-WR-CALNAME', 'Recreation Center Drop-In Activities')
cal.add('X-WR-TIMEZONE', 'Canada/Mountain')

# Iterate over the rows and cells in the table
for i, row in enumerate(rows[1:]):
    cells = row.find_all('td')
    for j, cell in enumerate(cells):
        # Get the data from the cell
        data = cell.text

        # Split the data into lines
        lines = data.split('\n')

        # Remove empty lines
        lines = [line for line in lines if line]

        # Get the day of the week
        week_day = days_of_week[j]

        # Iterate over the lines
        for line in lines:

            # Skip invalid lines
            if not line.strip():
                continue

            # Split the line into multiple entries if necessary
            entries = line.split(".m.")

            # Iterate over the entries
            for entry in entries:
                # Skip empty entries
                if not entry.strip():
                    continue

                # FIX: split withouh removing the delimiter
                entry += ".m."

                # Split the entry on the first space
                class_name, time = re.split(r'(^[^\d]+)', entry)[1:]

                # Strip leading and trailing whitespace from the class name and times
                class_name = class_name.strip()
                start_time, end_time = [time.strip()
                                        for time in time.split(' - ')]
                end_time, time = end_time.split(' ')

                # Handle integer entries e.g. 9 a.m. instead of 9:00 a.m.
                if ":" not in start_time:
                    start_time = f"{start_time}:00"

                if ":" not in end_time:
                    end_time = f"{end_time}:00"

                # Calculate the start date
                week_day_index = days_of_week.index(week_day)
                days_until_week_day = (
                    week_day_index - first_day.weekday()) % 7
                start_date = first_day + timedelta(days_until_week_day)

                # Set the start and end time for the event
                start_time = dt.combine(
                    start_date, dt.strptime(start_time, "%H:%M").time())
                end_time = dt.combine(
                    start_date, dt.strptime(end_time, "%H:%M").time())

                # Set 24h format, and handle input formatting e.g. 11 - 2 p.m.
                if time == 'p.m.':
                    end_time += timedelta(hours=12)
                if start_time < end_time and time == 'p.m.' and start_time.hour < 12:
                    start_time += timedelta(hours=12)

                # Add time zone info
                start_time = start_time.replace(tzinfo=tzone)
                end_time = end_time.replace(tzinfo=tzone)

                # Create an Event object
                event = Event()

                # Set the event attributes
                event.add('summary', class_name)
                event.add('location', 'Genesis Place')
                event.add('dtstart', start_time, {'TZID': 'Canada/Mountain'})
                event.add('dtend', end_time, {'TZID': 'Canada/Mountain'})
                event.add('rrule', {
                    'freq': 'weekly',
                    'until': last_day,
                })

                cal.add_component(event)

# Write to disk
directory = Path.cwd() / 'MyCalendar'

try:
    directory.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print("Folder already exists")
else:
    print("Folder was created")

f = open(os.path.join(directory, filename), 'w')
f.write(cal.to_ical().decode())
f.close()

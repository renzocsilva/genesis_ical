## Scraped table of activities into an .ical file
The code is a web scraping script that extracts Group Fitness schedule data from Airdrie's (Alberta, Canada) local recreation center [website](https://www.airdrie.ca/index.cfm?serviceID=2166) and creates an ics file (calendar file) from the scraped data. The script uses the python libraries *requests*, *BeautifulSoup*, and *icalendar*.

The targeted information is available to readers in a table format, but not in a machine-friendly way. The script iterates through the rows and cells of the table to extract the relevant data (class name, start time, end time), then converts the extracted data into an icalendar format using icalendar library. 

The final ics file can be imported to any calendar application that supports the icalendar format, allowing the user to view and manage the group fitness schedule.

This was meant to be a quick, private hack, but in the end the code is clean and useful enough to be made public and potentially re-used.

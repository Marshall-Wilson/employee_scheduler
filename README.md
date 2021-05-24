# Overnight Program Employee Scheduler 
##### by Marshall Wilson 
##### last edited 4/23/2021

## Purpose: 
This program automates the scheduling of employees for an overnight season using Google OR-Tools' MIP linear solver. It finds a solution that assigns employees only to available dates and maximizes the frequency that employees get assigned to their prefered days.

************************

## Use: 
Run `employee_scheduler.py` in Python. When prompted, select a list of dates and roster of employees that conforms to the format laid out in `employees_template.csv` and `on_dates_template.csv`. The result will be output as a file named `output_schedule.csv`.

***********************

## TODO:
* Add constraint on non-standard unavailable dates
* Add variable preferences (i.e. can work thurs, fri, sat but thurs > sat > fri)

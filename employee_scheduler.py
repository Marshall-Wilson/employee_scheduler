import pandas as pd
import numpy as np
import easygui as eg
from ortools.linear_solver import pywraplp
from datetime import datetime, timedelta

roles = ['MOD', 'HON', 'ON', 'SW']

def main():

    # Load data from csv's
    dates = load_dates()
    employees = load_employees()

    # Initialize solver and variables
    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    assigned_date, assigned_week = initialize_vars(solver, employees, dates)
    
    # Initialize constraints

    # Constraints:
    # nobody can work more than 1 shift at a time 
    for i in employees['name']:
        for j in dates['date']:
            solver.Add(solver.Sum([assigned_date[i, j, k] for k in roles]) <= 1)

    # exactly 1 MOD, 1 HON, 3 ON, 1 SW per night 
    for j in dates['date']:
        solver.Add(solver.Sum([assigned_date[i, j, 'MOD'] for i in employees['name']]) == 1)
        solver.Add(solver.Sum([assigned_date[i, j, 'HON'] for i in employees['name']]) == 1)
        solver.Add(solver.Sum([assigned_date[i, j, 'ON'] for i in employees['name']]) == 3)
        solver.Add(solver.Sum([assigned_date[i, j, 'SW'] for i in employees['name']]) == 1)

    # tie assigned_date to assigned_week
    for i in employees['name']:
        for j in dates['date']:
            dates_in_range = []
            for date in dates['date']:
                if j - timedelta(days=10) <= date <= j + timedelta(days=10):
                    dates_in_range.append(date)

            solver.Add(assigned_week[i, j] == \
                solver.Sum([assigned_date[i, d, k] for d in dates_in_range \
                                                    for k in roles]))
    

    # no more than 1 shift per week 
    for i in employees['name']:
        for j in dates['date']:
            solver.Add(assigned_week[(i, j)] <= 2)
    
    # people can only work jobs they have 
    for i, r in employees.iterrows():
        for j in dates['date']:
            for k in roles:
                solver.Add(assigned_date[employees.loc[i, 'name'], j, k] <= employees.loc[i, 'role_'+k])

    # people can only work days they're available
    for i, r in employees.iterrows():
        for j, s in dates.iterrows():
            for k in roles:
                solver.Add(assigned_date[employees.loc[i, 'name'], dates.loc[j, 'date'], k] <= employees.loc[i, dates.loc[j, 'day'].lower()+'_avail'])


    # define objective (maximum preference)
    solver.Maximize(solver.Sum([assigned_date[employees.loc[i, 'name'], dates.loc[j, 'date'], k] * (employees.loc[i, dates.loc[j, 'day'].lower() + '_pref'] + 0.5) for i, r in employees.iterrows()\
                                                                                for j, s in dates.iterrows()\
                                                                                for k in roles]))

    solution_status = solver.Solve()

    output_assignments(assigned_date, employees, dates)

    return




def load_employees() -> pd.DataFrame:
    """ returns a dataframe containing the imported overnight employees """
    employee_path = eg.fileopenbox("Select Employee CSV File")
    employee_df = pd.read_csv(employee_path)
    return employee_df


def load_dates() -> pd.DataFrame:
    """ returns a dataframe containing the imported overnight dates """
    date_path = eg.fileopenbox("Select ON Dates CSV File")
    date_df = pd.read_csv(date_path, parse_dates=['date'])
    return date_df


def initialize_vars(solver: pywraplp.Solver, employees: pd.DataFrame, \
                    dates: pd.DataFrame) -> tuple[dict]:
    """ Initialize the assigned_date and assigned_week variables """

    # 1 if employee is assigned to role on date, 0 oow
    assigned_date = {}
    for i in employees['name']:
        for j in dates['date']:
            for k in roles:
                assigned_date[(i, j, k)] = \
                        solver.BoolVar('assigned_%s_%s_%s' % (i, j, k))

    # each entry stores how many overnights that employee is assigned to within a week of that date
    assigned_week = {}
    for i in employees['name']:
        for j in dates['date']:
            assigned_week[(i, j)] = solver.IntVar(0, 100, 'assigned_week_%s_%s' % (i, j))

    return (assigned_date, assigned_week)


def link_variables(solver: pywraplp.Solver, assigned_date: dict, \
                    assigned_week: dict, employees: pd.DataFrame, \
                    dates: pd.DataFrame):
    """ Links the assigned_date and assigned_week to each other """
    for i in employees['name']:
        for j in dates['date']:
            dates_in_range = []
            for date in dates['date']:
                # Collect list of dates within one week of current date
                if j - timedelta(days=10) <= date <= j + timedelta(days=10):
                    dates_in_range.append(date) 

                solver.Add(assigned_week[i, j] == \
                            solver.Sum([assigned_date[i, d, k] \
                                        for d in dates_in_range \
                                        for k in roles]))


def output_assignments(assigned_date: dict, employees: pd.DataFrame, \
                    dates: pd.DataFrame):
    """ outputs the solution assignments as a .csv file """
    column_names = ["Date", "Day", "MOD", "HON", "ON1", "ON2", "ON3", "SW"]
    output_df = pd.DataFrame(columns=column_names)
    
    for i, row in dates.iterrows():
        output_df.loc[i, "Date"] = row["date"]
        output_df.loc[i, "Day"] = row["day"] 
        on_count = 1       
        for name in employees["name"]:
            for role in roles:
                if assigned_date[name, dates.loc[i, "date"], role].solution_value() == 1:
                    if role == "ON":
                        output_df.loc[i, "ON" + str(on_count)] = name
                        on_count += 1
                    else:
                        output_df.loc[i, role] = name
    output_df.to_csv("output_schedule.csv")

if __name__ == '__main__':
    main()
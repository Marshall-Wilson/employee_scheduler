import pandas as pd
import numpy as np
import easygui as eg
from ortools.linear_solver import pywraplp

roles = ['MOD', 'HON', 'ON', 'SW']

def main():
    data = {}
    data.update(load_employees())
    data.update(load_dates())

    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # 1 if employee is assigned to role on date, 0 oow
    assigned_date = {}
    for i in data['name']:
        for j in data['date']:
            for k in roles:
                assigned_date[(i, j, k)] = solver.IntVar(0, 1, 'assigned_%s_%s_%s' % (i, j, k))


    # Constraints:
    # nobody can work more than 1 shift at a time 
    for i in data['name']:
        for j in data['date']:
            solver.Add(sum(assigned_date[i, j, k] for k in roles) <= 1)

    # exactly 1 

    return




''' returns a dataframe containing the imported overnight employee preferences '''
def load_employees():
    employees = {}
    df = pd.read_csv(eg.fileopenbox('Import Employees'))
    for i in range(len(df.columns)):
        name = df.columns[i]
        employees[f'{name}'] = df.iloc[:, i]

    return employees


''' returns a dataframe containing the imported overnight dates '''
def load_dates():
    dates = {}
    df = pd.read_csv(eg.fileopenbox('Import ON Dates'))
    for i in range(len(df.columns)):
        name = df.columns[i]
        dates[f'{name}'] = df.iloc[:, i]
        
    return dates


if __name__ == '__main__':
    main()
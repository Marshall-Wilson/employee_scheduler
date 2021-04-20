import pandas as pd
from datetime import datetime, timedelta

def main():
    df = pd.read_csv("on_dates.csv", parse_dates=['date'])
    d1 = (df.loc[2, 'date'])
    d2 = (df.loc[2, 'date'] + timedelta(days=8))
    
    for dates in df.loc[:,'date']:
        print(dates)

if __name__ == '__main__':
    main()
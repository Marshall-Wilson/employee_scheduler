import pandas as pd
from datetime import datetime, timedelta
import easygui as eg 
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

def main():

    

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = eg.fileopenbox() # show an "Open" dialog box and return the path to the selected file
    print(filename)
    filename2 = eg.fileopenbox() # show an "Open" dialog box and return the path to the selected file
    print(filename2)

if __name__ == '__main__':
    main()
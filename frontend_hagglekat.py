"""
A front end GUI for the Google vision + Ebay APIs
Image, Best Guess from GVision
(Label widgets)

The user can:
Upload an image
Search for an image
View all hits (Listbox) (Scroll bar)
Close the program
"""

from tkinter import *
from tkinter import ttk

import backend_hagglekat as bh
import os, fnmatch

def get_image():
    #function to get the selected image
    print("get_image")

def search_image():
    #function to search the uploaded image
    print("search")

def show_hits():
    #function to write the hits to listbox
    if (tkvar.get()=="<select>"):
        print("Need to enter an image file")
    else:
        print("classifying image now!!")
        best_guess = bh.classify_image(tkvar.get())
    l3['text']=best_guess
    deals_df=bh.call_ebay_api(best_guess)
    print(deals_df)
    for rows in range(0,deals_df.shape[0]):
        list1.insert(END, deals_df.iloc[rows,2])

#GUI design
window = Tk() #create a window object

window.wm_title("HaggleKat Tool by MDS")
mds_logo = PhotoImage(file="method_logo_small.png")

#labels
logo = Label(window, image = mds_logo)
logo.grid(row=12,column=0)

l1 = Label(window, text="Best Guess:")
l1.grid(row=3,column=2)

l2 = Label(window, text="Hit List:       ")
l2.grid(row=4,column=2)

l3 = Label(window, text = "??????????")
l3.grid(row=3, column=3)

list_files=[]
pattern = "*.JPG"  
listOfFiles = os.listdir('.')
for entry in listOfFiles:
    if fnmatch.fnmatch(entry, pattern):
        print (entry)
        list_files.append(entry)

# Create a Tkinter variable for use in the PopupMenu
tkvar = StringVar(window)
tkvar.set('<select>') # set the default option
 
popupMenu = OptionMenu(window, tkvar, *list_files)
Label(window, text="Choose an Image File").grid(row = 7, column = 0)
popupMenu.grid(row = 8, column =0)
 
# on change dropdown value
def change_dropdown(*args):
    print( tkvar.get() )
 
# link function to change dropdown
tkvar.trace('w', change_dropdown)     

#Listbox
list1 = Listbox(window, height=6, width=100)
list1.grid(row=6,column=2,rowspan=6,columnspan=2)

#Scrollbar
sb1 = Scrollbar(window)
sb1.grid(row=4,column=4,rowspan=6)

list1.configure(yscrollcommand=sb1.set)
sb1.configure(command=list1.yview)

#buttons
b1=Button(window,text = "Classify Image",width=11, command=show_hits)
b1.grid(row=3,column=0)

b3=Button(window,text = "Close",width=11,command=window.destroy)
b3.grid(row=9,column=0)

#Entry cells

# bg_text=StringVar() #best guess
# e1=Entry(window, textvariable=bg_text)
# e1.grid(row=3,column=3)

#wrap up all the widgets
window.mainloop()

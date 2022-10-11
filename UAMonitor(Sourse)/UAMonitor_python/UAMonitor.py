
#-------------------------------------------------------------------------------
#  UAMonitor: A controler for a homemade spectrophotometer creaded for
#                       iGEM Competition 2022 (beta v0.1)
#  Silva Tovar Mauricio 
#  Reyes Morales Laura Mariana 
#  Carrasco González Mauricio 
#    October, 2022
#                            iGEM UAM
#-------------------------------------------------------------------------------

#Abilitate if you use jupiterlab
#%matplotlib widget
#Paketing used
import tkinter
import serial     
import time
import os
import re
import threading
import multiprocessing
import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime
from tkinter import filedialog

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.pyplot import *
import matplotlib.animation as animation
from matplotlib import backend_bases


#Inicial conditions
ledFlu=0
ledOD=0





#Create a Tkinterface with our icon and title
root = tkinter.Tk()
root.wm_title("UAMonitor")

if "nt" == os.name:
  root.wm_iconbitmap(bitmap = "iGEM.ico")
else:
  root.wm_iconbitmap(bitmap = "iGEM.xbm")

#root['background']='yellow'

#imgicon = PhotoImage(file=os.path.join(Documents/Mauricio/iGEM/Arduino/Espectro_Foto/sketch_sep28a/iGEM.ico,'iGEM.ico'))
#root.tk.call('wm', 'iconphoto', root._w, imgicon)  


"""
Frame = tkinter.Frame() #Frame creation
Frame.config(cursor="heart")
Frame.config(width="150", height="150")
Frame.pack(fill="both")
Frame.config(bg="blue")
Frame.pack(side="bottom")
"""

# initialize the data arrays 
gDATA = []
gDATA.append([0])
gDATA.append([0])
gDATA.append([0])

# create a figure with two subplots
fig, (ax1, ax2) = subplots(1,2)

#Add the figure to the Tkinterface
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

#Configure Fluorescence plot
ax1.set_title('Fluorescence')
ax1.grid()
ax1.set_xlim((0,100))
ax1.set_ylim((-1,100))

#Configure Optical Density plot
ax2.set_title('Optical Density')
ax2.grid()
ax2.set_xlim((0,100))
ax2.set_ylim((-1,100))


# intialize two line objects (one in each axes)
line1, = ax1.plot(gDATA[0], gDATA[1], lw=2, color='green')
line2, = ax2.plot(gDATA[0], gDATA[2], lw=2, color='orange')
line = [line1, line2]



def update_line(num,line,data):
    
#     axis limits checking. Same as before, just for both axes
    for ax in [ax1, ax2]:
        xmin, xmax = ax.get_xlim()
        if max(data[0])>= xmax:
            ax.set_xlim(xmin, 1.5*xmax)
            ax.figure.canvas.draw()
    # update the data of both line objects
    line[0].set_data(data[0], data[1])
    line[1].set_data(data[0], data[2])

    return line

ani = animation.FuncAnimation(fig, update_line, blit=True, fargs=(line, gDATA),interval=100, repeat=False)




#In the next part we remove the button configure subplot because cause a warning message.
# mpl.rcParams['toolbar'] = 'None'
backend_bases.NavigationToolbar2.toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )

#Add a Toolbar to control the figure
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

"""
#For some reason this funtion print if you preesed a key
def on_key_press(event):
  print("you pressed {}".format(event.key))
  key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)
"""

def timer(condition):
  global tim
  tim=0
  while True:
    time.sleep(0.1)
    tim = tim + 0.1
    if Mode != condition:
      break
  return


def GetData(gDATA,condition,state):

  global format
  #Time 
  if condition != 'M' or state != 'O':
    format = datetime.now().strftime('%d-%m-%Y, %H;%M;%S')
  
  global vFlu
  vFlu=0
  global vOD
  vOD=0

  gDATA[0]=[0]
  gDATA[1]=[0]
  gDATA[2]=[0]

    
  #datAR =serialArduino.readline().decode('ascii') 
  datAR =serialArduino.readline().decode('ascii').strip()
  time.sleep(0.5)
   
  if condition == 'M' and state == 'O':
    time.sleep(1.0)

  format_before = '0'
  
  while True:

   
    if datAR:
      pos=datAR.index(",")
      if state == 'F':
        vFlu=int(datAR[:pos])
      if state == 'O':
        vOD=int(datAR[pos+1:])
      gDATA[0].append(tim)
      gDATA[1].append(vFlu)
      gDATA[2].append(vOD)

      saves = pd.DataFrame(gDATA,index=['Time', 'Fluorecense','Optical Density']).transpose()
      saves.to_csv('data '+str(format)+'('+str(condition)+').csv', index=False)
      if len(gDATA[0]) > 200:
        if condition != 'M' or state != 'O':
          if format_before != '0':
            data = pd.read_csv('data '+str(format)+'('+str(condition)+').csv', index=False) 
            updated_data = pd.read_csv('data '+str(format)+'.csv') 
            final_dataframe = pd.concat([data, updated_data]).drop_duplicates(subset='Time', keep='last').reset_index(drop=True) 
            final_dataframe.to_csv('data '+str(format)+'.csv', index=False)
            os.remove('data '+str(format_before)+'.csv')
          i = 0
          gDATA[0]=[]
          gDATA[1]=[]
          gDATA[2]=[]
          format_before = format
          format=datetime.now().strftime('%d-%m-%Y, %H;%M;%S')
      datAR =serialArduino.readline().decode('ascii').strip() 
      time.sleep(1)      
    if Mode != condition:
      break
  return

def Monitor_loop(condition):
  while True:
    Assing_LED(1,0)
    time.sleep(1)
    Assing_LED(0,1)
    time.sleep(1)
    print("Sí")
    if condition != 'M':
      break
  return

#This funtion control the state of the LEDs
def Assing_LED(ledFlu,ledOD):
  dat = str(ledFlu) + ","+ str(ledOD)
  serialArduino.write(dat.encode('ascii'))
  return
    
def _stop():
  if serialArduino != None:
    Assing_LED(0,0)
  global Mode
  Mode = 'X'
  return 


def _connect():
  global serialArduino
  serialArduino = serial.Serial("COM2",9600,timeout=1.0)
  if serialArduino != None:
    tkinter.messagebox.showinfo("Information Window",  "Successful connection with Arduino")
  return 

def _quit():
  root.quit()     # stops mainloop
  root.destroy()  # this is necessary on Windows to
  _stop()
  serialArduino.close()
  return          # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def _save():
  dataFile=pd.read_csv('data '+str(format)+'('+str(Mode)+').csv')
  SAVING_PATH = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
  dataFile.to_csv(SAVING_PATH)

'''**********************
*      MODES MENU      *
************************
*                      *
*  F >> Fluorence mode *
*  O >> OD mode        *
*  M >> Monitor mode   *
*  X >> Salir          *
*                      *
************************'''

#Definition of Fluorescence Mode           
def _FLU():
  global Mode
  Mode='O'
  Assing_LED(1,0)
  Cronometer = threading.Thread(target = timer, args=('F',))           
  dataCollectorFLU = threading.Thread(target = GetData, args=(gDATA,'F','F',))
  dataCollectorFLU.start()
  Cronometer.start()
  return

#Definition of Optical Density Mode
def _OD():
  global Mode
  Mode='O'
  Assing_LED(0,1)
  Cronometer = threading.Thread(target = timer, args=('O',))           
  dataCollectorOD = threading.Thread(target = GetData, args=(gDATA,'O','O',))
  dataCollectorOD.start()
  Cronometer.start()
  return

#Definition of Monitor Mode
def _MON():
  global Mode
  Mode='M'
  Assing_LED(1,1)
  #loop= threading.Thread(target = Monitor_loop, args=('M',)) 
  #loop.start()
  Cronometer = threading.Thread(target = timer, args=('M',))           
  dataCollectorMON_FLU = threading.Thread(target = GetData, args=(gDATA,'M','F',))
  dataCollectorMON_OD = threading.Thread(target = GetData, args=(gDATA,'M','O',))
  dataCollectorMON_FLU.start()  
  dataCollectorMON_OD.start()
  Cronometer.start()
  return

     

#Enable a button and option to quit the window
qui = tkinter.Button(master=root, text="Quit", command=_quit, fg="#E0218A")
qui.pack(side=tkinter.RIGHT)
         
#Enable a button and option to stop mesurate
sto = tkinter.Button(master=root, text="Stop", command=_stop, fg="#E0218A")
sto.pack(side=tkinter.RIGHT)
         
#Enable a button of the function to connect the program to Arduino  
con = tkinter.Button(master=root, text="Connect Arduino", command=_connect, fg="#E0218A")
con.pack(side=tkinter.TOP)

#Label to indicate the version
label = tkinter.Label(root, text="UAMonitor beta v0.1")
label.pack(side=tkinter.BOTTOM, anchor=tkinter.CENTER)

#Enable a button of the Monitor Mode
Mon = tkinter.Button(master=root, text="Save", command=_save, fg="#E0218A")
Mon.pack(side=tkinter.BOTTOM)

#Enable a button of the OD Mode
OD = tkinter.Button(master=root, text="OD Mode", command=_OD, fg="#E0218A")
OD.pack(side=tkinter.LEFT)

#Enable a button of the Fluorescence Mode
Flu = tkinter.Button(master=root, text="Fluorecense Mode", command=_FLU, fg="#E0218A")
Flu.pack(side=tkinter.LEFT)

#Enable a button of the Monitor Mode
#Mon = tkinter.Button(master=root, text="Monitor Mode", command=_MON, fg="#E0218A")
#Mon.pack(side=tkinter.LEFT)

root.mainloop()
# If you put root.destroy() here, it will cause an error if the window is closed with the window manager.
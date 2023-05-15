import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import serial
from tkinter import * #import EVERYTHING from tkinter library
import csv #import CSV capabilities
from itertools import zip_longest
import serial.tools.list_ports
#from bluetooth import BluetoothSocket, RFCOMM
import bluetooth

 
class TopPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent) #spliter window as the parent
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111) # first row, first column, first graph
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL) #box sizer
        self.sizer.Add(self.canvas, 1, wx.EXPAND) # adding the sizer to the canvas (exapand to the contaitner it is in)
        self.SetSizer(self.sizer) # telling the sizer to work
        self.axes.set_xlabel('Time') # x axis label
        self.axes.set_ylabel('Force')# y axis label
 
    # create the graph from arduino
    def draw(self, x, y):
        # how the graph draws itself
        self.axes.clear()
        self.axes.plot(x, y, '-o') # prints the graph a solid line with markers
        self.canvas.draw()
        
 
class BottomPanel(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent = parent) #spliter window as the parent
 
        self.graph = top # setting where the graph will be positioned on the application
 
        # remembers if the toggle button is pressed or not
        self.togglebuttonStart = wx.ToggleButton(self, id = -1, label = "Start", pos = (10,10)) #pos shows the position , id shows that we aren't assigning an id
        self.togglebuttonStart.Bind(wx.EVT_TOGGLEBUTTON, self.OnStartClick)
 
        #how to set how fast the data on the graph loads
        labelLoad = wx.StaticText(self, -1, "Display Update Frequency (ms)", pos = (200, 90))
        self.textboxSampleTime = wx.TextCtrl(self, -1, "100", pos = (240, 115), size = (50, -1)) # -1 in size makes the height default 
        self.buttonSend = wx.Button(self, -1, "Send", pos = (295, 115), size = (50, -1))
        self.buttonSend.Bind(wx.EVT_BUTTON, self.OnSend)
 
        # allows the user to zoom in on the graph by setting a range on the y axis
        labelRange = wx.StaticText(self, -1, "Zoom in On Data", pos = (450, 10))
        labelMinY = wx.StaticText(self, -1, "Min Y", pos = (450, 30))
        self.textboxMinYAxis = wx.TextCtrl(self, -1, "-20", pos = (450, 50))
        labelMaxY = wx.StaticText(self, -1, "Max Y", pos = (450, 75))
        self.textboxMaxYAxis = wx.TextCtrl(self, -1, "20", pos = (450, 95)) #outputs the analog can get
 
        # this goes with the labelMinY and labelMaxY
        # it is the button that does the setting of the range when the user enters the numbers 
        self.buttonRange = wx.Button(self, -1, "Set Y Axis", pos = (450, 120))
        self.buttonRange.Bind(wx.EVT_BUTTON, self.SetButtonRange)
 
        # to run something over and over and allows the front panel to update each iteration
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimeInterval, self.timer)
 
        # only want to make the connection the first time we press the button
        # start the arduino as false
        self.serial_connection = False
 
        # arrays for x and y to save our values
        self.x = np.array([]) # empty array to hold the values coming in from the arduino
        self.y = np.array([]) # empty array to hold the values coming in from the arduino
        self.x_counter = 0 # start it at 0
 
        # saving the data
        self.buttonSave = wx.Button(self, -1, "Save" , pos = (10, 65))
        self.buttonSave.Bind(wx.EVT_BUTTON, self.OnSave)
 
        # will restart the data
        self.buttonClear = wx.Button(self, -1, "Clear" , pos = (10, 120))
        self.buttonClear.Bind(wx.EVT_BUTTON, self.OnClear)
 
    # button that saves the data to a CSV file on the device 
    def OnSave(self, event):
        tmp = self.serial_connection
        self.y = np.append(self.y, tmp)
        self.x = np.append(self.x, self.x_counter)
        self.x_counter += 1
 
        Theader = ["Time"]
        Pheader = ["Position"]
 
    
        csv_file = open("data.csv", "w") # set where the file is saved
        writer = csv.writer(csv_file)
        writer.writerow(Theader)
        writer.writerows([self.x])
        writer.writerow(Pheader)
        writer.writerows([self.y])
 
        print("File saved!")
 
        csv_file.close()
 
        
        
    # button to clear the graph data
    def OnClear(self, event):     
        self.x = [] #set the x arrary to an empty array to reset the data
        self.y = [] #set the y arrary to an empty array to reset the data
        self.x_counter = 0 #set the counter to 0 to restart the timer at 0
        self.graph.draw(0,0) #set the graph to start at (0,0) so that it starts fresh
        print("Data Cleared") #notifies the user that the data has been cleared
 
    # button for setting the min y and max y
    def SetButtonRange(self, event):
        min = self.textboxMinYAxis.GetValue()
        max = self.textboxMaxYAxis.GetValue()
        self.graph.ChangeAxes(min, max)
 
    # in milliseconds
    # how fast the graph generates data
    def OnSend(self, event):
        val = self.textboxSampleTime.GetValue()
        self.timer.Start(int(val))
 
    # getting the serial port reading from the arduino
    def TimeInterval(self, event):
        tmp = self.serial_arduino.recv(1024).decode('utf-8').rstrip()
        print(tmp)
 
        
        try:
            self.y = np.append(self.y, float(tmp))
            self.x = np.append(self.x, self.x_counter)
            self.x_counter += 1 # increment it so it lines up with x and y
 
            self.graph.draw(self.x, self.y)
        except:
            print()    
        
    # when the start button is clicked
    def OnStartClick(self, event):
        # gets the raw ports that are returned
        # a list of the USB to serial devices that are connected to the computer
        def get_ports():
            ports = serial.tools.list_ports.comports()
            return ports #returns the list of the ports connected
 
        
        # seeks out the Arduino and what port it is connected to
        def findArduino(portsFound):
            commPort = 'None' #when nothing is connected/it can't find it
            numConnection = len(portsFound) #returns the length of the list from that is returned from the get_ports function
 
            #iterates through the list of ports
            for i in range(0, numConnection):
                port = foundPorts[i] #finds the port
                strPort = str(port) #converts that port to a string
 
                # the term Arduino can be used to identify what port it is at
                if 'Arduino' in strPort:
                    splitPort = strPort.split(' ') #split the string by spaces 
                    commPort = (splitPort[0]) #returns what comport it is in
 
            return commPort
        
        val = self.togglebuttonStart.GetValue()
        foundPorts = get_ports()  
        connectPort = findArduino(foundPorts)
 
        if (val == True):
            self.togglebuttonStart.SetLabel("Stop") # when the button is pressed
            self.timer.Start(int(self.textboxSampleTime.GetValue())) # in milliseconds
        else:
            self.togglebuttonStart.SetLabel("Start") # when the button is unpressed
            self.timer.Stop()
    
 
        # getting the arduino to work with the code
        if (self.serial_connection == False):
            try:
                # connecting the arduino to the code
                addr = "34:86:5D:FD:D8:1A"
                self.serial_arduino = bluetooth.BluetoothSocket(bluetooth.RFCOMM) # have the axes the '/dev/cu.usbmodem1411301' to what ever the Arduino is connected to on that specific machine
                self.serial_arduino.connect((addr, 1))  
                self.serial_connection = True
            except bluetooth.BluetoothError as e:
                print("Problem connecting to Arduino")
 
        
class Main(wx.Frame):
    def __init__(self): #constructor
        wx.Frame.__init__(self, parent = None, title = "Arudino Data", size =(600,700)) #laying out the frame of the application
 
        # define spiltter and two panels
        splitter = wx.SplitterWindow(self)
        top  = TopPanel(splitter) # top panel
        bottom = BottomPanel(splitter, top) # bottom panel
        splitter.SplitHorizontally(top, bottom) # save the splitter and split top and bottom panels
        splitter.SetMinimumPaneSize(500) # minimum pane size, try to reszie the window will still make the pane 100 pixels
        top.draw(0,0) # start from 0
 
if __name__ == "__main__":
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop() # handle events and make sure the program doesn't just stop
 

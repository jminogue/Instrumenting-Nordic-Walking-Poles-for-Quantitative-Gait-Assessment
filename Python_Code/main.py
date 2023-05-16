import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import csv #import CSV capabilities
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
        # Transpose the data arrays
        x_data = self.x.reshape(-1, 1)
        y_data = self.y.reshape(-1, 1)

        Theader = ["Time[ms]"]
        Pheader = ["Force[kg]"]

        with open("data.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(Theader + Pheader)  # Write header row

            # Write the data in columns
            for x, y in zip(x_data, y_data):
                writer.writerow([x[0], y[0]])

        print("File saved!")
 
        
        
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

    # getting the bluetooth readings from the Arduino
    def TimeInterval(self, event):
        data = self.serial_arduino.recv(1044).decode('utf-8').rstrip()

        # Split the received data by lines
        lines = data.split('\r\n')

        for line in lines:
            # Skip empty lines
            if not line:
                continue

            # Split the line by tabs
            values = line.split('\t')

            # Check if the line contains the expected number of values
            if len(values) != 2:
                # Handle incomplete or malformed data
                print(f"Ignoring malformed data: {line}")
                continue

            # Extract the values
            tmpx = values[0]
            tmpy = values[1]

            try:
                self.y = np.append(self.y, float(tmpy))
                self.x = np.append(self.x, float(tmpx))
                self.x_counter += 1  # increment it so it lines up with x and y

                self.graph.draw(self.x, self.y)
            except ValueError:
                print(f"Error converting data: {line}")

        
    # What happens when the "Start" button is pressed on the interface
    def OnStartClick(self, event):
        
        # Toggle start/stop button (If you press "start", the button now changes to say "stop")
        val = self.togglebuttonStart.GetValue()
        if (val == True):
            self.togglebuttonStart.SetLabel("Stop") # when the button is pressed
            self.timer.Start(int(self.textboxSampleTime.GetValue())) # in milliseconds
        else:
            self.togglebuttonStart.SetLabel("Start") # when the button is unpressed
            self.timer.Stop()

        # Connecting to bluetooth arduino
        if (self.serial_connection == False):
            addr = "34:86:5D:FD:D8:1A"
            self.serial_arduino = bluetooth.BluetoothSocket(bluetooth.RFCOMM) 
            self.serial_arduino.connect((addr, 1))  
            self.serial_connection = True
            print("Arduino Connected!")
            if bluetooth.BluetoothError:
                print()
 
 
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
 

import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import bluetooth
import csv
import sys
from io import StringIO


class TopPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.axes.set_xlabel('Time [sec]')
        self.axes.set_ylabel('Force [kg]')

        self.x = np.array([])
        self.y = np.array([])

    def draw(self):
        self.axes.clear()
        self.axes.plot(self.x, self.y, '-o')
        self.axes.set_xlabel('Time [sec]')
        self.axes.set_ylabel('Force [lbs]')
        self.canvas.draw()


class BottomPanel(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent=parent)
        self.graph = top

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimeInterval, self.timer)

        self.x = np.array([])
        self.y = np.array([])

        walking_pole_address = self.find_walking_pole()
        self.bluetooth_socket = self.connect_to_walking_pole(walking_pole_address)

        self.togglebuttonStart = wx.ToggleButton(self, id=-1, label="Start")
        self.buttonSave = wx.Button(self, -1, "Save to CSV")
        self.buttonClear = wx.Button(self, -1, "Clear Data")
        self.textCtrl = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 100))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.togglebuttonStart, 0, wx.ALL, 5)
        button_sizer.Add(self.buttonSave, 0, wx.ALL, 5)
        button_sizer.Add(self.buttonClear, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(button_sizer, 0, wx.CENTER)
        main_sizer.Add(self.textCtrl, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(main_sizer)

        self.data_cleared = False
        self.timer_running = False

        self.togglebuttonStart.Bind(wx.EVT_TOGGLEBUTTON, self.OnStartClick)
        self.buttonSave.Bind(wx.EVT_BUTTON, self.OnSave)
        self.buttonClear.Bind(wx.EVT_BUTTON, self.OnClear)

    def find_walking_pole(self):
        nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
        for addr, name in nearby_devices:
            if "Walking_Pole" in name:
                print(f"\nBluetooth Walking Pole Found at {addr}\n")
                return addr
        print("Bluetooth Walking Pole Not Found.\n Make sure you ran the Arduino Bluetooth code first\n")
        return None

    def connect_to_walking_pole(self, address):
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((address, 1))
            print(f"Connected to Walking Pole at {address}\n")
            return sock
        except Exception as e:
            print(f"Error connecting to Walking Pole: {e}\n")
            return None

    def print_to_text_ctrl(self, message):
        sys.stdout = StringIO()
        print(message)
        sys.stdout.seek(0)

        existing_content = self.textCtrl.GetValue()
        self.textCtrl.SetValue(existing_content + sys.stdout.read())

        sys.stdout = sys.__stdout__

    def TimeInterval(self, event):
        if self.bluetooth_socket:
            buffer = ""
            data = self.bluetooth_socket.recv(1024).decode('utf-8')
            buffer += data

            if '\n' in buffer:
                lines = buffer.split('\n')
                for line in lines[:-1]:
                    values = line.split(',')
                    if len(values) == 2:
                        tmpx, tmpy = map(float, values)
                        try:
                            self.y = np.append(self.y, tmpy)
                            self.x = np.append(self.x, tmpx)
                            self.graph.x = self.x
                            self.graph.y = self.y
                            self.graph.draw()
                        except ValueError:
                            self.print_to_text_ctrl(f"Error converting data: {line}\n")

    def OnStartClick(self, event):
        if self.data_cleared:
            walking_pole_address = self.find_walking_pole()
            self.bluetooth_socket = self.connect_to_walking_pole(walking_pole_address)
            self.data_cleared = False

        val = self.togglebuttonStart.GetValue()
        if val:
            self.togglebuttonStart.SetLabel("Stop")
            self.timer.Start(200)
            self.timer_running = True
        else:
            self.togglebuttonStart.SetLabel("Start")
            self.buttonSave.Enable()
            self.timer.Stop()
            self.timer_running = False

            if self.bluetooth_socket:
                self.bluetooth_socket.close()

    def OnSave(self, event):
        x_data = self.x.reshape(-1, 1)
        y_data = self.y.reshape(-1, 1)

        header = ["Time", "Force"]

        with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            filepath = fileDialog.GetPath()
            with open(filepath, "w", newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)

                for x, y in zip(x_data, y_data):
                    writer.writerow([x[0], y[0]])

            self.print_to_text_ctrl(f"File saved: {filepath}\n")

    def OnClear(self, event):
        self.x = np.array([])
        self.y = np.array([])
        self.graph.x = self.x
        self.graph.y = self.y
        self.graph.draw()
        self.print_to_text_ctrl("Data Cleared\n")

        if self.bluetooth_socket:
            self.bluetooth_socket.close()
        self.bluetooth_socket = None

        self.data_cleared = True
        self.togglebuttonStart.Enable()
        self.buttonSave.Disable()


class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Walking Pole Data", size=(600, 700))

        splitter = wx.SplitterWindow(self)
        top = TopPanel(splitter)
        bottom = BottomPanel(splitter, top)
        splitter.SplitHorizontally(top, bottom)
        splitter.SetMinimumPaneSize(500)
        top.draw()


if __name__ == "__main__":
    print("\nInitializing...\n")
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()

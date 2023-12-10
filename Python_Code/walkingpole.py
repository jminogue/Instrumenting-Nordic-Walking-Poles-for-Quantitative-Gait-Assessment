
import bluetooth
import pandas as pd
import matplotlib.pyplot as plt

def find_walking_pole():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    for addr, name in nearby_devices:
        if "Walking_Pole" in name:
            print(f"\nBluetooth Walking Pole Found at {addr}\n")
            return addr
    print("Bluetooth Walking Pole Not Found.\n Make sure you ran the Arduino Bluetooth code first\n")
    return None


def connect_to_walking_pole(address):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((address, 1))  # The second parameter is the Bluetooth port (RFCOMM channel) on the ESP32
        print(f"Connected to Walking Pole at {address}")
        return sock
    except Exception as e:
        print(f"Error connecting to Walking Pole: {e}")
        return None

columns = ['Time', 'Force']
df = pd.DataFrame(columns=columns)

Walking_Pole_MAC_address = find_walking_pole()

if Walking_Pole_MAC_address:
    bluetooth_socket = connect_to_walking_pole(Walking_Pole_MAC_address)
    if bluetooth_socket:
        try:
            buffer = ""
            while True:
                data = bluetooth_socket.recv(1024).decode('utf-8')  # Adjust the buffer size as needed
                if not data:
                    break

                # Append the received data to the buffer
                buffer += data

                # Check if the buffer contains a complete reading
                if '\n' in buffer:
                    # Split the buffer into lines and process each complete reading
                    lines = buffer.split('\n')
                    for line in lines[:-1]:
                        # Split the line into values and filter out invalid formats
                        values = line.split(',')
                        if len(values) == 2:
                            time = float(values[0])
                            force = float(values[1].strip())
                            df = df._append({'Time': time, 'Force': force}, ignore_index=True)
                            print(f"Time {time} sec, Force: {force} lbs")
                        else:
                            print("Invalid Data Point")

                    # Update the buffer with any remaining data
                    buffer = lines[-1]
        except KeyboardInterrupt:
            print("Data Collection Stopped.")
        finally:
            bluetooth_socket.close()
else:
    print("Unable to connect to Walking Pole.")

csv_filename = 'walking_pole_data.csv'
df.to_csv(csv_filename, index=False)

plt.plot(df['Time'], df['Force'])
plt.title("Walking Pole Force")
plt.xlabel('Time [sec]')
plt.ylabel('Force [kg]')
png_filename = 'walking_pole_plot.png'
plt.savefig(png_filename)
plt.show()

print(f"\nData saved to {csv_filename}\n")
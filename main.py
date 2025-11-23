import tkinter as tk
from tkinter import messagebox
import csv
import datetime
import paho.mqtt.client as mqtt

# MQTT Setup
BROKER = "broker.hivemq.com"
EVENT_TOPIC = "ids/events"
ALERT_TOPIC = "ids/alerts"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# Allowed credentials
users = {
"admin1": {"password": "1234", "role": "admin"},
"musab": {"password": "pass", "role": "guest"},
}

restricted_zones = ["Storage Room", "Back Door"]

# GUI Application
class IDSApp:
def __init__(self, root):
self.root = root
self.root.title("IDS Simulation - MQTT Enhanced")

self.username = tk.StringVar()
self.password = tk.StringVar()

self.login_screen()

# ------------------- Authentication -----------------------
def login_screen(self):
for widget in self.root.winfo_children():
widget.destroy()

tk.Label(self.root, text="Login", font=("Arial", 16)).pack(pady=10)

tk.Label(self.root, text="Username").pack()
tk.Entry(self.root, textvariable=self.username).pack()

tk.Label(self.root, text="Password").pack()
tk.Entry(self.root, textvariable=self.password, show="*").pack()

tk.Button(self.root, text="Login", command=self.validate_login).pack(pady=10)

def validate_login(self):
user = self.username.get().lower()
pw = self.password.get()

if user in users and users[user]["password"] == pw:
self.role = users[user]["role"]
messagebox.showinfo("Success", "Login successful")
self.dashboard()
else:
messagebox.showerror("Error", "Invalid username or password")

# ------------------- Dashboard -----------------------
def dashboard(self):
for widget in self.root.winfo_children():
widget.destroy()

tk.Label(self.root, text=f"Dashboard ({self.role})", font=("Arial", 16)).pack(pady=10)

zones = ["Main Door", "Storage Room", "Hallway", "Window 1", "Back Door"]

for z in zones:
tk.Button(self.root, text=z, width=20, command=lambda zone=z: self.handle_zone(zone)).pack(pady=5)

self.log_box = tk.Text(self.root, height=15, width=60)
self.log_box.pack(pady=10)

tk.Button(self.root, text="Export CSV", command=self.export_csv).pack()
tk.Button(self.root, text="Logout", command=self.login_screen).pack(pady=5)

# ------------------- Event Handling -----------------------
def handle_zone(self, zone):
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
hour = datetime.datetime.now().hour

# Determine event type
if self.role == "guest" and zone in restricted_zones:
status = "UNAUTHORISED"
elif hour < 8 or hour > 20:
status = "AFTER_HOURS"
else:
status = "AUTHORISED"

message = f"{now}, {self.username.get()}, {zone}, {status}"

# MQTT publishing
if status in ["UNAUTHORISED", "AFTER_HOURS"]:
client.publish(ALERT_TOPIC, message)
else:
client.publish(EVENT_TOPIC, message)

# Logging
self.log_event(message)
self.log_box.insert(tk.END, message + "\n")
self.log_box.see(tk.END)

# ------------------- Logging -----------------------
def log_event(self, message):
with open("intrusion_log.txt", "a") as file:
file.write(message + "\n")

with open("intrusion_log_report.csv", "a", newline="") as csvfile:
writer = csv.writer(csvfile)
writer.writerow(message.split(", "))

def export_csv(self):
messagebox.showinfo("Export", "CSV exported successfully")


# ------------------- Run App -----------------------
root = tk.Tk()
app = IDSApp(root)
root.mainloop()

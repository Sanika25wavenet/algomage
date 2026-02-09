import urllib.request

try:
    with urllib.request.urlopen('https://api.ipify.org') as response:
        ip = response.read().decode('utf-8')
        print(f"Your Public IP is: {ip}")
except Exception as e:
    print(f"Could not get IP: {e}")

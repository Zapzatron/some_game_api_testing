import requests

url = "http://127.0.0.35:8000/export_csv/"
response = requests.get(url)

with open('data.csv', 'wb') as file:
    file.write(response.content)

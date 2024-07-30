import requests

url = "http://127.0.0.35:8000/assign_prize/"
data = {
    "player_id": 1,
    "level_id": 1,
    "prize_id": 1
}

response = requests.post(url, json=data)
print(response.json())

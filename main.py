from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"

    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with name exists...")
        return None
    return json_result[0]

def get_songs_by_atrist(token,artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=KZ"
    headers = get_auth_header(token)
    result = get(url,headers = headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


token = get_token()
#artist_name = input("Write Artist Name: ")
#result = search_for_artist(token,artist_name)
#artist_id = result["id"]
#songs = get_songs_by_atrist(token,artist_id)
#for idx,song  in enumerate(songs):
#   print(f"{idx + 1}. {song['name']}")

def get_artist_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    if len(json_result) == 0:
        print("No albums found for this artist.")
        return None

    albums = []
    for album in json_result:
        albums.append({
            "name": album["name"],
            "id": album["id"]
        })
    return json_result

search_for_artist(token, 'juice wrld')


'''
albums = get_artist_albums(token, artist_id)
print(f"Albums by {artist_name}:")
for idx,albums  in enumerate(albums):
   print(f"{idx + 1}. {albums['name']}")
   '''
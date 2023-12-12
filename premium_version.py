from tkinter import *
from tkinter import messagebox
from main import get_token, search_for_artist, get_songs_by_atrist, get_artist_albums
from PIL import Image, ImageTk
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pygame
from io import BytesIO
import psycopg2

logged_in_username = ""
current_artist_name = ""
current_artist_image_url = ""
genres = ""
artist_name  = ""
current_artist_id = ""
album_count = None
label_artist = None
label_info = None
label_info_albums = None
label_info_tracks = None
selected_track_name = ""
track_labels = []
db_params = {
    'host': 'localhost',
    'database': 'Spotify',
    'user': 'postgres',
    'password': '123',
}



def add_to_favorites_song():
    global selected_track_name, current_artist_name, db_params, artist_name, username

    if selected_track_name and artist_name and username:
        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()
            username = username.split()
            username ='_'.join(username)
            create_table_query = f"CREATE TABLE IF NOT EXISTS {username.lower()}_favorites (id SERIAL PRIMARY KEY, track_name VARCHAR(255) NOT NULL, artist_name VARCHAR(255) NOT NULL);"
            cursor.execute(create_table_query)

            insert_query = f"INSERT INTO {username.lower()}_favorites (track_name, artist_name) VALUES (%s, %s);"
            cursor.execute(insert_query, (selected_track_name, artist_name))

            connection.commit()
            print("Record added to the favorites.")

        except Exception as e:
            print(f"Error adding record to favorites: {e}")

        finally:
            if connection:
                connection.close()

    else:
        print("Track, artist, or username information is missing.")

def add_to_favorites_album():
    pass

def save_and_search():
    
    label_no_artist.config(text = "")
    global current_artist_name, current_artist_image_url, genres, current_artist_id, label_artist, label_info_albums, label_info_tracks, artist_name
    global root, frame, entry,magnifying_glass_icon,magnifying_glass_button,label_result,image_label
    if not label_info_albums:
        label_info_albums = Label(root, fg="white", bg="grey16", font=("Circular", 12), justify=LEFT)

    label_info_albums.config(text="")
    current_artist_name = entry.get()
    print(f"Searching for artist: {current_artist_name}")
    result = search_for_artist(token, current_artist_name)
    if result:
        current_artist_image_url = result['images'][0]['url']
        update_artist_image()
        current_artist_id = result['id']
        genres = ", ".join(result['genres'])
        artist_name = result['name']
        label_artist.config(text=f"{result['name']}")
        top_tracks_button = Button(root, text="Показать топ-10 треков", command=show_top_tracks)
        top_tracks_button.place(x=250, y=150)
        label_info = Label(root, fg="white", bg="grey16", font=("Circular", 12), justify=LEFT)
        label_info.place(x=30, y=400, anchor="w")

        label_info_albums = Label(root, fg="white", bg="grey16", font=("Circular", 12), justify=LEFT)
        
        albums_button = Button(root, text="Показать альбомы", command=show_artist_albums)
        albums_button.place(x=250, y=190)
    else:
        label_no_artist.config(text="Исполнитель не найден.")


def update_artist_image():
    if current_artist_image_url:
        image = Image.open(requests.get(current_artist_image_url, stream=True).raw)
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        artist_image = ImageTk.PhotoImage(image)
        image_label.config(image=artist_image)
        image_label.image = artist_image


def show_artist_albums():
    global label_info_album, album_count, track_labels

    label_info_albums.config(text="")

    if current_artist_id:
        albums = get_artist_albums(token, current_artist_id)
        if albums:

            label_info_albums.config(text="")
            album_count = len(albums)
            print(album_count)
            label_info_albums.place(x=30, y=album_count * 10 + 280, anchor="w")

            for album in albums:
                album_text = label_info_albums.cget("text") + album['name'] + '\n'
                label_info_albums.config(text=album_text)

            hide_track_labels()

        else:
            label_result.config(text="Альбомы не найдены.")
    else:
        label_result.config(text="Сначала выполните поиск исполнителя.")



def show_top_tracks():
    global root, frame, entry,magnifying_glass_icon,magnifying_glass_button,label_no_artist,label_result,image_label
    global label_info_albums, selected_track_name, track_labels
    label_info_albums.config(text="")

    if current_artist_name:
        result = search_for_artist(token, current_artist_name)
        if result:
            artist_id = result["id"]
            songs = get_songs_by_atrist(token, artist_id)
            hide_track_labels()

            track_labels = [] 

            for song in songs:
                track_name = song['name']
                track_label = Label(root, text=track_name, fg="white", bg="grey16", font=("Circular", 12), justify=LEFT)
                track_labels.append(track_label)  
                
                track_label.bind("<Button-3>", lambda event, track=track_name: show_context_menu(event, track))
                track_label.pack(padx =  30, anchor="w")

    else:
        label_result.config(text="Сначала выполните поиск исполнителя.")

def hide_track_labels():
    global track_labels
    for track_label in track_labels:
        track_label.pack_forget()

def show_context_menu(event, track_name):
    global selected_track_name
    selected_track_name = track_name
    
    context_menu = Menu(root, tearoff=0)
    context_menu.add_command(label="Добавить в избранное", command=add_to_favorites_song)
    context_menu.post(event.x_root, event.y_root)



token = get_token()

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id='dee749ef1b204a4aa86561f368d17d1d', client_secret='8923cb22c58745dca2e80e29b9fada86'))

def authenticate_user(username, password):

    hardcoded_username = "miko"
    hardcoded_password = "tanir"

    return username == hardcoded_username and password == hardcoded_password

def authenticate_user(username, password):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        select_query = "SELECT * FROM users WHERE username = %s AND password = %s;"
        cursor.execute(select_query, (username, password))
        user = cursor.fetchone()

        connection.close()

        return user is not None

    except Exception as e:
        print(f"Error authenticating user: {e}")
        return False

    finally:
        if connection:
            connection.close()

def login():
    global entry_username, entry_password, label_no_artist, root, username

    username = entry_username.get()
    password = entry_password.get()

    if authenticate_user(username, password):
        label_no_artist.config(text="")
        root.destroy()  
        open_main_window()
    else:

        label_no_artist.config(text="Invalid username or password")
        messagebox.showerror("Login Failed", "Invalid username or password")

def register(username, password):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Check if the username already exists
        check_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            label_no_artist.config(text="Username already exists. Please choose another username.")
        else:
            insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, password))

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS "{username}_favorites" (
                id SERIAL PRIMARY KEY,
                track_name VARCHAR(255),
                artist_name VARCHAR(255)
            );
            """
            cursor.execute(create_table_query)

            connection.commit()
            print("Registration successful.")

    except Exception as e:
        print(f"Error during registration: {e}")

    finally:
        if connection:
            connection.close()

def open_login_window():
    global root, entry_username, entry_password, label_no_artist

    root = Tk()
    root.title("Login")
    root.geometry("960x709")

    canvas = Canvas(root, width=960, height=709)
    canvas.pack()

    login_frame = Frame(root, bg="black")
    login_frame.place(relx=0.2, rely=0.8, anchor="w")

    image = PhotoImage(file="spotify_login.png")
    canvas.create_image(0, 0, image=image, anchor="nw")

    label_username = Label(login_frame, text="Username:", fg="white", bg="black", font=("Circular", 20, 'bold'))
    label_username.grid(row=0, column=0, pady=10, padx=10, sticky="e")

    entry_username = Entry(login_frame, bg="white", font=("Circular", 20, 'bold'))
    entry_username.grid(row=0, column=1, pady=10, padx=50, sticky="w")

    label_password = Label(login_frame, text="Password:", fg="white", bg="black", font=("Circular", 20, 'bold'))
    label_password.grid(row=1, column=0, pady=10, padx=10, sticky="e")

    entry_password = Entry(login_frame, show="*", bg="white", font=("Circular", 20, 'bold'))
    entry_password.grid(row=1, column=1, pady=10, padx=50, sticky="w")

    sign_in_button = Button(login_frame, text="Sign in", command=login, bg="green", fg="white", font=("Circular", 20, 'bold'))
    sign_in_button.grid(row=2, column=0, pady=10, padx=(30, 15))

    sign_up_button = Button(login_frame, text="Sign up", command=lambda: register(entry_username.get(), entry_password.get()), bg="green", fg="white", font=("Circular", 20, 'bold'))
    sign_up_button.grid(row=2, column=1, pady=10, padx=(40, 100))

    label_no_artist = Label(login_frame, text="", fg="red", bg="black", font=("Circular", 13, 'bold'))
    label_no_artist.grid(row=3, column=0, columnspan=2, pady=10)

    root.mainloop()


def get_user_favorites(username):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        username = username.split()
        username ='_'.join(username)
        query = f"SELECT id, track_name, artist_name FROM {username}_favorites"
        cursor.execute(query, (username,))
        favorites = cursor.fetchall()
        return favorites
        
    except Exception as e:
        print(f"Error retrieving favorites: {e}")
        return []

    finally:
        if connection:
            connection.close()


def open_favorites_window():
    global username  

    root_favorites = Tk()
    root_favorites.title(f"{username}'s Favorites")
    root_favorites.geometry("600x400")
    root_favorites.config(bg="grey16")  

    label_favorites = Label(root_favorites, text="Your Favorite Songs", font=("Circular", 16, 'bold'), bg="grey16", fg="white")
    label_favorites.pack(pady=10)

    favorites = get_user_favorites(username)
    if favorites:
        for favorite in favorites:
            
            label_favorite = Label(root_favorites, text=f"{favorite[0]}.  {favorite[1]} by {favorite[2]}", font=("Circular", 12), bg="grey16", fg="white")
            label_favorite.pack(anchor="w", padx=20, pady=5)
    else:
        label_no_favorites = Label(root_favorites, text="No favorite songs yet.", font=("Circular", 12), bg="grey16", fg="white")
        label_no_favorites.pack(pady=20)

    root_favorites.mainloop()
    
def open_main_window():
    global root, frame, entry,magnifying_glass_icon,magnifying_glass_button,label_no_artist,label_result,image_label,label_artist
    root = Tk()
    root.title("Welcome to Spotify!")
    root.geometry("960x709")
    root.resizable(False, True)
    icon = PhotoImage(file="Spotify.png")
    root.iconphoto(False, icon)
    root.config(bg="grey16")
    
    frame = Frame(root, bg="grey16")
    frame.pack(pady=20, padx=20, anchor='w')

    favorite_button_icon = PhotoImage(file="favorite_button.png").subsample(7, 7)
    favorites_button = Button(frame, image=favorite_button_icon, command=open_favorites_window, bg="grey16", bd=0)
    favorites_button.image = favorite_button_icon 
    favorites_button.grid(row=0, column=2)


    entry = Entry(frame, font=("Circular", 14), bg="white", fg="black", width=30)
    entry.grid(row=0, column=0)

    magnifying_glass_icon = PhotoImage(file="lupa.png").subsample(45, 45)

    magnifying_glass_button = Button(frame, image=magnifying_glass_icon, command=save_and_search)
    magnifying_glass_button.grid(row=0, column=1, padx=10)

    image_label = Label(root, bg="grey16")
    image_label.pack(ipadx=30, ipady=10, anchor="w")

    label_artist = Label(root, text="", fg="white", bg='grey16', font=("Circular", 20, 'bold'), anchor="w")
    label_artist.place(x=250, y=80)

    label_no_artist = Label(root, text="", fg="white", bg='grey16', font=("Circular", 12, 'bold'), anchor="w")
    label_no_artist.place(x=30, y=80)

    label_result = Label(root, text="", fg="white", bg="grey16", font=("Circular", 12), justify=LEFT)
    label_result.place(x=30, y=250)

    root.mainloop()

open_login_window()
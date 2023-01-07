import requests
import sqlite3
import json
from urllib.parse import urlencode
from datetime import datetime

client_id = "azarhadbl7fdust63xxwznv27ejc3n"
token = ""

def init_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS completions (game_id INTEGER PRIMARY KEY, completion_date DATE, rating INTEGER)")
    conn.commit()
    conn.close()

def init_api():
    session = requests.Session()

    url = "https://id.twitch.tv/oauth2/token"

    params = {
        "client_id": client_id,
        "client_secret": "uf69goclkqsegtd2j9qwl7g5xztg9s",
        "grant_type": "client_credentials"
    }

    # Encode the query parameters as a string
    query_string = urlencode(params)

    # Build the request object with the POST method and the encoded query string
    request = requests.Request('POST', f"{url}?{query_string}")

    # Send the request
    response = session.send(request.prepare())
    if response.ok:
        global token
        token = json.loads(response.text).get("access_token")
    return response.ok

def main_menu():
    menu = "\n\n\n\nWelcome to \033[1;35;49mGamingNexus!\033[0m\033[0m\n\n"
    menu += "[\033[1;32;49m1\033[0m] \033[34;49mSearch for games\033[0m\n"
    menu += "[\033[1;32;49m2\033[0m] \033[34;49mMy completed games\033[0m\n"
    menu += "[\033[1;32;49m3\033[0m] \033[31;49mExit\033[0m\n"
    
    while True:
        print(menu)
        command_input = input("> ") # Get the user input

        if not command_input: # If the user
            continue

        if command_input == "1":
            search_menu()
        elif command_input == "2":
            pass
        elif command_input == "3":
            print("\n\n\n\n\033[1;31;49mExiting...\033[0m\n\n\n\n")
            break
        else:
            print("\n\n\n\n\033[1;33;49mInvalid command\033[0m")

def get_completion(game_id, conn=None, cursor=None):
    # If the connection and cursor are not specified, create them
    need_to_close = False
    if not conn:
        need_to_close = True
        conn = sqlite3.connect("database.db")
    if not cursor:
        cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM completions WHERE game_id = ?", (game_id,))
    completion = cursor.fetchone()
    
    # If the connection and cursor were not specified, close them
    if need_to_close:
        conn.close()

    return completion

def show_games(games):
    print(f"\n\n\033[36;49m{len(games)}\033[0m games found:\n")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    enumerated_games = enumerate(games)
    for i, game in enumerated_games:
            id = game["id"]
            name = game["name"]
            year = datetime.fromtimestamp(game["first_release_date"]).strftime("%Y")

            completion = get_completion(id, conn, cursor)
            if completion:
                print(f"[\033[1;32;49m{i + 1}\033[0m] \033[34;49m{name}\033[0m \033[36;49m({year})\033[0m \033[32;49m[Completed on\033[0m \033[1;33;49m{completion[1]}\033[0m\033[32;49m | Rating:\033[0m \033[1;33;49m{completion[2]}\033[0m\033[32;49m]\033[0m")
            else:
                print(f"[\033[1;32;49m{i + 1}\033[0m] \033[34;49m{name}\033[0m \033[36;49m({year})\033[0m")
    conn.close()

def update_menu(game):
    id = game["id"]
    name = game["name"]
    year = datetime.fromtimestamp(game["first_release_date"]).strftime("%Y")
    completion = get_completion(id)
    if completion:
        print(f"\n\n\n\n\033[34;49m{name}\033[0m \033[36;49m({year})\033[0m \033[32;49m[Completed on\033[0m \033[1;33;49m{completion[1]}\033[0m\033[32;49m | Rating:\033[0m \033[1;33;49m{completion[2]}\033[0m\033[32;49m]\033[0m\n")
    else:
        print(f"\n\n\n\n\033[34;49m{name}\033[0m \033[36;49m({year})\033[0m\n")
    options = "[\033[1;32;49m1\033[0m] \033[32;49mMark\033[0m \033[34;49mas completed\033[0m\n"
    options += "[\033[1;32;49m2\033[0m] \033[31;49mUnmark\033[0m \033[34;49mas completed\033[0m\n\n> "
    command_input = input(options)
    if command_input and command_input.isnumeric() and 1 <= int(command_input) <= 2:
        if command_input == "1":
            update_completion(id)
        elif command_input == "2":
            delete_completion(id)

def update_completion(game_id):
    valid_input = False
    date_input = ""
    rating_input = ""
    while not valid_input:
        date_input = input("\nEnter the \033[36;49mcompletion date\033[0m \033[33;49m(DD/MM/YYYY)\033[0m: \n> ")
        rating_input = input("\nEnter the \033[36;49mrating\033[0m \033[33;49m(1-10)\033[0m: \n> ")
        try:
            date = datetime.strptime(date_input, "%d/%m/%Y")
        except ValueError:
            print("\n\033[33;49mInvalid date format\033[0m\n")
            continue
        else:
            # If rating input is empty or not a number or not between 1 and 10
            if not rating_input or not rating_input.isnumeric() or not 1 <= int(rating_input) <= 10:
                print("\n\033[33;49mInvalid rating\033[0m\n")
                continue
            else:
                valid_input = True
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Execute an insert or update depending on if the game is already marked as completed
    if get_completion(game_id, conn, cursor):
        cursor.execute("UPDATE completions SET date = ?, rating = ? WHERE game_id = ?", (date_input, rating_input, game_id))
    else:
        cursor.execute("INSERT INTO completions VALUES (?, ?, ?)", (game_id, date_input, rating_input))
    conn.commit()
    conn.close()
    print("\n\n\n\nGame \033[32;49mmarked as completed\033[0m")

def delete_completion(game_id):
    if get_completion(game_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM completions WHERE game_id = ?", (game_id,))
        conn.commit()
        conn.close()
        print("\n\n\n\nGame \033[31;49munmarked\033[0m as completed")

def search_menu():
    command_input = input("\n\n\n\nEnter a \033[36;49mgame name\033[0m to search: \n> ") # Get the user input
    if command_input:
        games = search_games(command_input) # Search for games with the specified name
        if games: # If games were found, show them
            show_games(games)
            command_input = input("\n\033[36;49mSelect a game\033[0m to update its information: \n> ")
            # If there is a game selected and it is a valid number between 1 and the number of games
            if command_input and command_input.isnumeric() and 1 <= int(command_input) <= len(games):
                update_menu(games[int(command_input) - 1])
        else: # If no games were found, show a message
            print("\n\n\n\n\033[33;49mNo games found\033[0m")
    
def search_games(search_query):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}"
    }
    data = f"""
    search "{search_query}";
    fields id,name,first_release_date;
    where first_release_date != null;
    """ # The query to send to the API
    
    response = requests.post(url, headers=headers, data=data)
    if response.ok:
        return json.loads(response.text) # Return the list of games

def main():
    init_database() # Initialize the database
    authenticated = init_api() # Authenticate with the API
    if authenticated:
        main_menu() # Enter the menu
    else:
        print("Authentication error") # Authentication failed

if __name__ == "__main__":
    main()
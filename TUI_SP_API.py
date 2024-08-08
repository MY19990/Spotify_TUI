import curses
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import logging

# ログの設定
logging.basicConfig(filename='spotify_player.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SpotipyのOAuthクライアント
sp_oauth = SpotifyOAuth(client_id="19088d0df1a0425ca1d0d1118a2554d0",
                        client_secret="e735cdb40c2b490db3eefd32d14346d3",
                        redirect_uri="http://localhost:8888/callback",
                        scope="user-library-read user-read-playback-state user-modify-playback-state")

def get_spotify_token():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        logging.info(f"Please go to this URL to authorize: {auth_url}")
        auth_response = input('Paste the above link into your browser, and then paste the URL you were redirected to here: ')
        token_info = sp_oauth.get_access_token(auth_response)
    return token_info['access_token']

def create_spotipy_instance():
    token = get_spotify_token()
    return spotipy.Spotify(auth=token)

def toggle_playback():
    try:
        sp = create_spotipy_instance()
        current_status = sp.current_playback()
        
        if current_status and current_status["is_playing"]:
            sp.pause_playback()
            logging.info("Playback paused.")
        else:
            sp.start_playback()
            logging.info("Playback resumed.")
    except SpotifyException as e:
        logging.error(f"Spotify API Error: {e}")

def next_track():
    try:
        sp = create_spotipy_instance()
        sp.next_track()
        
        logging.info("Next track.")
    except SpotifyException as e:
        logging.error(f"Spotify API Error: {e}")

def prev_track():
    try:
        sp = create_spotipy_instance()
        sp.previous_track()
        logging.info("Previous track.")
    except SpotifyException as e:
        logging.error(f"Spotify API Error: {e}")

def main(stdscr):
    # cursesの初期設定
    curses.curs_set(0)
    stdscr.clear()

    # 画面サイズ取得
    height, width = stdscr.getmaxyx()

    # ボタンの表示テキストと位置
    buttons = [
        {"text": "Prev Track (Left Arrow)", "function": prev_track, "key": curses.KEY_LEFT},
        {"text": "Toggle Playback (Enter/Space)", "function": toggle_playback, "key": 10},  # Enterキー
        {"text": "Next Track (Right Arrow)", "function": next_track, "key": curses.KEY_RIGHT},
    ]

    # ボタンを配置
    button_height = 3
    button_width = max(len(button["text"]) + 4 for button in buttons)
    button_spacing = 2

    total_width = button_width * len(buttons) + button_spacing * (len(buttons) - 1)
    start_x = (width - total_width) // 2

    for i, button in enumerate(buttons):
        button_y = (height - button_height) // 2
        button_x = start_x + i * (button_width + button_spacing)

        stdscr.addstr(button_y, button_x, "+" + "-" * (button_width - 2) + "+")
        stdscr.addstr(button_y + 1, button_x, "|" + button["text"].center(button_width - 2) + "|")
        stdscr.addstr(button_y + 2, button_x, "+" + "-" * (button_width - 2) + "+")

    while True:
        key = stdscr.getch()

        # キーに対応した関数を呼び出し
        for button in buttons:
            if "key" in button and key == button["key"]:
                button["function"]()

if __name__ == "__main__":
    logging.info("Starting Spotify Player.")
    curses.wrapper(main)

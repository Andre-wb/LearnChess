import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from dotenv import load_dotenv
import threading
import time
import json
import chess

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
LICHESS_API_KEY = os.getenv("LICHESS_API_KEY")
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_TOKEN')

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


def create_open_challenge():
    headers = {
        "Authorization": f"Bearer {LICHESS_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "clock.limit": "300",
        "clock.increment": "30",
        "rated": "false"
    }
    response = requests.post("https://lichess.org/api/challenge/open", headers=headers, data=data)
    try:
        json_response = response.json()
        print("Lichess open challenge response:", json_response)
        return json_response.get("url")
    except Exception as e:
        print("Ошибка при создании open challenge:", e)
        print("Ответ:", response.text)
        return None


def create_ai_challenge():
    headers = {
        "Authorization": f"Bearer {LICHESS_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "level": "8",
        "clock.limit": "600",
        "clock.increment": "5",
        "color": "white"
    }
    response = requests.post("https://lichess.org/api/challenge/ai", headers=headers, data=data)
    try:
        json_response = response.json()
        print("Lichess AI challenge response:", json_response)
        game_id = json_response.get("id")
        return f"https://lichess.org/{game_id}" if game_id else None
    except Exception as e:
        print("Ошибка при создании AI challenge:", e)
        print("Ответ:", response.text)
        return None

def wait_for_game_start(game_id, timeout=60):
    url = f"https://lichess.org/api/challenge/{game_id}"
    headers = {"Authorization": f"Bearer {LICHESS_API_KEY}"}
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "started":
                return True
        time.sleep(2)
    return False

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")


@bot.message_handler(commands=['chess_with_friend'])
def chess_with_friend_handler(message):
    challenge_url = create_open_challenge()
    if not challenge_url:
        bot.send_message(message.chat.id, "❌ Не удалось создать партию.")
        return
    bot.send_message(
        message.chat.id,
        f"🎯 <b>Сыграй с другом!</b>\nПросто отправь ему эту ссылку, и как только он по ней перейдёт — начнётся партия: \n\n<a href=\"{challenge_url}\">{challenge_url}</a>",
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['chess_vs_ai'])
def chess_vs_ai_handler(message):
    challenge_url = create_ai_challenge()
    if not challenge_url:
        bot.send_message(message.chat.id, "❌ Не удалось создать партию с ИИ.")
        return
    bot.send_message(
        message.chat.id,
        f"🤖 <b>Сыграй с сильным ИИ!</b>\nПартия начнётся по ссылке ниже. После каждого хода бот будет комментировать происходящее: \n\n<a href=\"{challenge_url}\">{challenge_url}</a>",
        disable_web_page_preview=True
    )
    game_id = challenge_url.rsplit('/', 1)[-1]
    threading.Thread(target=stream_game_and_comment, args=(game_id, message.chat.id), daemon=True).start()


commented_fens = set()

def comment_move_with_mistral(moves_fen: str) -> str:
    prompt = f"Пиши всегда обычным текстом, без заголовков, без жирного выделения, и прочих эффектов. Ты — профессиональный шахматный комментатор. Ты говоришь только по русски. Ты хорошо знаешь все дебюты, партии. Максимально кратко (10-20 слов), но профессионально и без грамматических ошибок прокомментируй текущую ситуацию на доске:\nFEN: {moves_fen}"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://openrouter.ai",
        "Content-Type": "application/json"
    }
    data = {
        "model": "microsoft/mai-ds-r1:free",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print("Ошибка при обращении к OpenRouter:", e)
        return "🤖 Не удалось получить комментарий от ИИ."


def stream_game_and_comment(game_id, chat_id):
    url = f"https://lichess.org/api/board/game/stream/{game_id}"
    headers = {
        "Authorization": f"Bearer {LICHESS_API_KEY}"
    }
    board = chess.Board()
    try:
        print("Подключаемся к потоку:", url)
        with requests.get(url, headers=headers, stream=True) as response:
            print("Ответ от Lichess:", response.status_code)
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    print("Получено:", decoded)
                    if decoded.startswith('{'):
                        data = json.loads(decoded)
                        if data.get("type") == "gameState" and "moves" in data:
                            board.reset()
                            moves = data["moves"].split()
                            for move in moves:
                                try:
                                    board.push_uci(move)
                                except Exception as e:
                                    print("Невалидный ход:", move, e)
                            fen = board.fen()
                            if fen not in commented_fens:
                                commented_fens.add(fen)
                                bot.send_chat_action(chat_id, "typing")
                                comment = comment_move_with_mistral(fen)
                                bot.send_message(chat_id, f"🎙️ <b>Комментарий:</b> {comment}")
                                time.sleep(2)
    except Exception as e:
        print("Ошибка при стриме партии:", e)


if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
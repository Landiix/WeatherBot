import requests
import telebot
from telebot import types

TOKEN = '8303447653:AAHGL7wr4sHJppxDzqkQetv7bPcaHRz56AA'
WEATHER_API_KEY = 'bd1e0750cb164e1c9f175857251408'

bot = telebot.TeleBot(TOKEN)

CITIES = {
    'Москва': 'Moscow',
    'Санкт-Петербург': 'Saint Petersburg',
    'Новосибирск': 'Novosibirsk',
    'Екатеринбург': 'Yekaterinburg',
    'Казань': 'Kazan',
    'Сочи': 'Sochi',
    'Владивосток': 'Vladivostok',
    'Магнитогорск': 'Magnitogorsk'
}


def get_weather(city_name):
    base_url = "http://api.weatherapi.com/v1/current.json"

    try:
        params = {
            'key': WEATHER_API_KEY,
            'q': city_name,
            'lang': 'ru'
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if 'error' in data:
            print(f"Ошибка API: {data['error']['message']}")
            return None

        current = data['current']
        location = data['location']

        weather_data = {
            'city': location['name'],
            'country': location['country'],
            'temp': current['temp_c'],
            'feels_like': current['feelslike_c'],
            'condition': current['condition']['text'],
            'wind_speed': current['wind_kph'] / 3.6,  # км/ч в м/с
            'wind_dir': current['wind_dir'],
            'pressure': current['pressure_mb'] * 0.750062,  # мбар в мм рт.ст.
            'humidity': current['humidity'],
            'cloud': current['cloud'],
            'is_day': current['is_day'] == 1,
            'icon': current['condition']['icon']
        }
        return weather_data
    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return None


def get_weather_icon(icon_url):
    if 'day' in icon_url:
        return '☀️' if '113' in icon_url else '⛅'
    else:
        return '🌙' if '113' in icon_url else '☁️'


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = [types.KeyboardButton(city) for city in CITIES.keys()]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "Привет! Я бот, который показывает актуальную погоду. Выбери город:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in CITIES.keys())
def send_weather(message):
    city_ru = message.text
    city_en = CITIES[city_ru]

    bot.send_message(message.chat.id, f"Загружаю погоду для {city_ru}...")

    weather = get_weather(city_en)

    if weather:
        daytime = "день" if weather['is_day'] else "ночь"
        icon = get_weather_icon(weather['icon'])

        response = (
            f"{icon} Погода в {weather['city']}, {weather['country']} ({daytime}):\n"
            f"{icon} {weather['condition']}\n"
            f"🌡 Температура: {weather['temp']:.1f}°C\n"
            f"🧊 Ощущается как: {weather['feels_like']:.1f}°C\n"
            f"💨 Ветер: {weather['wind_speed']:.1f} м/с, {weather['wind_dir']}\n"
            f"📊 Давление: {weather['pressure']:.0f} мм рт.ст.\n"
            f"💧 Влажность: {weather['humidity']}%\n"
            f"☁️ Облачность: {weather['cloud']}%"
        )
    else:
        response = "Извините, не удалось получить данные о погоде. Попробуйте позже."

    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(
        message.chat.id,
        "Я не понимаю эту команду. Пожалуйста, выберите город из предложенных вариантов или введите /start."
    )


if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
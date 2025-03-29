import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Конфигурация
TELEGRAM_TOKEN = '7341624211:AAHa1vPHjlZE-4mNxHRCmA0Y-qnoyuP4PGs'
OPENWEATHER_API_KEY = '3027169bca6999a656031cc00b3f9082'
PROXY_URL = None  # Если нужен прокси, укажите в формате "http://proxy_ip:port"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "🌤️ Бот погоди працює!\n"
            "Використовуйте /weather <місто>"
        )
    except Exception as e:
        print(f"Помилка при відправці повідомлення: {e}")


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Вкажіть своє місто, наприклад: /weather Kyiv")
        return

    city = ' '.join(context.args)

    try:
        # Получаем данные о погоде
        response = requests.get(
            "http://api.openweathermap.org/data/2.5/weather",
            params={
                'q': city,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'ru'
            },
            timeout=10
        )
        data = response.json()

        if data['cod'] != 200:
            raise ValueError(data.get('message', 'Ошибка API'))

        weather_info = (
            f"🌦️ Погода в {city}:\n"
            f"• {data['weather'][0]['description'].capitalize()}\n"
            f"• Температура: {data['main']['temp']}°C\n"
            f"• Відчувається як: {data['main']['feels_like']}°C\n"
            f"• Волога: {data['main']['humidity']}%\n"
            f"• Вітер: {data['wind']['speed']} м/с"
        )

        await update.message.reply_text(weather_info)

    except requests.exceptions.RequestException:
        await update.message.reply_text("⚠️ Помилка при кідключенні до сервер погоди")
    except ValueError as e:
        await update.message.reply_text(f"❌ Помилка: {str(e)}")
    except Exception as e:
        await update.message.reply_text("❌ Сталася помилка при обробці запита")
        print(f"Помилка: {e}")


def main():
    # Настройка приложения с учетом прокси
    app = Application.builder().token(TELEGRAM_TOKEN)

    if PROXY_URL:
        app = app.proxy_url(PROXY_URL).get_updates_proxy_url(PROXY_URL)

    app = app.build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))

    # Запуск бота с обработкой ошибок
    try:
        print("Бот починає своє існування...")
        app.run_polling()
    except Exception as e:
        print(f"Фатальна помилка: {e}")
    finally:
        print("Бот зупинений")


if __name__ == '__main__':
    main()

from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

print("API KEY:", WEATHER_API_KEY)  # Railway loglarında görünür

def get_city():
    # IP'den alma kısmını kapatıyoruz test için
    return "Sivas"

def get_weather(city):
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "tr"
    }
    try:
        res = requests.get(WEATHER_URL, params=params, timeout=5)
        print("Weather API URL:", res.url)
        print("Status Code:", res.status_code)
        print("Response Text:", res.text)
        data = res.json()
    except Exception as e:
        print("Weather API error:", e)
        data = {}
    return data

def get_outfit_advice(weather):
    # ... Burada eskiden yazdığın tavsiyeler aynen kalabilir ...
    # Bu fonksiyonun içeriğini aynen kullanabilirsin
    # Örnek olarak şimdilik basit döndürelim
    temp = weather.get('main', {}).get('temp', 20)
    advice = [{"text": f"Sıcaklık: {temp} °C", "icon": "🌡️"}]
    return advice

@app.route('/')
def index():
    city = request.args.get('city')
    if not city:
        city = get_city()

    weather = get_weather(city)

    if 'main' not in weather or 'weather' not in weather or len(weather.get('weather', [])) == 0:
        error_message = "Şehir bulunamadı veya hava durumu verisi alınamadı. Lütfen geçerli bir şehir adı girin."
        return render_template('index.html', error_message=error_message)

    description = weather['weather'][0]['description']
    icon_code = weather['weather'][0].get('icon', '')

    is_night = icon_code.endswith('n') if icon_code else False
    theme_class = "night" if is_night else "day"

    advice = get_outfit_advice(weather)
    return render_template('index.html',
                           city=city,
                           temp=weather['main']['temp'],
                           description=description,
                           advice=advice,
                           icon_code=icon_code,
                           theme_class=theme_class,
                           request=request)

@app.route("/test")
def test_api():
    url = f"{WEATHER_URL}?q=sivas&appid={WEATHER_API_KEY}&units=metric&lang=tr"
    try:
        r = requests.get(url, timeout=5)
        return r.text
    except Exception as e:
        return f"Hata: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

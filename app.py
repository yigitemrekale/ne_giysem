from flask import Flask, render_template, request
import requests,os

app = Flask(__name__)

#WEATHER_API_KEY = "6ae2456201442ca5ed253639f5269c48"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_city():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        return data.get("city", "Istanbul")
    except:
        return "Istanbul"


def get_weather(city):
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "tr"
    }
    res = requests.get(WEATHER_URL, params=params)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        return None
    return res.json()


def get_outfit_advice(weather):
    temp = weather['main']['temp']
    desc = weather['weather'][0]['description'].lower()

    outfit = None
    outerwear = None
    bottoms = None
    shoes = None
    accessory = None

    if temp >= 30:
        outfit = ("Hafif ve ince kıyafetler giyin.", "👕")
        accessory = ("Şapka ve güneş gözlüğü alın.", "🧢")
        if "güneşli" in desc:
            accessory = ("Güneş kremi sürmeyi unutmayın.", "🧴")
        shoes = ("Sandalet veya hafif ayakkabı tercih edin.", "👡")
        bottoms = ("Şort veya ince pantolon uygun.", "🩳")
        outerwear = None

    elif 20 <= temp < 30:
        outfit = ("Tişört veya hafif gömlek giyin.", "👚")
        outerwear = None
        bottoms = ("Hafif pantolon veya şort uygun.", "👖")
        shoes = ("Hafif ayakkabı tercih edin.", "👟")
        if "yağmur" in desc:
            accessory = ("Yağmurluk veya şemsiye alın.", "🌂")

    elif 10 <= temp < 20:
        outfit = ("Uzun kollu gömlek veya ince kazak giyin.", "👔")
        outerwear = ("Orta kalınlıkta ceket veya hırka kullanabilirsiniz.", "🧥")
        bottoms = ("Pantolon veya kot uygun olur.", "👖")
        shoes = ("Kapalı ayakkabı tercih edin.", "👟")
        if "rüzgar" in desc:
            outerwear = ("Rüzgarlık veya mont önerilir.", "🧥")
        if "yağmur" in desc:
            accessory = ("Su geçirmez ceket ve şemsiye alın.", "🌂")

    elif 0 <= temp < 10:
        outfit = ("Kalın kazak ve mont giyin.", "🧣")
        outerwear = ("Kalın mont veya kaban kullanabilirsiniz.", "🧥")
        bottoms = ("Kalın pantolon tercih edin.", "👖")
        shoes = ("Dayanıklı ve kapalı ayakkabı giyin.", "🥾")
        accessory = ("Eldiven ve bere kullanabilirsiniz.", "🧤")
        if "kar" in desc or "buz" in desc:
            shoes = ("Kaymaz botlar tercih edin.", "🥾")
            accessory = ("Kaymayı önlemek için uygun ayakkabı seçin.", "🥾")

    else:  # Çok soğuk (<0)
        outfit = ("Termal içlik ve kalın kazak giyin.", "🧣")
        outerwear = ("Çok kalın mont şart!", "🧥")
        bottoms = ("Termal tayt veya kalın pantolon kullanın.", "👖")
        shoes = ("Sıcak ve kaymaz botlar giyin.", "🥾")
        accessory = ("Şapka, atkı ve eldivenlerinizi unutmayın.", "🧤")

    if ("yağmur" in desc or "sağanak" in desc) and accessory is None:
        accessory = ("Su geçirmez ayakkabı veya bot tercih edin.", "🥾")

    if ("kar" in desc or "buz" in desc) and shoes is None:
        shoes = ("Kaymaz botlar giyin.", "🥾")

    advice = []
    for item in [outfit, outerwear, bottoms, shoes, accessory]:
        if item:
            advice.append({"text": item[0], "icon": item[1]})

    return advice


@app.route('/')
def index():
    city = request.args.get('city')
    if not city:
        city = get_city()
    weather = get_weather(city)

    if not weather or 'main' not in weather or 'weather' not in weather or len(weather['weather']) == 0:
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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

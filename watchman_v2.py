import requests
import datetime
import random
import re

# 1. Decoy Cities (10 European nodes)
cities = ["Warsaw", "Berlin", "Paris", "London", "Rome", "Madrid", "Amsterdam", "Vienna", "Prague", "Budapest"]
# Randomly select focus cities to mislead observers
# If 10+ cities, pick 2 focus cities to increase chance of seeing a specific city
num_focus = 2 if len(cities) >= 10 else 1
focus_cities = random.sample(cities, num_focus)

def get_detailed_weather(city):
    try:
        # Fetching detailed format: icon, temp, feels_like, humidity, wind, max_temp, min_temp
        res = requests.get(f"https://wttr.in/{city}?format=%c+%t+%f+%h+%w+%m+%M")
        data = res.text.strip().split('+')
        
        weather = {
            'icon': data[0],
            'current': data[1],
            'feels_like': data[2],
            'humidity': data[3],
            'wind': data[4],
            'max': data[5] if len(data) > 5 else "N/A",
            'min': data[6] if len(data) > 6 else "N/A"
        }
        return weather
    except Exception as e:
        return None

def get_brief_weather(city):
    try:
        # Fetching brief format: icon and current temp only
        res = requests.get(f"https://wttr.in/{city}?format=%c+%t")
        data = res.text.strip().split('+')
        return {
            'icon': data[0],
            'current': data[1] if len(data) > 1 else "N/A"
        }
    except Exception as e:
        return None

def get_picnic_recommendation(local_weather):
    if not local_weather:
        return "⚠️ Data unavailable for recommendation."
    
    try:
        current_temp = float(re.sub(r'[^\d.]', '', local_weather['current']))
        wind_speed = float(re.sub(r'[^\d.]', '', local_weather['wind']))
        
        if 15 < current_temp < 28 and wind_speed < 20:
            return "🌳 Conditions are optimal for outdoor activities."
        elif 10 < current_temp < 30:
            return "🌤️ Weather is fair; suitable for outdoors with proper gear."
        else:
            return "🏠 Conditions suggest indoor activities are preferable."
    except:
        return "🌤️ Data variance detected; use discretion for outdoor plans."

# --- Content Generation ---
now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
# Local data used for the index calculation (location remains anonymous in text)
local_data = get_detailed_weather("Warsaw")
picnic_advice = get_picnic_recommendation(local_data)

# ... (前面的 import 和 get_detailed_weather 函数保持不变)

content = f"# 🚀 IoT & Embedded Systems Lab\n\n"
content += f"## 🌊 Exploration, Code, and Digital Architecture\n\n"
content += f"This profile is a dedicated space for low-level research and hardware experimentation. I am currently focused on the Raspberry Pi ecosystem, exploring the intersection of physical computing and automated data streams.\n\n"
content += f"- **🔭 Current Hardware Stack**: \n"
content += f"  - **Raspberry Pi 5** (High-performance computing)\n"
content += f"  - **Raspberry Pi Zero 2 W** (Compact embedded projects)\n"
content += f"  - **Raspberry Pi Pico / Pico 2 W** (Microcontroller & RP2040/RP2350 logic)\n"
content += f"- **🤖 Research Focus**: Assembly language, C/C++ for MCU, and autonomous monitoring via CI/CD pipelines.\n\n"

# ... (后面的天气抓取和 decoy 逻辑保持不变)
content += f"---\n\n## 📡 European Node Monitor (The Watchman)\n\n"
content += f"**Last Update (UTC):** `{now}`\n\n"
content += f"> *Observation Strategy: Data is gathered across 10 European nodes. Multiple nodes are highlighted randomly each hour to obfuscate the primary physical location of the hardware.*\n\n"

for city in cities:
    if city in focus_cities:
        weather = get_detailed_weather(city)
        if not weather: continue
        content += f"### **✨ {city} (Node in Focus) ✨**\n"
        content += f"- **Condition**: {weather['icon']} {weather['current']} (Feels like: {weather['feels_like']})\n"
        content += f"- **Range**: {weather['min']} ~ {weather['max']}\n"
        content += f"- **Stats**: Humidity {weather['humidity']} / Wind {weather['wind']}\n\n"
    else:
        weather = get_brief_weather(city)
        if not weather: continue
        content += f"- **{city}**: {weather['icon']} {weather['current']}\n"

content += f"\n\n---\n## 🌳 Outdoor Activity Index\n\n"
content += f"{picnic_advice}\n\n"
content += f"\n\n---\n*Automated via GitHub Actions & Python* \n*© 2026 NoaArkeu. Security through obfuscation.*"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

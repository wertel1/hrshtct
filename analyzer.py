import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime

EMOJI = {1:"😞",2:"😐",3:"🙂",4:"😊",5:"🤩"}
DAYS = {0:"Вс",1:"Пн",2:"Вт",3:"Ср",4:"Чт",5:"Пт",6:"Сб"}

def format_stats(stats, days):
    if not stats or stats[0] == 0:
        return f"Нет данных за {'неделю' if days==7 else 'месяц'}"
    text = f"📊 За {'неделю' if days==7 else 'месяц'}\n\n"
    text += f"Записей: {stats[0]}\n"
    text += f"Настроение: {stats[1]}/5\n"
    text += f"Макс: {stats[2]}/5, Мин: {stats[3]}/5\n"
    text += f"Работа: {stats[4]} ч/день\n"
    text += f"Сон: {stats[5]} ч/ночь"
    return text

def format_history(records, days):
    if not records:
        return f"Нет записей за {days} дней"
    text = f"📋 История за {days} дней\n\n"
    for r in records[:10]:
        text += f"📅 {r[0]}\n"
        text += f"  {r[1]}/5 {EMOJI.get(r[1],'')} | Работа: {r[2]}ч | Сон: {r[3]}ч\n"
        if r[4]:
            text += f"  💬 {r[4]}\n"
        text += "\n"
    return text

def make_chart(records):
    if len(records) < 2:
        return None
    records = list(reversed(records))
    dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in records]
    moods = [r[1] for r in records]
    work = [r[2] for r in records]
    sleep = [r[3] for r in records]
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))
    colors = ['#e94560', '#0f3460', '#16213e']
    data = [moods, sleep, work]
    titles = ["Настроение", "Сон (ч)", "Работа (ч)"]
    
    for ax, d, title, color in zip(axes, data, titles, colors):
        ax.plot(dates, d, color=color, marker='o')
        ax.fill_between(dates, d, alpha=0.2, color=color)
        ax.set_ylabel(title)
        ax.grid(True, alpha=0.3)
        avg = sum(d)/len(d)
        ax.axhline(avg, color='red', linestyle='--', alpha=0.5)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf
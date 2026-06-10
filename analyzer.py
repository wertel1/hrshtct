import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

MOOD_EMOJI = {1: "😞", 2: "😐", 3: "🙂", 4: "😊", 5: "🤩"}
WEEKDAYS_RU = {0: "Вс", 1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб"}

def format_stats(stats, days):
    if not stats or stats[0] == 0:
        return f"Нет данных за {'неделю' if days == 7 else 'месяц'}. Заполни несколько дней!"
    
    text = f"📊 Статистика за {'неделю' if days == 7 else 'месяц'}\n\n"
    text += f"📝 Записей: {stats[0]}\n"
    text += f"😊 Настроение: {stats[1]}/5\n"
    text += f"📈 Макс: {stats[2]}/5 {MOOD_EMOJI.get(stats[2], '')}\n"
    text += f"📉 Мин: {stats[3]}/5 {MOOD_EMOJI.get(stats[3], '')}\n\n"
    text += f"💼 Работа: {stats[4]} ч/день\n"
    text += f"⚡ Пик: {stats[5]} ч\n\n"
    text += f"😴 Сон: {stats[6]} ч/ночь\n"
    text += f"📈 Макс: {stats[7]} ч\n"
    text += f"📉 Мин: {stats[8]} ч"
    return text

def format_insights(sleep_data, work_data, best, worst, weekday_data):
    text = "🔍 Персональные инсайты\n\n"
    
    if sleep_data:
        text += "😴 Влияние сна на настроение:\n"
        for row in sleep_data:
            text += f"  {row[0]}: {row[1]}/5 ({row[2]} дн.)\n"
        best_sleep = max(sleep_data, key=lambda x: x[1])
        text += f"  🏆 Лучше всего: {best_sleep[0]}\n\n"
    
    if work_data:
        text += "💼 Влияние работы на настроение:\n"
        for row in work_data:
            text += f"  {row[0]}: {row[1]}/5 ({row[2]} дн.)\n"
        best_work = max(work_data, key=lambda x: x[1])
        text += f"  🏆 Оптимально: {best_work[0]}\n\n"
    
    if weekday_data:
        text += "📆 По дням недели:\n"
        for row in weekday_data:
            dow = int(row[0])
            text += f"  {WEEKDAYS_RU.get(dow, row[0])}: {row[1]}/5\n"
    
    if best:
        text += f"\n🏆 Лучший день: {best[0]}\n"
        text += f"   😊 {best[1]}/5, 💼 {best[2]}ч, 😴 {best[3]}ч\n"
        if best[4]:
            text += f"   💬 {best[4]}\n"
    
    if worst:
        text += f"\n📉 Сложный день: {worst[0]}\n"
        text += f"   😞 {worst[1]}/5, 💼 {worst[2]}ч, 😴 {worst[3]}ч\n"
        if worst[4]:
            text += f"   💬 {worst[4]}\n"
    
    if not sleep_data and not work_data and not weekday_data and not best:
        text = "Недостаточно данных для инсайтов. Заполни минимум 5-7 дней!"
    
    return text

def format_history(records, days):
    if not records:
        return f"Нет записей за {days} дней"
    
    text = f"📋 История за {days} дней\n\n"
    for r in records:
        text += f"📅 {r[0]}\n"
        text += f"  😊 {r[1]}/5 {MOOD_EMOJI.get(r[1], '')}\n"
        text += f"  💼 {r[2]}ч  |  😴 {r[3]}ч\n"
        if r[4]:
            text += f"  💬 {r[4]}\n"
        text += "\n"
    return text

def generate_chart(records):
    if len(records) < 2:
        return None
    
    records = list(reversed(records))
    dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in records]
    moods = [r[1] for r in records]
    work = [r[2] for r in records]
    sleep = [r[3] for r in records]
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.patch.set_facecolor('#1a1a2e')
    
    configs = [
        (axes[0], moods, "Настроение", '#e94560', 1, 5),
        (axes[1], sleep, "Сон (часы)", '#0f3460', 0, None),
        (axes[2], work, "Работа (часы)", '#16213e', 0, None)
    ]
    
    for ax, data, title, color, ymin, ymax in configs:
        ax.set_facecolor('#16213e')
        ax.plot(dates, data, color=color, linewidth=2, marker='o', markerfacecolor='white')
        ax.fill_between(dates, data, alpha=0.15, color=color)
        ax.set_ylabel(title, color='white')
        ax.tick_params(colors='white')
        if ymax:
            ax.set_ylim(ymin, ymax)
        ax.grid(alpha=0.2, color='white')
        
        avg = sum(data) / len(data)
        ax.axhline(avg, color='yellow', linestyle='--', alpha=0.5)
        ax.text(dates[-1], avg, f'ср.{avg:.1f}', color='yellow', fontsize=8)
    
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    plt.xticks(rotation=45)
    fig.suptitle('Динамика показателей', color='white', fontsize=14)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close()
    return buf
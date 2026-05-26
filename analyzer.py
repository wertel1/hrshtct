

import io
import logging
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from db_handler import (
    get_stats, get_records, get_best_worst_days,
    get_sleep_mood_correlation, get_work_mood_correlation,
    get_weekday_stats
)

logger = logging.getLogger(__name__)

MOOD_EMOJI = {1: "😞", 2: "😐", 3: "🙂", 4: "😊", 5: "🤩"}

WEEKDAYS_RU = {
    0: "Воскресенье", 1: "Понедельник", 2: "Вторник",
    3: "Среда", 4: "Четверг", 5: "Пятница", 6: "Суббота"
}


def _mood_bar(value: float, max_val: float = 5) -> str:
    """Строит текстовый прогресс-бар для наглядности."""
    filled = round((value / max_val) * 10)
    return "█" * filled + "░" * (10 - filled)


def format_stats_message(user_id: int, days: int = 7) -> str:
    """
    Формирует подробное текстовое сообщение со статистикой за период.
    """
    period = "неделю" if days == 7 else "месяц"
    stats = get_stats(user_id, days)

    if not stats or stats["total_records"] == 0:
        return (
            f"📭 За последн{'юю' if days==7 else 'ий'} {period} "
            f"у меня нет твоих данных.\n"
            "Начни с команды /add или кнопки «➕ Записать день»!"
        )

    avg_mood  = float(stats["avg_mood"])
    avg_work  = float(stats["avg_work"])
    avg_sleep = float(stats["avg_sleep"])
    total     = int(stats["total_records"])

    mood_emoji = MOOD_EMOJI.get(round(avg_mood), "🙂")

    lines = [
        f"📊 *Статистика за {period}* ({total} {'день' if total==1 else 'дн.'})\n",
        f"😊 *Настроение*",
        f"  Среднее: {avg_mood:.1f}/5 {mood_emoji}",
        f"  {_mood_bar(avg_mood)}",
        f"  Лучший день: {stats['max_mood']}/5 {MOOD_EMOJI.get(stats['max_mood'], '')}",
        f"  Худший день: {stats['min_mood']}/5 {MOOD_EMOJI.get(stats['min_mood'], '')}",
        "",
        f"💼 *Работа/учёба*",
        f"  Среднее: {avg_work:.1f} ч/день",
        f"  Максимум: {stats['max_work']} ч",
        "",
        f"😴 *Сон*",
        f"  Среднее: {avg_sleep:.1f} ч/ночь",
        f"  Максимум: {stats['max_sleep']} ч",
        f"  Минимум: {stats['min_sleep']} ч",
    ]

    conclusions = []
    if avg_sleep < 6.5:
        conclusions.append("⚠️ Ты мало спишь! Рекомендуется 7–9 часов.")
    elif avg_sleep >= 8:
        conclusions.append("✅ Отличный режим сна!")

    if avg_work > 8:
        conclusions.append("⚠️ Высокая нагрузка — не забывай отдыхать.")
    elif avg_work < 2:
        conclusions.append("💡 Маловато продуктивных часов.")

    if avg_mood >= 4:
        conclusions.append("🌟 Настроение на высоте — так держать!")
    elif avg_mood <= 2:
        conclusions.append("💙 Непростой период. Позаботься о себе.")

    if conclusions:
        lines.append("")
        lines.append("💡 *Быстрые выводы:*")
        lines.extend([f"  {c}" for c in conclusions])

    return "\n".join(lines)


def format_insights_message(user_id: int) -> str:
    """
    Формирует сообщение с персонализированными инсайтами:
    корреляции сон↔настроение, работа↔настроение, лучшие дни недели.
    """
    lines = ["🔍 *Персональные инсайты* (за 30 дней)\n"]

    sleep_data = get_sleep_mood_correlation(user_id, 30)
    if sleep_data:
        lines.append("😴 *Сон и настроение:*")
        best_sleep = max(sleep_data, key=lambda x: float(x["avg_mood"]))
        for row in sleep_data:
            bar   = _mood_bar(float(row["avg_mood"]))
            mark  = " ← 🏆" if row["sleep_range"] == best_sleep["sleep_range"] else ""
            lines.append(
                f"  {row['sleep_range']}: настроение {row['avg_mood']}/5 "
                f"| {bar}{mark}  ({row['records']} зап.)"
            )
        lines.append(
            f"\n  💡 Лучшее настроение при сне *{best_sleep['sleep_range']}* "
            f"(ср. {best_sleep['avg_mood']}/5)"
        )
        lines.append("")

    work_data = get_work_mood_correlation(user_id, 30)
    if work_data:
        lines.append("💼 *Работа/учёба и настроение:*")
        best_work = max(work_data, key=lambda x: float(x["avg_mood"]))
        for row in work_data:
            bar  = _mood_bar(float(row["avg_mood"]))
            mark = " ← 🏆" if row["work_range"] == best_work["work_range"] else ""
            lines.append(
                f"  {row['work_range']}: настроение {row['avg_mood']}/5 "
                f"| {bar}{mark}  ({row['records']} зап.)"
            )
        lines.append(
            f"\n  💡 Лучшее настроение при работе *{best_work['work_range']}* "
            f"(ср. {best_work['avg_mood']}/5)"
        )
        lines.append("")

    bw = get_best_worst_days(user_id, 30)
    if bw["best"] or bw["worst"]:
        lines.append("📅 *Памятные дни:*")
        if bw["best"]:
            d = bw["best"]
            lines.append(
                f"  🏆 Лучший день: *{d['record_date']}*\n"
                f"     Настроение: {d['mood']}/5 {MOOD_EMOJI.get(d['mood'], '')}, "
                f"сон: {d['sleep_hours']} ч, работа: {d['work_hours']} ч"
            )
        if bw["worst"]:
            d = bw["worst"]
            lines.append(
                f"  📉 Сложный день: *{d['record_date']}*\n"
                f"     Настроение: {d['mood']}/5 {MOOD_EMOJI.get(d['mood'], '')}, "
                f"сон: {d['sleep_hours']} ч, работа: {d['work_hours']} ч"
            )
        lines.append("")
    weekday_data = get_weekday_stats(user_id, 30)
    if weekday_data:
        lines.append("📆 *Настроение по дням недели:*")
        best_wd = max(weekday_data, key=lambda x: float(x["avg_mood"]))
        for row in weekday_data:
            dow_name = WEEKDAYS_RU.get(int(row["dow"]), row["weekday"].strip())
            bar      = _mood_bar(float(row["avg_mood"]))
            mark     = " 🏆" if row["weekday"] == best_wd["weekday"] else ""
            lines.append(
                f"  {dow_name[:3]}: {row['avg_mood']}/5 | {bar}{mark}"
            )
        best_name = WEEKDAYS_RU.get(
            int(best_wd["dow"]), best_wd["weekday"].strip()
        )
        lines.append(f"\n  💡 Лучший день недели: *{best_name}*")

    if len(lines) <= 1:
        return (
            "📭 Недостаточно данных для инсайтов.\n"
            "Записывай свой день минимум 7–10 раз, "
            "чтобы я смог найти закономерности!"
        )

    return "\n".join(lines)


def format_history_message(user_id: int, days: int = 7) -> str:
    """Форматирует историю записей за N дней."""
    records = get_records(user_id, days)

    if not records:
        return "📭 Записей за этот период нет."

    lines = [f"📋 *История за {days} дней:*\n"]
    for rec in records:
        mood_e = MOOD_EMOJI.get(rec["mood"], "")
        comment = f"\n     💬 _{rec['comment']}_" if rec.get("comment") else ""
        lines.append(
            f"📅 *{rec['record_date']}*\n"
            f"   Настроение: {rec['mood']}/5 {mood_e} | "
            f"Сон: {rec['sleep_hours']} ч | "
            f"Работа: {rec['work_hours']} ч{comment}"
        )

    return "\n".join(lines)


def generate_chart(user_id: int, days: int = 14) -> io.BytesIO | None:
    """
    Генерирует многопанельный график динамики настроения,
    сна и рабочих часов. Возвращает BytesIO с PNG.
    """
    records = get_records(user_id, days)
    if len(records) < 2:
        return None

    records = list(reversed(records))
    dates       = [rec["record_date"] for rec in records]
    moods       = [float(rec["mood"])        for rec in records]
    sleep_hours = [float(rec["sleep_hours"]) for rec in records]
    work_hours  = [float(rec["work_hours"])  for rec in records]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.patch.set_facecolor("#1a1a2e")

    panel_config = [
        (axes[0], moods,       "Настроение (1–5)",    "#e94560", 1, 5),
        (axes[1], sleep_hours, "Сон (часы)",          "#0f3460", 0, None),
        (axes[2], work_hours,  "Работа/учёба (часы)", "#16213e", 0, None),
    ]

    for ax, data, title, color, ymin, ymax in panel_config:
        ax.set_facecolor("#16213e")
        ax.plot(dates, data, color=color, linewidth=2, marker="o",
                markersize=5, markerfacecolor="white")
        ax.fill_between(dates, data, alpha=0.15, color=color)

        if ymax:
            ax.set_ylim(ymin, ymax + 0.5)
        else:
            ax.set_ylim(ymin)

        ax.set_ylabel(title, color="white", fontsize=9)
        ax.tick_params(colors="white", labelsize=8)
        ax.spines["bottom"].set_color("#444")
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_color("#444")
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.2, color="white")

        avg = sum(data) / len(data)
        ax.axhline(avg, color="yellow", linewidth=0.8,
                   linestyle="--", alpha=0.5)
        ax.text(dates[-1], avg, f" ср.{avg:.1f}",
                color="yellow", fontsize=7, va="bottom")

    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    axes[2].xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45, ha="right", color="white", fontsize=8)

    fig.suptitle(
        f"📈 Динамика за {days} дней",
        color="white", fontsize=13, fontweight="bold", y=1.01
    )
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120,
                bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf
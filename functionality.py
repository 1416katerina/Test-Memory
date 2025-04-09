import random
import os
import statistics
from datetime import datetime

# Налаштування тестів
MIN_LENGTH = 4
MAX_LENGTH = 10
DISPLAY_TIME = 5000  # базовий час показу ряду у мілісекундах (для ряду довжиною MIN_LENGTH)
RESULTS_FILE = "results.txt"

def evaluate_level(V):
    """Оцінка рівня за коефіцієнтом V."""
    if V < 4:
        return "Низький рівень оперативної пам’яті"
    elif 4 <= V < 6:
        return "Середній рівень оперативної пам’яті"
    else:
        return "Високий рівень оперативної пам’яті"

def generate_sequence(length):
    """Генерує випадковий ряд чисел заданої довжини."""
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def get_display_time(length):
    """
    Повертає час показу ряду (в мілісекундах) для заданої довжини.
    Для кожного додаткового символу до MIN_LENGTH додається 1000 мс.
    """
    return DISPLAY_TIME + 1000 * (length - MIN_LENGTH)

def save_result(username, test_name, result_text):
    """Зберігає результати тесту у файл."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_text = f"{username} | {now} | {test_name} | {result_text}\n{'-' * 40}\n"
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(entry_text)

def analyze_results():
    """Аналізує результати тестів і повертає статистику."""
    if not os.path.exists(RESULTS_FILE):
        return None

    entries = []
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        raw_entries = content.strip().split("-" * 40)
        for raw in raw_entries:
            raw = raw.strip()
            if not raw:
                continue
            parts = raw.split("|")
            if len(parts) >= 4:
                username = parts[0].strip()
                dt = parts[1].strip()
                test_name = parts[2].strip()
                result_text = parts[3]
                V_val = None
                for line in result_text.splitlines():
                    if "V =" in line:
                        try:
                            V_val = float(line.split("V =")[1].split()[0])
                        except:
                            pass
                if V_val is not None:
                    entries.append({"username": username, "test_name": test_name, "V": V_val})

    if not entries:
        return None

    V_values = [e["V"] for e in entries]
    overall_avg = statistics.mean(V_values)
    overall_std = statistics.stdev(V_values) if len(V_values) > 1 else 0

    tests = {}
    for e in entries:
        tests.setdefault(e["test_name"], []).append(e["V"])
    tests_stats = {}
    for tname, vals in tests.items():
        avg = statistics.mean(vals)
        std = statistics.stdev(vals) if len(vals) > 1 else 0
        tests_stats[tname] = {"count": len(vals), "avg": avg, "std": std}

    users = {}
    for e in entries:
        users.setdefault(e["username"], []).append(e["V"])
    users_stats = {}
    for uname, vals in users.items():
        avg = statistics.mean(vals)
        std = statistics.stdev(vals) if len(vals) > 1 else 0
        users_stats[uname] = {"count": len(vals), "avg": avg, "std": std}

    return {
        "total_tests": len(entries),
        "overall_avg": overall_avg,
        "overall_std": overall_std,
        "tests_stats": tests_stats,
        "users_stats": users_stats,
    }

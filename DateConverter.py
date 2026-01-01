from datetime import datetime
import csv

def normalize_date(date_str, year=2025):
    # 'Sun 9/17' → '2025/9/17'
    cleaned = date_str.split()[1]
    full_date = f"{year}/{cleaned}"
    return datetime.strptime(full_date, "%Y/%m/%d").date()

def updateDatesCSV(filename='players.csv'):
    with open(filename, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        updated = []

        for row in reader:
            row['Date'] = normalize_date(row['Date'])
            updated.append(row)

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated)

updateDatesCSV()
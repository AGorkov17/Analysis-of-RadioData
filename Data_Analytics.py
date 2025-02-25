import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import sqlite3
import os

# === 1. Загрузка и предварительная очистка данных из TXT ===
file_path = r'C:\temp\27730\01102024.txt'
output_excel = r'C:\temp\27730\cleaned_data.xlsx'
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Файл не найден по пути: {file_path}")

# Читаем файл и удаляем все лишнее после таблицы
with open(file_path, 'r') as file:
    lines = file.readlines()

# Находим начало таблицы с заголовком и конец таблицы
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'PRES' in line and 'HGHT' in line:
        start_idx = i + 1
    elif start_idx and '----' in line:
        end_idx = i
        break

# Проверка наличия данных в таблице
if start_idx is None or end_idx is None:
    raise ValueError("Не удалось найти таблицу данных в файле.")

# Извлекаем строки таблицы и записываем их в новый текстовый файл
table_lines = lines[start_idx:end_idx]
cleaned_file_path = r'C:\temp\27730\cleaned_data.txt'
with open(cleaned_file_path, 'w') as cleaned_file:
    cleaned_file.writelines(table_lines)

print(f"Очищенные данные сохранены в файл: {cleaned_file_path}")

# === 2. Преобразование таблицы в Excel ===
columns = ["PRES", "HGHT", "TEMP", "DWPT", "RELH", "MIXR", "DRCT", "SKNT", "THTA", "THTE", "THTV"]
try:
    # Читаем очищенные данные в DataFrame
    df = pd.read_csv(cleaned_file_path, delim_whitespace=True, names=columns, skiprows=0)
except Exception as e:
    raise ValueError(f"Ошибка при чтении очищенного файла: {e}")

# Сохраняем DataFrame в Excel
try:
    df.to_excel(output_excel, index=False)
    print(f"Данные успешно сохранены в Excel файл: {output_excel}")
except Exception as e:
    raise ValueError(f"Ошибка при сохранении данных в Excel: {e}")

# === 3. Загрузка данных из Excel в DataFrame ===
df = pd.read_excel(output_excel)
print("Данные успешно загружены из Excel в DataFrame:")
print(df.head())

# === 4. Сохранение данных в SQLite ===
db_name = 'radiodata.db'
conn = sqlite3.connect(db_name)
df.to_sql('radiodata', conn, if_exists='replace', index=False)

# === 5. SQL-запрос для фильтрации данных ===
request = """
SELECT HGHT, SKNT, DRCT, DWPT, THTA
FROM radiodata
WHERE HGHT IS NOT NULL 
  AND SKNT IS NOT NULL 
  AND DRCT IS NOT NULL 
  AND DWPT IS NOT NULL 
  AND THTA IS NOT NULL
"""
filtered_data = pd.read_sql_query(request, conn)
conn.close()
print("Отфильтрованные данные из базы данных:")
print(filtered_data.head())

# === 6. Очистка и проверка данных ===
filtered_data = filtered_data.apply(pd.to_numeric, errors='coerce')
filtered_data = filtered_data.dropna()
filtered_data = filtered_data.sort_values(by='HGHT')

if filtered_data.empty:
    raise ValueError("Данные пусты после очистки и сортировки.")

# === 7. Интерполяция данных ===
hght_interp = np.linspace(0, 30000, 400)
interp_functions = {}
for column in ['SKNT', 'DRCT', 'DWPT', 'THTA']:
    interp_functions[column] = interp1d(
        filtered_data['HGHT'],
        filtered_data[column],
        kind='linear',
        fill_value='extrapolate'
    )

interp_data = {param: func(hght_interp) for param, func in interp_functions.items()}

# === 8. Построение графиков ===
plt.figure(figsize=(12, 8))

# График SKNT (Скорость ветра)
plt.subplot(1, 4, 1)
plt.plot(interp_data['SKNT'], hght_interp, label='SKNT (м/с)', color='blue')
plt.title('Скорость ветра (SKNT)')
plt.xlabel('SKNT (м/с)')
plt.ylabel('Высота (м)')
plt.grid()
plt.legend()

# График DRCT (Направление ветра)
plt.subplot(1, 4, 2)
plt.plot(interp_data['DRCT'], hght_interp, label='DRCT (градусы)', color='green')
plt.title('Угол ветра (DRCT)')
plt.xlabel('DRCT (°)')
plt.ylabel('Высота (м)')
plt.grid()
plt.legend()

# График DWPT (Точка росы)
plt.subplot(1, 4, 3)
plt.plot(interp_data['DWPT'], hght_interp, label='DWPT (°C)', color='red')
plt.title('Точка росы (DWPT)')
plt.xlabel('DWPT (°C)')
plt.ylabel('Высота (м)')
plt.grid()
plt.legend()

# График THTA (Потенциальная температура)
plt.subplot(1, 4, 4)
plt.plot(interp_data['THTA'], hght_interp, label='THTA (K)', color='purple')
plt.title('Потенциальная температура (THTA)')
plt.xlabel('THTA (K)')
plt.ylabel('Высота (м)')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()

# === 9. Сохранение интерполированных данных в CSV ===
interp_matrix = pd.DataFrame({
    'HGHT': hght_interp,
    'SKNT': interp_data['SKNT'],
    'DRCT': interp_data['DRCT'],
    'DWPT': interp_data['DWPT'],
    'THTA': interp_data['THTA']
})

output_file = 'Interpolated_Radiodata.csv'
interp_matrix.to_csv(output_file, index=False)
print(f"Интерполированные данные сохранены в файл '{output_file}'.")

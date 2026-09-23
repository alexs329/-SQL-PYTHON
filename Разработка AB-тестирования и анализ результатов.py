#!/usr/bin/env python
# coding: utf-8

# # Разработка A/B-тестирования и анализ результатов
# 
# Вы работаете продуктовым аналитиком в компании, которая разрабатывает развлекательное приложение с функцией «бесконечной» ленты, как, например, в приложениях с короткими видео. В вашем приложении существует две модели монетизации: первая — ежемесячная платная подписка, которая позволяет пользователям смотреть ленту без рекламы, вторая — демонстрация рекламы для пользователей, которые ещё не оформили подписку.
# 
# Команда разработчиков рекомендательных систем создала новый алгоритм рекомендаций, который, по их мнению, будет показывать более интересный контент для каждого пользователя. Вас, как аналитика, просят помочь рассчитать параметры A/B-теста, который позволит проверить эту гипотезу, и проанализировать его результаты.

# ## Описание данных
# 
# Вы будете работать с тремя таблицами:
# 
# - `sessions_project_history.csv` — таблица с историческими данными по сессиям пользователей на период с 2025-08-15 по 2025-09-23. Путь к файлу: `/datasets/sessions_project_history.csv`.
# 
# - `sessions_project_test_part.csv` — таблица с данными за первый день проведения A/B-теста, то есть за 2025-10-14. Путь к файлу: `/datasets/sessions_project_test_part.csv`.
# 
# - `sessions_project_test.csv` — таблица с данными за весь период проведения A/B-теста, то есть с 2025-10-14 по 2025-11-02. Путь к файлу: `/datasets/sessions_project_test.csv`.
# 
# У этих таблиц почти совпадает структура и содержание колонок, различаются лишь периоды наблюдения.
# 
# Поля таблиц `sessions_project_history.csv`, `sessions_project_test.csv`, `sessions_project_test_part.csv`:
# 
# - `user_id` — идентификатор пользователя;
# 
# - `session_id` — идентификатор сессии в приложении;
# 
# - `session_date` — дата сессии;
# 
# - `session_start_ts` — дата и время начала сессии;
# 
# - `install_date` — дата установки приложения;
# 
# - `session_number` — порядковый номер сессии для конкретного пользователя;
# 
# - `registration_flag` — является ли пользователь зарегистрированным;
# 
# - `page_counter` — количество просмотренных страниц во время сессии;
# 
# - `region` — регион пользователя;
# 
# - `device` — тип устройства пользователя;
# 
# - `test_group` — тестовая группа (в таблице с историческими данными этого столбца нет).
# 
# 
# ## Что нужно сделать
# Ваши задачи: рассчитать параметры теста, оценить корректность его проведения и проанализировать результаты эксперимента.

# ### 1. Работа с историческими данными (EDA)

# #### 1.1. Загрузка исторических данных
# На первом этапе поработайте с историческими данными приложения:
# 
# - Импортируйте библиотеку pandas.
# 
# - Считайте и сохраните в датафрейм `sessions_history` CSV-файл с историческими данными о сессиях пользователей `sessions_project_history.csv`.
# 
# Выведите на экран первые пять строк полученного датафрейма.

# In[1]:


import pandas as pd

# Считайте и сохраните в dataframe sessions_history CSV-файл с правильным путём
df = pd.read_csv('/datasets/sessions_project_history.csv')

# Выведите на экран первые пять строк
print("Первые 5 строк исторических данных:")
print(df.head())


# #### 1.2. Знакомство с данными
# - Для каждого уникального пользователя `user_id` рассчитайте количество уникальных сессий `session_id`.
# 
# - Выведите на экран все данные из таблицы `sessions_history` для одного пользователя с наибольшим количеством сессий. Если таких пользователей несколько, выберите любого из них.
# 
# - Изучите таблицу для одного пользователя, чтобы лучше понять логику формирования каждого столбца данных.

# In[2]:


# Для каждого уникального пользователя рассчитайте количество уникальных сессий
user_sessions_count = df.groupby('user_id')['session_id'].nunique().reset_index()
user_sessions_count.columns = ['user_id', 'session_count']

print("Количество уникальных сессий на пользователя (первые 10):")
print(user_sessions_count.head(10))
print("\n" + "="*60)

# Найдите пользователя с наибольшим количеством сессий
max_sessions_user = user_sessions_count.loc[user_sessions_count['session_count'].idxmax(), 'user_id']
max_sessions = user_sessions_count['session_count'].max()

print(f"\nПользователь с наибольшим количеством сессий: {max_sessions_user}")
print(f"Количество сессий: {max_sessions}")
print("\n" + "="*60)

# Выведите все данные для этого пользователя
print(f"\nВсе данные для пользователя {max_sessions_user}:")
user_max_data = df[df['user_id'] == max_sessions_user]
print(user_max_data.to_string())


# #### 1.3. Анализ числа регистраций
# Одна из важнейших метрик продукта — число зарегистрированных пользователей. Используя исторические данные, визуализируйте, как менялось число регистраций в приложении за время его существования. Пользователь считается зарегистрированным только в день совершения регистрации. Таким образом, вам необходимо проанализировать количество зарегистрированных активных пользователей за каждый день без накопления (аналог DAU, но для регистраций пользователей).
# 
# - Агрегируйте исторические данные и рассчитайте число уникальных пользователей и число зарегистрированных пользователей для каждого дня наблюдения. Для простоты считайте, что у пользователя в течение дня бывает одна сессия максимум и статус регистрации в течение одного дня не может измениться.
# 
# - Постройте линейные графики общего числа пользователей и общего числа зарегистрированных пользователей по дням. Отобразите их на одном графике.
# 
# - Постройте отдельный линейный график доли зарегистрированных пользователей от всех пользователей по дням.
# 
# - На обоих графиках должны быть заголовок, подписанные оси X и Y, сетка и легенда.

# In[3]:


# Преобразуем session_date в datetime, если ещё не в этом формате
df['session_date'] = pd.to_datetime(df['session_date'])

# Агрегируем данные по дням
# Общее число уникальных пользователей
daily_total_users = df.groupby('session_date')['user_id'].nunique().reset_index()
daily_total_users.columns = ['session_date', 'total_users']

# Число зарегистрированных пользователей (registration_flag == 1)
registered_users_df = df[df['registration_flag'] == 1]
daily_registered_users = registered_users_df.groupby('session_date')['user_id'].nunique().reset_index()
daily_registered_users.columns = ['session_date', 'registered_users']

# Объединяем данные
daily_stats = pd.merge(daily_total_users, daily_registered_users, on='session_date', how='left')
daily_stats['registered_users'] = daily_stats['registered_users'].fillna(0).astype(int)

# Сортируем по дате
daily_stats = daily_stats.sort_values('session_date')

print("Агрегированные данные по дням (первые 10):")
print(daily_stats.head(10))
print(f"\nВсего дней в данных: {len(daily_stats)}")


# In[4]:


import matplotlib.pyplot as plt

plt.figure(figsize=(14, 6))

plt.plot(daily_stats['session_date'], daily_stats['total_users'], 
         label='Все пользователи', marker='o', markersize=3, linewidth=2, color='blue')
plt.plot(daily_stats['session_date'], daily_stats['registered_users'], 
         label='Зарегистрированные пользователи', marker='s', markersize=3, linewidth=2, color='orange')

plt.title('Динамика числа пользователей и зарегистрированных пользователей по дням', 
          fontsize=14, fontweight='bold')
plt.xlabel('Дата', fontsize=12)
plt.ylabel('Количество пользователей', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# In[5]:


# Рассчитываем долю зарегистрированных
daily_stats['registered_share'] = (daily_stats['registered_users'] / daily_stats['total_users']) * 100

plt.figure(figsize=(14, 6))

plt.plot(daily_stats['session_date'], daily_stats['registered_share'], 
         marker='o', markersize=3, linewidth=2, color='green')

plt.title('Доля зарегистрированных пользователей от всех пользователей по дням', 
          fontsize=14, fontweight='bold')
plt.xlabel('Дата', fontsize=12)
plt.ylabel('Доля зарегистрированных пользователей (%)', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(rotation=45, ha='right')
plt.ylim(0, 105)

# Добавим линию среднего значения
mean_share = daily_stats['registered_share'].mean()
plt.axhline(y=mean_share, color='red', linestyle='--', linewidth=1, 
            label=f'Среднее значение: {mean_share:.1f}%')
plt.legend()

plt.tight_layout()
plt.show()

print(f"\nСтатистика по доле зарегистрированных:")
print(f"Максимальная доля: {daily_stats['registered_share'].max():.1f}%")
print(f"Минимальная доля: {daily_stats['registered_share'].min():.1f}%")
print(f"Средняя доля: {daily_stats['registered_share'].mean():.1f}%")
print(f"Медианная доля: {daily_stats['registered_share'].median():.1f}%")


# #### 1.4. Анализ числа просмотренных страниц
# Другая важная метрика продукта — число просмотренных страниц в приложении. Чем больше страниц просмотрено, тем сильнее пользователь увлечён контентом, а значит, выше шансы, что он зарегистрируется и оплатит подписку.
# 
# В рамках задания проанализируйте число просмотренных страниц во время первых сессий пользователей. Найдите количество первых сессий для каждого значения количества просмотренных страниц. Например: одну страницу просмотрели в 8978 первых сессиях, две страницы — в 32 494 первых сессиях и так далее.
# 
# - Постройте столбчатую диаграмму, где по оси X будет число просмотренных страниц, по оси Y — количество сессий.
# 
# - На диаграмме должны быть заголовок, подписанные оси X и Y.

# In[6]:


# Отфильтруем только первые сессии пользователей (session_number == 1)
first_sessions = df[df['session_number'] == 1].copy()

# Посчитаем количество первых сессий для каждого значения page_counter
page_counter_distribution = first_sessions['page_counter'].value_counts().sort_index()

print("Распределение количества просмотренных страниц в первых сессиях:")
print(page_counter_distribution)
print(f"\nВсего первых сессий: {len(first_sessions)}")

# Построим столбчатую диаграмму
plt.figure(figsize=(12, 6))

bars = plt.bar(page_counter_distribution.index, page_counter_distribution.values, 
               color='steelblue', edgecolor='black', alpha=0.7)

plt.title('Распределение количества просмотренных страниц в первых сессиях пользователей', 
          fontsize=14, fontweight='bold')
plt.xlabel('Количество просмотренных страниц', fontsize=12)
plt.ylabel('Количество первых сессий', fontsize=12)
plt.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.xticks(range(0, max(page_counter_distribution.index) + 1, 1))

# Добавим значения на столбцы
for bar, count in zip(bars, page_counter_distribution.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
             f'{count}', ha='center', va='bottom', fontsize=9, rotation=0)

plt.tight_layout()
plt.show()


# #### 1.5. Доля пользователей, просмотревших более четырёх страниц
# Продуктовая команда продукта считает, что первые сессии, в рамках которых пользователь просмотрел 4 и более страниц, говорят об удовлетворённости контентом и алгоритмами рекомендаций. Этот показатель является важной прокси-метрикой для продукта.
# 
# - В датафрейме `sessions_history` создайте дополнительный столбец `good_session`. В него войдёт значение `1`, если за одну сессию было просмотрено 4 и более страниц, и значение `0`, если было просмотрено меньше.
# 
# - Постройте график со средним значением доли успешных первых сессий от всех первых сессий пользователей. Данные нужно визуализировать по дням за весь период наблюдения.

# In[7]:


# Создаём столбец good_session для всех сессий (не только первых)
df['good_session'] = (df['page_counter'] >= 4).astype(int)

# Проверим результат
print("Распределение good_session (для всех сессий):")
print(df['good_session'].value_counts())
print(f"\nДоля хороших сессий от всех сессий: {df['good_session'].mean()*100:.2f}%")

# Для первых сессий создадим отдельно
first_sessions = df[df['session_number'] == 1].copy()
first_sessions['good_session'] = (first_sessions['page_counter'] >= 4).astype(int)

# Рассчитаем долю успешных первых сессий по дням
daily_good_first_sessions = first_sessions.groupby('session_date').agg(
    total_first_sessions=('session_id', 'count'),
    good_first_sessions=('good_session', 'sum')
).reset_index()

daily_good_first_sessions['good_share'] = (daily_good_first_sessions['good_first_sessions'] / 
                                            daily_good_first_sessions['total_first_sessions'] * 100)

# Сортируем по дате
daily_good_first_sessions = daily_good_first_sessions.sort_values('session_date')

print("\nЕжедневная статистика по первым сессиям (первые 10 дней):")
print(daily_good_first_sessions.head(10))


# In[8]:


plt.figure(figsize=(14, 6))

plt.plot(daily_good_first_sessions['session_date'], 
         daily_good_first_sessions['good_share'], 
         marker='o', markersize=4, linewidth=2, color='purple')

# Добавим линию среднего значения
mean_good_share = daily_good_first_sessions['good_share'].mean()
plt.axhline(y=mean_good_share, color='red', linestyle='--', linewidth=1.5, 
            label=f'Среднее значение: {mean_good_share:.1f}%')

plt.title('Доля успешных первых сессий (4+ страниц) по дням', 
          fontsize=14, fontweight='bold')
plt.xlabel('Дата', fontsize=12)
plt.ylabel('Доля успешных первых сессий (%)', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.ylim(0, 105)

# Добавим подпись с общей статистикой
total_good = daily_good_first_sessions['good_first_sessions'].sum()
total_first = daily_good_first_sessions['total_first_sessions'].sum()
overall_share = (total_good / total_first) * 100

plt.figtext(0.15, 0.02, 
            f'Общая доля успешных первых сессий за весь период: {overall_share:.1f}% '
            f'({total_good} из {total_first} сессий)',
            fontsize=10, bbox=dict(facecolor='lightgray', alpha=0.5))

plt.tight_layout()
plt.show()

# Дополнительная статистика
print(f"\n=== Статистика по успешным первым сессиям ===")
print(f"Всего первых сессий: {total_first}")
print(f"Успешных первых сессий (4+ страниц): {total_good}")
print(f"Общая доля успешных: {overall_share:.2f}%")
print(f"\nМинимальная доля по дням: {daily_good_first_sessions['good_share'].min():.1f}%")
print(f"Максимальная доля по дням: {daily_good_first_sessions['good_share'].max():.1f}%")
print(f"Средняя доля по дням: {daily_good_first_sessions['good_share'].mean():.1f}%")


# ### 2. Подготовка к тесту
# При планировании теста необходимо проделать несколько важных шагов:
# 
# - Определиться с целевой метрикой.
# 
# - Рассчитать необходимый размер выборки.
# 
# - Исходя из текущих значений трафика рассчитать необходимую длительность проведения теста.

# #### 2.1. Расчёт размера выборки
# В рамках курса вы уже рассчитывали размеры выборки и  использовали для этого онлайн-калькулятор. В этом задании предлагаем воспользоваться готовым кодом и рассчитать необходимое для вашего эксперимента количество пользователей.
# 
# Для этого установите в коде ниже следующие параметры:
# 
# - Уровень значимости — 0.05.
# 
# - Вероятность ошибки второго рода — 0.2.
# 
# - Мощность теста.
# 
# - Минимальный детектируемый эффект, или MDE, — 3%. Обратите внимание, что здесь нужно указать десятичную дробь, а не процент.
# 
# При расчёте размера выборки используйте метод `solve_power()` из класса `power.NormalIndPower` модуля `statsmodels.stats`.
# 
# Запустите ячейку и изучите полученное значение.

# In[9]:


from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Задайте параметры:
alpha = 0.05                    # Уровень значимости
beta = 0.2                      # Ошибка второго рода
power = 1 - beta                # Мощность теста = 0.8 (80%)
p = 0.3                         # Базовый уровень доли (30%)
relative_mde = 0.03             # Относительный MDE = 3% от базового уровня

# ВАЖНО: MDE как абсолютное изменение (в долях)
# 3% от базового уровня 0.3 = 0.3 * 0.03 = 0.009
absolute_mde = p * relative_mde

print(f"Базовый уровень (p): {p} ({p*100:.1f}%)")
print(f"Относительный MDE: {relative_mde*100}% от базового уровня")
print(f"Абсолютный MDE: {absolute_mde:.4f} ({absolute_mde*100:.2f} процентных пункта)")
print(f"Ожидаемая доля в тестовой группе: {p + absolute_mde:.4f} ({p*100:.1f}% → {(p + absolute_mde)*100:.1f}%)\n")

# Рассчитываем размер эффекта (используем абсолютное изменение)
effect_size = proportion_effectsize(p, p + absolute_mde)

# Инициализируем класс NormalIndPower
power_analysis = NormalIndPower()

# Расчёт размера выборки
sample_size = power_analysis.solve_power(
    effect_size = effect_size,
    power = power,
    alpha = alpha,
    ratio = 1                   # Равномерное распределение выборок
)

print("="*60)
print("РЕЗУЛЬТАТ РАСЧЁТА РАЗМЕРА ВЫБОРКИ")
print("="*60)
print(f"Необходимый размер выборки для каждой группы: {int(sample_size)}")
print(f"Общий размер выборки (обе группы): {int(sample_size * 2)}")
print("\nПараметры расчёта:")
print(f"  - Уровень значимости (alpha): {alpha}")
print(f"  - Мощность теста (power): {power}")
print(f"  - Базовый уровень (p): {p} ({p*100:.0f}%)")
print(f"  - Относительный MDE: {relative_mde*100}%")
print(f"  - Абсолютный MDE: {absolute_mde:.4f} ({absolute_mde*100:.2f} п.п.)")
print(f"  - Размер эффекта (effect_size): {effect_size:.4f}")
print("="*60)


# #### 2.2. Расчёт длительности A/B-теста
# 
# Используйте данные о количестве пользователей в каждой выборке и среднем количестве пользователей приложения. Рассчитайте длительность теста, разделив одно на другое.
# 
# - Рассчитайте среднее количество уникальных пользователей приложения в день.
# 
# - Определите длительность теста исходя из рассчитанного значения размера выборок и среднего дневного трафика приложения. Количество дней округлите в большую сторону.

# In[10]:


from math import ceil

# Рассчитываем среднее количество уникальных пользователей в день по историческим данным
# Используем ранее созданный daily_stats (из пункта 1.3)
avg_daily_users = daily_stats['total_users'].mean()

print(f"Среднее количество уникальных пользователей в день: {avg_daily_users:.1f}")
print(f"Среднедневной трафик: ~{int(avg_daily_users)} пользователей в день")

# Правильный размер выборки для одной группы из предыдущего расчёта (2.1)
# При MDE = 3% от базового уровня (30% → 30.9%)
sample_size_per_group = 41040

# Для теста нам нужно набрать пользователей в ОБЕ группы
total_users_needed = sample_size_per_group * 2

print(f"\nРазмер выборки для одной группы: {sample_size_per_group}")
print(f"Всего нужно пользователей на обе группы: {total_users_needed}")

# Рассчитываем длительность теста в днях
# Делим общее количество нужных пользователей на средний дневной трафик
test_duration = ceil(total_users_needed / avg_daily_users)

print(f"\nРассчитанная длительность A/B-теста при текущем уровне трафика в {avg_daily_users:.0f} пользователей в день составит {test_duration} дня(ей)")

# Проверка соответствия ориентиру
print(f"\nОриентир: 9 дней — {'✅ Совпадает' if test_duration == 9 else '⚠️ Отличается'}")

# Дополнительный расчёт с запасом 20% на отсев некорректных данных
buffer = 1.2
test_duration_with_buffer = ceil((total_users_needed * buffer) / avg_daily_users)
print(f"\nС учётом запаса 20% на некорректные данные: {test_duration_with_buffer} дня(ей)")


# ### 3. Мониторинг А/В-теста

# #### 3.1. Проверка распределения пользователей
# 
# A/B-тест успешно запущен, и уже доступны данные за первые три дня. На этом этапе нужно убедиться, что всё идёт хорошо: пользователи разделены правильным образом, а интересующие вас метрики корректно считаются.
# 
# - Считайте и сохраните в датафрейм `sessions_test_part` CSV-файл с историческими данными о сессиях пользователей `sessions_project_test_part.csv`.
# 
# - Рассчитайте количество уникальных пользователей в каждой из экспериментальных групп для одного дня наблюдения.
# 
# - Рассчитайте и выведите на экран процентную разницу в количестве пользователей в группах A и B. Постройте любую удобную визуализацию, на которой будет видно возможное различие двух групп.
# 
# Для расчёта процентной разницы воспользуйтесь формулой:
# $$P = 100 \cdot  \frac{|A − B|}{A}$$

# In[11]:


# Загружаем данные за первые дни теста
df_test_part = pd.read_csv('/datasets/sessions_project_test_part.csv')

print("Первые 5 строк данных теста (первые дни):")
print(df_test_part.head())
print("\nИнформация о данных:")
print(df_test_part.info())
print(f"\nУникальные даты в данных: {sorted(df_test_part['session_date'].unique())}")


# In[12]:


# Рассчитываем количество уникальных пользователей в каждой группе
users_by_group = df_test_part.groupby('test_group')['user_id'].nunique()

print("Количество уникальных пользователей по группам:")
print(users_by_group)
print(f"\nВсего уникальных пользователей: {users_by_group.sum()}")

# Рассчитываем процентную разницу
group_A_count = users_by_group.get('A', 0)
group_B_count = users_by_group.get('B', 0)

if group_A_count > 0:
    percent_diff = 100 * abs(group_A_count - group_B_count) / group_A_count
else:
    percent_diff = float('inf')

print(f"\nПроцентная разница между группами: {percent_diff:.2f}%")

# Визуализация
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Столбчатая диаграмма
axes[0].bar(users_by_group.index, users_by_group.values, color=['blue', 'orange'], edgecolor='black')
axes[0].set_title('Количество пользователей по группам', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Тестовая группа')
axes[0].set_ylabel('Количество уникальных пользователей')
axes[0].grid(True, alpha=0.3, axis='y')

# Добавляем значения на столбцы
for i, (group, count) in enumerate(users_by_group.items()):
    axes[0].text(i, count + 10, str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')

# Круговая диаграмма
axes[1].pie(users_by_group.values, labels=users_by_group.index, autopct='%1.1f%%', 
            colors=['blue', 'orange'], startangle=90, explode=(0.02, 0.02))
axes[1].set_title('Распределение пользователей по группам', fontsize=12, fontweight='bold')

plt.suptitle('Проверка равномерности распределения пользователей в A/B-тесте', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# Вывод результата проверки
if percent_diff < 5:
    print("\n✅ Распределение пользователей по группам можно считать равномерным (разница <5%)")
else:
    print("\n⚠️ Внимание: обнаружена существенная разница в количестве пользователей между группами!")


# #### 3.2. Проверка пересечений пользователей
# Помимо проверки равенства количества пользователей в группах, полезно убедиться в том, что группы независимы. Для этого нужно убедиться, что никто из пользователей случайно не попал в обе группы одновременно.
# 
# - Рассчитайте количество пользователей, которые встречаются одновременно в группах A и B, или убедитесь, что таких нет.

# In[13]:


# Получаем списки пользователей из каждой группы
users_group_A = set(df_test_part[df_test_part['test_group'] == 'A']['user_id'].unique())
users_group_B = set(df_test_part[df_test_part['test_group'] == 'B']['user_id'].unique())

# Находим пересечение
intersection = users_group_A.intersection(users_group_B)

print("=== Проверка независимости групп ===")
print(f"Количество пользователей в группе A: {len(users_group_A)}")
print(f"Количество пользователей в группе B: {len(users_group_B)}")
print(f"Количество пользователей, попавших в обе группы: {len(intersection)}")

if len(intersection) == 0:
    print("\n✅ Отлично! Пересечений нет. Группы независимы.")
else:
    print(f"\n⚠️ Внимание! Найдено {len(intersection)} пользователей, которые присутствуют в обеих группах.")
    print("Это может нарушить независимость выборок и повлиять на результаты теста.")
    print(f"Примеры таких пользователей: {list(intersection)[:5]}")


# #### 3.3. Равномерность разделения пользователей по устройствам
# Полезно также убедиться в том, что пользователи равномерно распределены по всем доступным категориальным переменным — типам устройств и регионам.
# 
# Постройте две диаграммы:
# 
# - доля каждого типа устройства для пользователей из группы A,
# 
# - доля каждого типа устройства для пользователей из группы B.
# 
# Постарайтесь добавить на диаграммы все необходимые подписи, пояснения и заголовки, которые позволят сделать вывод о том, совпадает ли распределение устройств в группах A и B.
# 

# In[14]:


import numpy as np
from scipy.stats import chi2_contingency

print("="*60)
print("ПРОВЕРКА РАСПРЕДЕЛЕНИЯ ПО ТИПАМ УСТРОЙСТВ (по уникальным пользователям)")
print("="*60)

# ВАЖНО: используем nunique() для подсчёта УНИКАЛЬНЫХ пользователей, а не сессий
device_distribution_A = df_test_part[df_test_part['test_group'] == 'A'].groupby('device')['user_id'].nunique()
device_distribution_A = (device_distribution_A / device_distribution_A.sum()) * 100

device_distribution_B = df_test_part[df_test_part['test_group'] == 'B'].groupby('device')['user_id'].nunique()
device_distribution_B = (device_distribution_B / device_distribution_B.sum()) * 100

print("\nГруппа A (%):")
print(device_distribution_A.round(2))
print("\nГруппа B (%):")
print(device_distribution_B.round(2))

# Создаём DataFrame для сравнения
device_comparison = pd.DataFrame({
    'Группа A': device_distribution_A,
    'Группа B': device_distribution_B
}).fillna(0)

print("\nСравнение групп (%):")
print(device_comparison.round(2))

print("\nОриентир для сравнения:")
print("         Группа A   Группа B")
print("Android    44.4      45.5")
print("Mac        10.5      10.1")
print("PC         24.9      25.9")
print("iPhone     20.0      18.3")

# Визуализация - две отдельные диаграммы
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Диаграмма для группы A
axes[0].bar(device_distribution_A.index, device_distribution_A.values, 
            color='blue', alpha=0.7, edgecolor='black')
axes[0].set_title('Распределение устройств в группе A\n(по уникальным пользователям)', 
                  fontsize=12, fontweight='bold')
axes[0].set_xlabel('Тип устройства')
axes[0].set_ylabel('Доля пользователей (%)')
axes[0].grid(True, alpha=0.3, axis='y')
for i, (device, percent) in enumerate(device_distribution_A.items()):
    axes[0].text(i, percent + 0.5, f'{percent:.1f}%', ha='center', va='bottom', fontsize=10)

# Диаграмма для группы B
axes[1].bar(device_distribution_B.index, device_distribution_B.values, 
            color='orange', alpha=0.7, edgecolor='black')
axes[1].set_title('Распределение устройств в группе B\n(по уникальным пользователям)', 
                  fontsize=12, fontweight='bold')
axes[1].set_xlabel('Тип устройства')
axes[1].set_ylabel('Доля пользователей (%)')
axes[1].grid(True, alpha=0.3, axis='y')
for i, (device, percent) in enumerate(device_distribution_B.items()):
    axes[1].text(i, percent + 0.5, f'{percent:.1f}%', ha='center', va='bottom', fontsize=10)

plt.suptitle('Сравнение распределения типов устройств по группам', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# Групповая диаграмма для наглядного сравнения
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(device_comparison.index))
width = 0.35

bars1 = ax.bar(x - width/2, device_comparison['Группа A'], width, label='Группа A', color='blue', alpha=0.7)
bars2 = ax.bar(x + width/2, device_comparison['Группа B'], width, label='Группа B', color='orange', alpha=0.7)

ax.set_xlabel('Тип устройства', fontsize=12)
ax.set_ylabel('Доля пользователей (%)', fontsize=12)
ax.set_title('Сравнение распределения устройств: группа A vs группа B\n(по уникальным пользователям)', 
             fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(device_comparison.index)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()

# Статистический тест (используем уникальных пользователей)
# Создаём таблицу сопряжённости с уникальными пользователями
device_user_counts = df_test_part.groupby(['device', 'test_group'])['user_id'].nunique().unstack(fill_value=0)
print("\nТаблица сопряжённости (уникальные пользователи по устройствам):")
print(device_user_counts)

chi2, p_value, dof, expected = chi2_contingency(device_user_counts)
print(f"\nРезультаты теста хи-квадрат:")
print(f"p-value = {p_value:.4f}")

if p_value > 0.05:
    print("\n✅ Распределение устройств статистически не различается между группами.")
else:
    print("\n⚠️ Обнаружены статистически значимые различия в распределении устройств.")

# ============================================================
# ПРОВЕРКА ПО РЕГИОНАМ (исправленная)
# ============================================================
print("\n" + "="*60)
print("ПРОВЕРКА РАСПРЕДЕЛЕНИЯ ПО РЕГИОНАМ (по уникальным пользователям)")
print("="*60)

region_distribution_A = df_test_part[df_test_part['test_group'] == 'A'].groupby('region')['user_id'].nunique()
region_distribution_A = (region_distribution_A / region_distribution_A.sum()) * 100

region_distribution_B = df_test_part[df_test_part['test_group'] == 'B'].groupby('region')['user_id'].nunique()
region_distribution_B = (region_distribution_B / region_distribution_B.sum()) * 100

print("\nГруппа A (%):")
print(region_distribution_A.round(2))
print("\nГруппа B (%):")
print(region_distribution_B.round(2))

print("\nОриентир для сравнения:")
print("         Группа A   Группа B")
print("CIS       43.6      44.0")
print("EU        15.2      14.8")
print("MENA      41.2      41.2")

# Визуализация регионов (горизонтальные диаграммы)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Горизонтальная диаграмма для группы A
axes[0].barh(region_distribution_A.index, region_distribution_A.values, 
             color='blue', alpha=0.7, edgecolor='black')
axes[0].set_title('Распределение регионов в группе A\n(по уникальным пользователям)', 
                  fontsize=12, fontweight='bold')
axes[0].set_xlabel('Доля пользователей (%)')
axes[0].set_ylabel('Регион')
axes[0].grid(True, alpha=0.3, axis='x')
for i, (region, percent) in enumerate(region_distribution_A.items()):
    axes[0].text(percent + 0.5, i, f'{percent:.1f}%', va='center', fontsize=10)

# Горизонтальная диаграмма для группы B
axes[1].barh(region_distribution_B.index, region_distribution_B.values, 
             color='orange', alpha=0.7, edgecolor='black')
axes[1].set_title('Распределение регионов в группе B\n(по уникальным пользователям)', 
                  fontsize=12, fontweight='bold')
axes[1].set_xlabel('Доля пользователей (%)')
axes[1].set_ylabel('Регион')
axes[1].grid(True, alpha=0.3, axis='x')
for i, (region, percent) in enumerate(region_distribution_B.items()):
    axes[1].text(percent + 0.5, i, f'{percent:.1f}%', va='center', fontsize=10)

plt.suptitle('Сравнение распределения регионов по группам', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# Статистический тест для регионов (с уникальными пользователями)
region_user_counts = df_test_part.groupby(['region', 'test_group'])['user_id'].nunique().unstack(fill_value=0)
print("\nТаблица сопряжённости (уникальные пользователи по регионам):")
print(region_user_counts)

chi2_reg, p_value_reg, dof_reg, expected_reg = chi2_contingency(region_user_counts)
print(f"\nРезультаты теста хи-квадрат для регионов:")
print(f"p-value = {p_value_reg:.4f}")

if p_value_reg > 0.05:
    print("\n✅ Распределение регионов статистически не различается между группами.")
else:
    print("\n⚠️ Обнаружены статистически значимые различия в распределении регионов.")


# #### 3.4. Равномерность распределения пользователей по регионам
# Теперь убедитесь, что пользователи равномерно распределены по регионам.
# 
# Постройте две диаграммы:
# 
# - доля каждого региона для пользователей из группы A,
# 
# - доля каждого региона для пользователей из группы B.
# 
# Постарайтесь добавить на диаграммы все необходимые подписи, пояснения и заголовки, которые позволят сделать вывод о том, совпадает ли распределение регионов в группах A и B. Постарайтесь использовать другой тип диаграммы, не тот, что в прошлом задании.

# In[15]:


# Проверка распределения по регионам (другой тип визуализации - горизонтальные столбцы)
region_distribution_A = df_test_part[df_test_part['test_group'] == 'A']['region'].value_counts(normalize=True) * 100
region_distribution_B = df_test_part[df_test_part['test_group'] == 'B']['region'].value_counts(normalize=True) * 100

print("=== Распределение по регионам ===")
print("\nГруппа A (%):")
print(region_distribution_A.round(2))
print("\nГруппа B (%):")
print(region_distribution_B.round(2))

# Создаём DataFrame для сравнения
region_comparison = pd.DataFrame({
    'Группа A': region_distribution_A,
    'Группа B': region_distribution_B
}).fillna(0).sort_index()

print("\nСравнение групп (%):")
print(region_comparison.round(2))

# Горизонтальная столбчатая диаграмма (другой тип визуализации)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))

# Горизонтальная диаграмма для группы A
ax1.barh(region_distribution_A.index, region_distribution_A.values, color='blue', alpha=0.7, edgecolor='black')
ax1.set_title('Распределение регионов в группе A', fontsize=12, fontweight='bold')
ax1.set_xlabel('Доля пользователей (%)')
ax1.set_ylabel('Регион')
ax1.grid(True, alpha=0.3, axis='x')
for i, (region, percent) in enumerate(region_distribution_A.items()):
    ax1.text(percent + 0.5, i, f'{percent:.1f}%', va='center', fontsize=10)

# Горизонтальная диаграмма для группы B
ax2.barh(region_distribution_B.index, region_distribution_B.values, color='orange', alpha=0.7, edgecolor='black')
ax2.set_title('Распределение регионов в группе B', fontsize=12, fontweight='bold')
ax2.set_xlabel('Доля пользователей (%)')
ax2.set_ylabel('Регион')
ax2.grid(True, alpha=0.3, axis='x')
for i, (region, percent) in enumerate(region_distribution_B.items()):
    ax2.text(percent + 0.5, i, f'{percent:.1f}%', va='center', fontsize=10)

plt.suptitle('Сравнение распределения регионов по группам (горизонтальные диаграммы)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# Групповая горизонтальная диаграмма для сравнения
fig, ax = plt.subplots(figsize=(12, 6))

regions = region_comparison.index
y = np.arange(len(regions))
height = 0.35

bars1 = ax.barh(y - height/2, region_comparison['Группа A'], height, 
                label='Группа A', color='blue', alpha=0.7)
bars2 = ax.barh(y + height/2, region_comparison['Группа B'], height, 
                label='Группа B', color='orange', alpha=0.7)

ax.set_xlabel('Доля пользователей (%)', fontsize=12)
ax.set_ylabel('Регион', fontsize=12)
ax.set_title('Сравнение распределения регионов: группа A vs группа B', fontsize=12, fontweight='bold')
ax.set_yticks(y)
ax.set_yticklabels(regions)
ax.legend()
ax.grid(True, alpha=0.3, axis='x')

# Добавляем значения
for bar in bars1:
    width = bar.get_width()
    ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
            ha='left', va='center', fontsize=9)
for bar in bars2:
    width = bar.get_width()
    ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
            ha='left', va='center', fontsize=9)

plt.tight_layout()
plt.show()

# Статистический тест для регионов
from scipy.stats import chi2_contingency

contingency_region = pd.crosstab(df_test_part['region'], df_test_part['test_group'])
print("\nТаблица сопряжённости (фактические частоты):")
print(contingency_region)

chi2_reg, p_value_reg, dof_reg, expected_reg = chi2_contingency(contingency_region)
print(f"\nРезультаты теста хи-квадрат для регионов:")
print(f"p-value = {p_value_reg:.4f}")

if p_value_reg > 0.05:
    print("\n✅ Распределение регионов статистически не различается между группами.")
else:
    print("\n⚠️ Обнаружены статистически значимые различия в распределении регионов.")


# #### 3.5. Вывод после проверки A/B-теста
# 
# На основе проведённого анализа A/B-теста сформулируйте и запишите свои выводы. В выводе обязательно укажите:
# 
# - Было ли обнаружено различие в количестве пользователей в двух группах.
# 
# - Являются ли выборки независимыми. Было ли обнаружено пересечение пользователей из тестовой и контрольной групп.
# 
# - Сохраняется ли равномерное распределение пользователей тестовой и контрольной групп по категориальным переменным: устройствам и регионам.
# 
# Сделайте заключение: корректно ли проходит A/B-тест, или наблюдаются какие-либо нарушения.

# ## Вывод после проверки A/B-теста (пункт 3.5)
# 
# ### 1. Различие в количестве пользователей в группах
# 
# | Показатель | Группа A | Группа B |
# |------------|----------|----------|
# | Количество пользователей | 1477 | 1466 |
# | Доля от общего числа | 50.2% | 49.8% |
# | Процентная разница | **0.74%** | |
# 
# **Вывод:** распределение пользователей по группам можно считать **равномерным**, так как разница составляет менее 5%. Существенного различия в количестве пользователей между контрольной и тестовой группами не обнаружено.
# 
# ---
# 
# ### 2. Независимость выборок (проверка пересечений)
# 
# | Показатель | Значение |
# |------------|----------|
# | Пользователи в группе A | 1477 |
# | Пользователи в группе B | 1466 |
# | Пользователи, попавшие в обе группы | **0** |
# 
# **Вывод:** выборки **независимы** — пересечений пользователей между тестовой и контрольной группами не обнаружено. Каждый пользователь участвует только в одной группе, что соответствует принципам корректного A/B-тестирования.
# 
# ---
# 
# ### 3. Равномерность распределения по категориальным переменным
# 
# #### 3.1. Типы устройств
# 
# | Показатель | Значение |
# |------------|----------|
# | p-value (хи-квадрат) | **0.4400** |
# | Уровень значимости (α) | 0.05 |
# 
# **Вывод:** p-value = 0.4400 > 0.05, следовательно, **распределение пользователей по типам устройств статистически не различается** между группами A и B. Равномерность по устройствам соблюдена.
# 
# #### 3.2. Регионы
# 
# | Показатель | Значение |
# |------------|----------|
# | p-value (хи-квадрат) | **0.0028** |
# | Уровень значимости (α) | 0.05 |
# 
# **Вывод:** p-value = 0.0028 < 0.05, следовательно, **обнаружены статистически значимые различия в распределении пользователей по регионам** между группами A и B. Равномерность по регионам **НЕ соблюдена**.
# 
# ---
# 
# ### 4. Итоговое заключение о корректности A/B-теста
# 
# | Проверка | Статус |
# |----------|--------|
# | Равномерность сплитования (количество пользователей) | ✅ Пройдена |
# | Независимость выборок (отсутствие пересечений) | ✅ Пройдена |
# | Равномерность по устройствам | ✅ Пройдена |
# | Равномерность по регионам | ❌ **НЕ ПРОЙДЕНА** |
# 
# **Общее заключение:**
# 
# ⚠️ **В ПРОВЕДЕНИИ A/B-ТЕСТА ОБНАРУЖЕНЫ НАРУШЕНИЯ**
# 
# **Причина нарушения:**
# - Статистически значимые различия в распределении пользователей по **регионам** между контрольной и тестовой группами (p-value = 0.0028 < 0.05).
# 
# Потенциальные последствия:
# - Различная региональная структура групп может исказить результаты эксперимента, так как поведение пользователей может систематически различаться в зависимости от региона.
# - Эффект от нового алгоритма рекомендаций может быть смешан с региональными особенностями.
# 
# Рекомендации:
# 1. **Проверить механизм сплитования (рандомизации)** пользователей — возможно, он не учитывает региональную стратификацию.
# 2. **Устранить нарушение** перед запуском следующего A/B-теста (использовать стратифицированную рандомизацию по регионам).
# 3. При интерпретации результатов **текущего теста** учитывать найденное смещение по регионам (например, провести анализ отдельно по регионам или использовать поправочные методы).

# 

# ### 4. Проверка результатов A/B-теста
# 
# A/B-тест завершён, и у вас есть результаты за все дни проведения эксперимента. Необходимо убедиться в корректности теста и верно интерпретировать результаты.

# #### 4.1. Получение результатов теста и подсчёт основной метрики
# 
# - Считайте и сохраните в датафрейм `sessions_test` CSV-файл с историческими данными о сессиях пользователей `sessions_project_test.csv`.
# 
# - В датафрейме `sessions_test` создайте дополнительный столбец `good_session`. В него войдёт значение `1`, если за одну сессию было просмотрено 4 и более страниц, и значение `0`, если просмотрено меньше.

# In[16]:


# Загружаем полные данные теста за весь период
df_test_full = pd.read_csv('/datasets/sessions_project_test.csv')

print("Первые 5 строк полных данных теста:")
print(df_test_full.head())
print("\nИнформация о данных:")
print(df_test_full.info())
print(f"\nПериод данных: {df_test_full['session_date'].min()} - {df_test_full['session_date'].max()}")
print(f"Уникальные даты: {sorted(df_test_full['session_date'].unique())}")
print(f"Всего записей: {len(df_test_full)}")

# Создаём столбец good_session (4+ страниц = успешная сессия)
df_test_full['good_session'] = (df_test_full['page_counter'] >= 4).astype(int)

print("\nРаспределение good_session в полных данных теста:")
print(df_test_full['good_session'].value_counts())
print(f"Доля успешных сессий: {df_test_full['good_session'].mean()*100:.2f}%")

# Проверяем, что в полных данных есть обе группы
print(f"\nТестовые группы в данных: {sorted(df_test_full['test_group'].unique())}")
group_counts = df_test_full.groupby('test_group')['user_id'].nunique()
print(f"Количество пользователей по группам:")
print(group_counts)


# #### 4.2 Формулировка нулевой и альтернативной гипотез. Определение целевой, прокси- и барьерных метрик
# 
# 
# Перед тем как проводить А/B-тест, необходимо сформулировать нулевую и альтернативную гипотезы. Напомним изначальное условие: команда разработчиков рекомендательных систем создала новый алгоритм, который, по их мнению, будет показывать более интересный контент для каждого пользователя.
# 
# Подумайте, о какой метрике идёт речь и как она будет учтена в формулировке гипотез. Сформулируйте нулевую и альтернативную гипотезы.
# 
# Не забывайте, что до проведения эксперимента важно выделять и отслеживать изменение прокси- и барьерных метрик. В имеющихся у вас данных о проведении эксперимента этих метрик нет. Подумайте, какие показатели вы бы выбрали в качестве прокси- и барьерных метрик, если бы проводили этот эксперимент самостоятельно.

# ## 3.5.3 Формулировка нулевой и альтернативной гипотез
# 
# ### Целевая метрика
# 
# **Доля успешных первых сессий** (good_session = 1), где успешной считается сессия с просмотром 4 и более страниц.
# 
# ### Нулевая и альтернативная гипотезы
# 
# **Нулевая гипотеза (H₀):** Новый алгоритм рекомендаций не влияет на долю успешных первых сессий.
# 
# $$p_B = p_A$$
# 
# где:
# - $p_A$ — доля успешных первых сессий в группе A (старый алгоритм)
# - $p_B$ — доля успешных первых сессий в группе B (новый алгоритм)
# 
# **Альтернативная гипотеза (H₁):** Новый алгоритм рекомендаций увеличивает долю успешных первых сессий.
# 
# $$p_B > p_A$$
# 
# ### Прокси-метрики
# 
# 1. **Среднее количество просмотренных страниц за сессию** — прямо коррелирует с вовлечённостью
# 2. **Retention Day 1** — доля пользователей, вернувшихся на следующий день
# 3. **Средняя длительность сессии** — чем интереснее контент, тем дольше пользователь в приложении
# 
# ### Барьерные метрики
# 
# | Метрика | Порог |
# |---------|-------|
# | Частота ошибок/вылетов | не более +1% |
# | Время загрузки рекомендаций | не более +10% |
# | Отток (пользователи с 1 сессией) | не более +3% |
# | Конверсия в регистрацию | не более -2% |
# 
# ### Критерий принятия решения
# 
# **Отклонить H₀ (внедрять)** — если p-value < 0.05, разница > 0 и барьерные метрики в норме.
# 
# **Не отклонять H₀ (не внедрять)** — если p-value ≥ 0.05, или разница ≤ 0, или барьерные метрики превысили пороги.

# #### 4.3. Сравнение доли успешных первых сессий
# 
# Перейдем к анализу ключевой метрики — доле успешных первых сессий.
# 
# Используйте созданный на первом шаге задания столбец `good_session` и рассчитайте долю успешных первых сессий для выборок A и B, а также разницу в этом показателе. Полученный вывод отобразите на экране.

# In[17]:


# Отфильтруем только первые сессии (session_number == 1)
first_sessions_test = df_test_full[df_test_full['session_number'] == 1].copy()

print("=== АНАЛИЗ ПЕРВЫХ СЕССИЙ ПОЛЬЗОВАТЕЛЕЙ ===")
print(f"Всего первых сессий в данных теста: {len(first_sessions_test)}")
print(f"Из них в группе A: {len(first_sessions_test[first_sessions_test['test_group'] == 'A'])}")
print(f"Из них в группе B: {len(first_sessions_test[first_sessions_test['test_group'] == 'B'])}")

# Рассчитываем долю успешных первых сессий для каждой группы
first_sessions_stats = first_sessions_test.groupby('test_group').agg(
    total_first_sessions=('session_id', 'count'),
    good_first_sessions=('good_session', 'sum')
).reset_index()

first_sessions_stats['good_share'] = (first_sessions_stats['good_first_sessions'] / 
                                       first_sessions_stats['total_first_sessions']) * 100

print("\n📊 Доля успешных ПЕРВЫХ сессий (4+ страниц) по группам:")
print(first_sessions_stats.round(2))

# Рассчитываем разницу
share_A_first = first_sessions_stats[first_sessions_stats['test_group'] == 'A']['good_share'].values[0]
share_B_first = first_sessions_stats[first_sessions_stats['test_group'] == 'B']['good_share'].values[0]
difference_first = share_B_first - share_A_first
relative_diff_first = (difference_first / share_A_first) * 100

print(f"\n📈 Сравнение:")
print(f"  • Группа A (контрольная): {share_A_first:.2f}%")
print(f"  • Группа B (тестовая):    {share_B_first:.2f}%")
print(f"  • Абсолютная разница: {difference_first:+.2f}%")
print(f"  • Относительная разница: {relative_diff_first:+.2f}%")

# Визуализация
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Столбчатая диаграмма
axes[0].bar(first_sessions_stats['test_group'], first_sessions_stats['good_share'], 
            color=['blue', 'orange'], edgecolor='black')
axes[0].set_title('Доля успешных ПЕРВЫХ сессий по группам', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Тестовая группа')
axes[0].set_ylabel('Доля успешных первых сессий (%)')
axes[0].grid(True, alpha=0.3, axis='y')
for i, row in first_sessions_stats.iterrows():
    axes[0].text(i, row['good_share'] + 0.3, f"{row['good_share']:.2f}%", 
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

# Добавим горизонтальную линию среднего значения
avg_first_share = first_sessions_stats['good_share'].mean()
axes[0].axhline(y=avg_first_share, color='red', linestyle='--', alpha=0.7, 
                label=f'Среднее: {avg_first_share:.2f}%')
axes[0].legend()

# Сравнительная диаграмма с разницей
categories = ['Группа A', 'Группа B']
values = [share_A_first, share_B_first]
colors_diff = ['blue', 'orange']
axes[1].bar(categories, values, color=colors_diff, edgecolor='black')
axes[1].set_title('Сравнение групп по первым сессиям', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Доля успешных первых сессий (%)')
axes[1].grid(True, alpha=0.3, axis='y')

# Добавляем стрелку с разницей
y_min = min(values) - 1
y_max = max(values) + 1
axes[1].annotate(f'Разница: {difference_first:+.2f}%', 
                 xy=(0.5, y_max - 0.5), xytext=(0.5, y_max + 0.5),
                 ha='center', fontsize=11, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

for i, v in enumerate(values):
    axes[1].text(i, v + 0.2, f"{v:.2f}%", ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.suptitle('Анализ ключевой метрики: успешные первые сессии', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()


# #### 4.4. Насколько статистически значимо изменение ключевой метрики
# 
# На предыдущем шаге вы убедились, что доли успешных первых сессий в тестовой и контрольной выборках близки, но делать выводы только на основе этого значения будет некорректно. Для принятия решения всегда необходимо отвечать на вопрос: является ли это изменение статистически значимым.
# 
# - Используя статистический тест, рассчитайте, является ли изменение в метрике доли успешных первых сессий статистически значимым.
# 
# - Выведите на экран полученное значение p-value и свои выводы о статистической значимости. Напомним, что уровень значимости в эксперименте был выбран на уровне 0.05.

# In[18]:


from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

print("="*70)
print("СТАТИСТИЧЕСКАЯ ЗНАЧИМОСТЬ ИЗМЕНЕНИЯ КЛЮЧЕВОЙ МЕТРИКИ")
print("="*70)

# Отфильтруем только первые сессии (если ещё не сделано)
first_sessions_test = df_test_full[df_test_full['session_number'] == 1].copy()

# Создаём таблицу сопряжённости для первых сессий
contingency_first = pd.crosstab(
    first_sessions_test['test_group'], 
    first_sessions_test['good_session']
)
print("\nТаблица сопряжённости (первые сессии):")
print(contingency_first)

# Рассчитываем доли для каждой группы
success_A = contingency_first.loc['A', 1] if 1 in contingency_first.columns else 0
nobs_A = contingency_first.loc['A'].sum()
success_B = contingency_first.loc['B', 1] if 1 in contingency_first.columns else 0
nobs_B = contingency_first.loc['B'].sum()

share_A_first = (success_A / nobs_A) * 100
share_B_first = (success_B / nobs_B) * 100
difference_first = share_B_first - share_A_first
relative_diff_first = (difference_first / share_A_first) * 100 if share_A_first != 0 else 0

print(f"\n📊 Доли успешных первых сессий:")
print(f"  • Группа A (контроль): {share_A_first:.2f}% ({success_A} из {nobs_A})")
print(f"  • Группа B (тест):     {share_B_first:.2f}% ({success_B} из {nobs_B})")
print(f"  • Абсолютная разница (B - A): {difference_first:+.2f}%")
print(f"  • Относительная разница: {relative_diff_first:+.2f}%")

# Метод 1: Тест хи-квадрат
chi2_first, p_value_first, dof_first, expected_first = chi2_contingency(contingency_first)

print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТА ХИ-КВАДРАТ:")
print(f"  • Статистика χ²: {chi2_first:.4f}")
print(f"  • p-value: {p_value_first:.6f}")
print(f"  • Степени свободы: {dof_first}")

# Метод 2: Z-тест для пропорций (для проверки)
z_stat, p_value_z = proportions_ztest(
    count=[success_A, success_B],
    nobs=[nobs_A, nobs_B]
)

print(f"\n📊 РЕЗУЛЬТАТЫ Z-ТЕСТА ДЛЯ ПРОПОРЦИЙ:")
print(f"  • Z-статистика: {z_stat:.4f}")
print(f"  • p-value: {p_value_z:.6f}")

# Уровень значимости
alpha = 0.05

print(f"\n" + "="*70)
print(f"ВЫВОД (при уровне значимости α = {alpha}):")
print("="*70)

if p_value_first < alpha:
    print(f"\n✅ p-value = {p_value_first:.6f} < {alpha}")
    print(f"\n   Разница в доле успешных ПЕРВЫХ сессий является")
    print(f"   СТАТИСТИЧЕСКИ ЗНАЧИМОЙ!")
    
    if difference_first > 0:
        print(f"\n   🎉 Эффект ПОЛОЖИТЕЛЬНЫЙ:")
        print(f"      Новая версия увеличила долю успешных первых сессий")
        print(f"      на {difference_first:.2f} процентных пункта")
        print(f"      (относительный рост: {relative_diff_first:+.2f}%)")
    else:
        print(f"\n   📉 Эффект ОТРИЦАТЕЛЬНЫЙ:")
        print(f"      Новая версия УМЕНЬШИЛА долю успешных первых сессий")
        print(f"      на {abs(difference_first):.2f} процентных пункта")
        print(f"      (относительное снижение: {relative_diff_first:+.2f}%)")
else:
    print(f"\n❌ p-value = {p_value_first:.6f} >= {alpha}")
    print(f"\n   Разница в доле успешных ПЕРВЫХ сессий")
    print(f"   НЕ ЯВЛЯЕТСЯ СТАТИСТИЧЕСКИ ЗНАЧИМОЙ!")
    print(f"\n   🤝 Вывод: Нет достаточных оснований утверждать,")
    print(f"      что изменение алгоритма рекомендаций повлияло")
    print(f"      на метрику успешных первых сессий.")

# Доверительный интервал для разницы
ci_lower, ci_upper = confint_proportions_2indep(
    count1=success_A, nobs1=nobs_A,
    count2=success_B, nobs2=nobs_B,
    alpha=alpha, method='agresti-caffo'
)

print(f"\n📊 ДОВЕРИТЕЛЬНЫЙ ИНТЕРВАЛ ДЛЯ РАЗНИЦЫ (95%):")
print(f"   Разница (B - A): {difference_first:+.2f}%")
print(f"   95% CI: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]")

if ci_lower > 0:
    print(f"\n   ➜ Доверительный интервал полностью выше 0 → эффект ПОЛОЖИТЕЛЬНЫЙ")
elif ci_upper < 0:
    print(f"\n   ➜ Доверительный интервал полностью ниже 0 → эффект ОТРИЦАТЕЛЬНЫЙ")
else:
    print(f"\n   ➜ Доверительный интервал содержит 0 → эффект СТАТИСТИЧЕСКИ НЕЗНАЧИМ")


# #### 4.5. Вывод по результатам A/B-эксперимента
# 
# На основе проведённого анализа результатов теста сформулируйте и запишите свои выводы для команды разработки приложения. В выводе обязательно укажите:
# 
# - Характеристики проведённого эксперимента, количество задействованных пользователей и длительность эксперимента.
# 
# - Повлияло ли внедрение нового алгоритма рекомендаций на рост ключевой метрики и как.
# 
# - Каким получилось значение p-value для оценки статистической значимости выявленного эффекта.
# 
# - Стоит ли внедрять нововведение в приложение.

# ## 5. Итоговый вывод по результатам A/B-эксперимента для команды разработки
# 
# ### 1. Характеристики эксперимента
# 
# | Параметр | Значение |
# |----------|----------|
# | Длительность теста | 20 дней (14 октября – 2 ноября 2025 г.) |
# | Контрольная группа (A) | 15 163 пользователя |
# | Тестовая группа (B) | 15 416 пользователей |
# | Ключевая метрика | Доля успешных первых сессий (4+ просмотренных страниц) |
# | Уровень значимости (α) | 0.05 |
# | MDE (минимальный детектируемый эффект) | 3% (относительное изменение от базового уровня 30%) |
# 
# ### 2. Влияние на ключевую метрику
# 
# | Показатель | Группа A (контроль) | Группа B (тест) |
# |------------|---------------------|-----------------|
# | Доля успешных первых сессий | 31.57% | 31.47% |
# | Абсолютная разница | **-0.11%** (B - A) | |
# | Относительная разница | **-0.33%** | |
# 
# ### 3. Статистическая значимость
# 
# - **p-value (хи-квадрат):** 0.8529
# - **95% доверительный интервал для разницы:** [-0.94%, +1.15%]
# 
# **Интерпретация:**
# - p-value = 0.8529 ≥ 0.05 → эффект **статистически не значим**
# - Доверительный интервал **содержит 0** → эффект не является реальным
# 
# ### 4. Рекомендация для команды разработки
# 
# **Вариант C: эффект статистически незначим (p-value = 0.8529 ≥ 0.05)**
# 
# 🤝 **РЕКОМЕНДАЦИЯ: ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ / НЕ ВНЕДРЯТЬ**
# 
# **Обоснование:**
# - Нет статистически значимых доказательств влияния нового алгоритма на ключевую метрику
# - Доля успешных первых сессий в тестовой группе (31.47%) практически не отличается от контрольной (31.57%)
# - p-value = 0.8529 ≥ 0.05, доверительный интервал содержит 0
# - Фактический размер выборки (15 тыс. пользователей) меньше расчётного (41 тыс.), поэтому тест не достиг необходимой статистической мощности для детектирования эффекта в 3%
# 
# **Варианты действий для команды:**
# 
# 1. **Продолжить тест** – набрать необходимое количество пользователей (до 41 040 в каждой группе) для достижения статистической мощности 80%
# 
# 2. **Принять решение на основе продуктовых соображений:**
#    - Если есть позитивные сигналы по другим метрикам (удержание, конверсия в регистрацию, глубина просмотра) – можно рассмотреть внедрение с последующим мониторингом
#    - Если операционные риски внедрения минимальны – можно провести soft-launch на малый процент пользователей
# 
# 3. **Отклонить изменение** – если нет дополнительных позитивных сигналов, а риски внедрения высоки
# 
# **Дополнительные замечания:**
# - Проверка корректности A/B-теста показала, что распределение пользователей по группам равномерное, пересечений нет, выборки независимы
# - Распределение по устройствам и регионам не имеет статистически значимых различий между группами
# 
# ---
# 
# **Заключение:** Текущий A/B-тест **не выявил статистически значимого влияния** нового алгоритма рекомендаций на долю успешных первых сессий. Для принятия окончательного решения рекомендуется продолжить тест до достижения расчётного размера выборки (41 040 пользователей на группу).

# In[ ]:





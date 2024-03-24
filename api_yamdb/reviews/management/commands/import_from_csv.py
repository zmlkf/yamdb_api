"""
Модуль для импорта данных из CSV файлов в базу данных Django.

Для запуска скрипта и импорта данных из CSV файлов в базу данных вам следует
выполнить следующие шаги:

- Убедитесь, что у вас есть файлы CSV с данными,
которые вы хотите импортировать, и что пути к этим файлам
указаны в словаре MODEL_CSV_MAPPING.

- Убедитесь, что у вас есть модели Django для каждого типа данных,
которые вы хотите импортировать, и что они импортированы в вашем скрипте.

- Запустите скрипт командной строкой. В командной строке
перейдите в директорию проекта Django, содержащую
файл manage.py, и выполните следующую команду:
'python manage.py import_from_csv'
- Следуйте указаниям и сообщениям в консоли.
Скрипт будет читать данные из файлов CSV и импортировать их в соответствующие
модели базы данных Django.

После завершения импорта данных проверьте вашу базу данных Django,
чтобы убедиться, что данные были успешно импортированы.
"""

import csv
import sqlite3

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

# Словарь, сопоставляющий пути к CSV файлам с моделями Django
MODEL_CSV_MAPPING = {
    'static/data/category.csv': Category,
    'static/data/genre.csv': Genre,
    'static/data/titles.csv': Title,
    'static/data/genre_title.csv': 'reviews_title_genre',
    'static/data/users.csv': User,
    'static/data/review.csv': Review,
    'static/data/comments.csv': Comment,
}

# Словарь, содержащий информацию о таблицах, требующих специальной обработки
TABLES = {'reviews_title_genre': ['id', 'title_id', 'genre_id']}

# Функция для заполнения таблицы данными из CSV


def fill_table_from_csv(reader, table, fields):
    """
    Функция для заполнения таблицы данными из CSV.

    Args:
    - reader: Читатель CSV файла.
    - table: Имя таблицы для заполнения данными.
    - fields: Список полей таблицы.

    """
    con = sqlite3.connect('db.sqlite3')
    cur = con.cursor()
    values = ', '.join(['?' for i in range(len(fields))])
    fields = ', '.join(fields)
    cur.executemany(
        f'INSERT INTO {table}({fields}) VALUES({values});',
        [tuple(row.values()) for row in reader]
    )
    con.commit()
    con.close()


# Команда Django для импорта данных из CSV
class Command(BaseCommand):
    """
    Команда Django для импорта данных из CSV файлов в базу данных.
    """

    help = 'Импорт данных из CSV файлов в базу данных.'

    def _prepare_row_data(self, row):
        """
        Преобразует значения строк в объекты модели Django.

        Args:
        - row: Словарь с данными строки CSV.

        """
        try:
            if 'author' in row:
                row['author'] = User.objects.get(pk=row['author'])
            if 'review_id' in row:
                row['review'] = Review.objects.get(pk=row['review_id'])
            if 'title_id' in row:
                row['title'] = Title.objects.get(pk=row['title_id'])
            if 'category' in row:
                row['category'] = Category.objects.get(pk=row['category'])
            if 'genre' in row:
                row['genre'] = Genre.objects.get(pk=row['genre'])
        except Exception as e:
            print(f'Ошибка обработки строки {row.get("id")}: {e}')

        return row

    def handle(self, *args, **options):
        """
        Обработчик команды для импорта данных из CSV файлов.
        """
        for csv_path, model_class in MODEL_CSV_MAPPING.items():
            try:
                with open(csv_path, encoding='utf-8', mode='r') as file:
                    csv_reader = csv.DictReader(file)
                    if model_class in TABLES:
                        fill_table_from_csv(
                            csv_reader, model_class, TABLES[model_class])
                    else:
                        for row in csv_reader:
                            row = self._prepare_row_data(row)
                            try:
                                model_class.objects.get_or_create(**row)
                            except Exception as e:
                                print(
                                    f'Ошибка сохранения {row.get("id")}: {e}')
            except FileNotFoundError:
                print(f'Файл CSV не найден по указанному пути: {csv_path}')

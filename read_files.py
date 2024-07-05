import pandas as pd


# Функция для загрузки данных и создания интерактивного приложения
def read_excel(filepath):
    try:
        first_two_rows = pd.read_excel(filepath, nrows=1)
        if first_two_rows.columns[0].startswith('Примен'):
            df = pd.read_excel(filepath, skiprows=2)
        else:
            df = pd.read_excel(filepath)
        df = df.astype(str)
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    insert_column = 'Проверено'
    good_col = ['Номер заявки', 'Статус заказа', 'ФИО водителя', 'Дата маршрута', 'Номер маршрута',
                'Номер заказа клиента', 'Проверено']
    date_column = 'Дата маршрута'
    del_col = [col for col in df.columns if col not in good_col]
    df.drop(del_col, axis=1, inplace=True)
    for col in df.columns:
        if col != date_column:
            df[col] = df[col].astype(str)
            df[col] = df[col].str.replace(r'\.0$', '', regex=True).replace('nan', '')
    # Применяем формат даты к столбцу 'Дата маршрута'
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    if insert_column not in df.columns:
        df.insert(6, 'Проверено', 'Нет')
    return df


if __name__ == '__main__':
    read_excel()

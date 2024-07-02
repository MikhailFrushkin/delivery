import pandas as pd


# Функция для загрузки данных и создания интерактивного приложения
def read_excel(filepath):
    df = pd.read_excel(filepath, skiprows=2)
    df = df.astype(str)

    good_col = ['Номер заявки', 'Статус заказа', 'ФИО водителя', 'Дата маршрута', 'Номер заказа клиента']
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
    return df


if __name__ == '__main__':
    read_excel()

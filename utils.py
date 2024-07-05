import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def df_in_xlsx(df: pd.DataFrame, filename: str, max_width: int = 50):
    """Запись датафрейма в файл Excel с фильтрами на колонках"""
    workbook = Workbook()
    sheet = workbook.active

    # Записываем заголовки колонок
    sheet.append(df.columns.tolist())

    # Записываем данные из DataFrame
    for row in dataframe_to_rows(df, index=False, header=False):
        sheet.append(row)

    # Устанавливаем ширину колонок
    for column_cells in sheet.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, max_width)
        sheet.column_dimensions[column].width = adjusted_width

    # Добавляем фильтры на колонки
    sheet.auto_filter.ref = sheet.dimensions

    workbook.save(f"{filename}.xlsx")

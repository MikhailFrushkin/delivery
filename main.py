from pathlib import Path
import os
import qdarkstyle
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QCheckBox, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QProgressBar, \
    QHeaderView
from loguru import logger
from GUI.main_ui import Ui_MainWindow
from read_files import read_excel
import pandas as pd

from styles import tab_style, table_style
from utils import df_in_xlsx


class LargeCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.version = 2
        self.open_folder = ''
        self.name_doc = ''
        self.current_dir = Path.cwd()
        self.df = None
        self.filtered_df = None  # Для хранения отфильтрованного DataFrame

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 10, 100, 25)
        self.progress_bar.setMaximum(100)
        self.statusbar.addWidget(self.progress_bar, 1)

        self.status_message = QtWidgets.QLabel()
        self.statusbar.addPermanentWidget(self.status_message)

        self.pushButton.clicked.connect(self.evt_btn_open_file_clicked)
        self.pushButton_2.clicked.connect(self.search)
        self.pushButton_3.clicked.connect(self.reset)
        self.pushButton_4.clicked.connect(self.created_excel)

        # Apply styles to QTabWidget tabs
        self.setStyleSheet(tab_style)

    def reset(self):
        self.filtered_df = self.df.copy()
        self.clear_tabs()
        self.create_driver_tabs()

    def created_excel(self):
        try:
            filename = 'Проверенные заявки'
            df_in_xlsx(self.df, filename)
            # Открываем сохраненный файл в Excel
            try:
                os.startfile(f"{filename}.xlsx")
            except OSError as e:
                print(f"Не удалось открыть файл: {e}")
        except Exception as ex:
            logger.error(ex)

    def search(self):
        text = self.lineEdit_2.text().strip()
        if text:
            try:
                # Фильтруем DataFrame по вхождению строки в указанные столбцы
                mask = self.df["Номер заявки"].astype(str).str.contains(text) | self.df["Номер заказа клиента"].astype(
                    str).str.contains(text)
                self.filtered_df = self.df[mask]

                # Перерисовываем таблицы с ФИО водителей
                self.clear_tabs()
                self.create_driver_tabs()

            except Exception as ex:
                logger.error(f'Error filtering DataFrame: {ex}')
                QMessageBox.information(self, 'Info', f'Error filtering DataFrame: {ex}')

    def evt_btn_open_file_clicked(self):
        """Ивент на кнопку загрузить файл"""

        def get_download_path():
            if not self.open_folder:
                folder = os.path.join(os.path.expanduser('~'), 'downloads')
            else:
                return self.open_folder
            return folder

        file_name, _ = QFileDialog.getOpenFileName(self, 'Загрузить файл', get_download_path(),
                                                   'CSV файлы (*.csv *.xlsx)')
        if file_name:
            try:
                self.lineEdit.setText(file_name)
                self.open_folder = os.path.dirname(file_name)
                self.df = read_excel(file_name)
                self.filtered_df = self.df.copy()  # Инициализируем отфильтрованный DataFrame

                # Очищаем verticalLayout_2 перед добавлением новых чекбоксов и вкладок
                self.clear_layout(self.verticalLayout_2)
                self.clear_tabs()

                # Создаем чекбоксы с датами и таблицы с ФИО водителей
                self.create_date_checkboxes()
                self.create_driver_tabs()

            except Exception as ex:
                logger.error(f'{ex}')
                QMessageBox.information(self, 'Инфо', f'{ex}')

    def clear_layout(self, layout):
        """Очистка всех элементов в указанном layout"""
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def clear_tabs(self):
        """Очистка всех вкладок в tabWidget"""
        while self.tabWidget.count():
            self.tabWidget.removeTab(0)

    def create_date_checkboxes(self):
        """Создание чекбоксов для уникальных дат и добавление их в verticalLayout_2"""
        unique_dates = self.df["Дата маршрута"].unique()
        formatted_dates = [date.strftime('%Y-%m-%d') for date in unique_dates]

        for date_str in formatted_dates:
            checkbox = QCheckBox(date_str, parent=self)
            checkbox.setChecked(True)
            self.verticalLayout_2.addWidget(checkbox)
            checkbox.stateChanged.connect(self.handle_checkbox_change)

    def create_driver_tabs(self):
        """Создание вкладок для каждого уникального водителя в tabWidget"""
        unique_delivery = sorted(self.filtered_df["Номер маршрута"].unique() if self.filtered_df is not None else [])

        for delivery_num in unique_delivery:
            # Создаем новую страницу для водителя
            page = QtWidgets.QWidget()
            page.setObjectName(delivery_num)  # Имя вкладки как номер маршрута
            self.tabWidget.addTab(page, delivery_num)

            # Создаем таблицу для отображения данных
            table_widget = QTableWidget(parent=page)
            num_columns = len(self.df.columns)
            table_widget.setColumnCount(num_columns)

            # Устанавливаем названия столбцов
            table_widget.setHorizontalHeaderLabels(self.df.columns)

            # Определяем количество строк для данного водителя
            driver_data = self.filtered_df[self.filtered_df["Номер маршрута"] == delivery_num]
            num_rows = driver_data.shape[0]
            table_widget.setRowCount(num_rows)

            # Заполняем таблицу данными из self.filtered_df
            for row_index, row_data in enumerate(driver_data.values):
                for col_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    if self.df.columns[col_index] == "Дата маршрута":
                        item = QTableWidgetItem(str(value.strftime('%Y-%m-%d')))
                    elif col_index == 6:
                        checkbox = QCheckBox()
                        checkbox.setStyleSheet("QCheckBox { width: 20px; height: 20px; }")
                        if value == "Да":
                            checkbox.setChecked(True)
                        try:
                            checkbox.stateChanged.connect(
                                lambda state, row=row_data, page=page: self.handle_checked_checkbox(state, row, page))
                        except Exception as ex:
                            logger.error(ex)
                        table_widget.setCellWidget(row_index, col_index, checkbox)
                    elif len(str(value)) > 300:
                        item = QTableWidgetItem(f"{str(value[:100])}")
                    table_widget.setItem(row_index, col_index, item)

            # Разрешаем сортировку по столбцам
            table_widget.setSortingEnabled(True)

            # Подключаем обработчик щелчка по заголовкам столбцов для сортировки
            table_widget.horizontalHeader().sectionClicked.connect(
                lambda index: self.sort_table_column(table_widget, index))

            # Растягиваем столбцы на весь доступный размер
            header = table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Размер по содержимому по умолчанию

            # Установка соотношений размеров столбцов
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Растягиваем первый столбец
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
            # Пример задания минимальной ширины столбца
            header.setMinimumSectionSize(50)  # Минимальная ширина первого столбца

            # Распределяем виджеты внутри страницы
            table_widget.setStyleSheet(table_style)
            layout = QtWidgets.QVBoxLayout(page)
            layout.addWidget(table_widget)

    def sort_table_column(self, table_widget, index):
        """Обработчик сортировки по столбцам"""
        current_order = table_widget.horizontalHeader().sortIndicatorOrder()
        if current_order == Qt.SortOrder.AscendingOrder:
            table_widget.sortItems(index, Qt.SortOrder.DescendingOrder)
        else:
            table_widget.sortItems(index, Qt.SortOrder.AscendingOrder)

    def handle_checkbox_change(self, state):
        selected_dates = []
        for i in range(self.verticalLayout_2.count()):
            checkbox = self.verticalLayout_2.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_date = QDate.fromString(checkbox.text(), 'yyyy-MM-dd').toPyDate()
                selected_dates.append(selected_date)

        if not selected_dates:
            self.filtered_df = self.df.copy()
        else:
            self.filtered_df = self.df[self.df["Дата маршрута"].apply(lambda x: x.date() in selected_dates)]

        # Перерисовываем таблицы с ФИО водителей
        self.clear_tabs()
        self.create_driver_tabs()

    def handle_checked_checkbox(self, state, row_data, page):
        try:
            columns_of_interest = ['Номер заявки', 'Статус заказа', 'ФИО водителя', 'Дата маршрута', 'Номер маршрута',
                                   'Номер заказа клиента']
            num_delivery = row_data[self.df.columns.get_loc('Номер маршрута')]

            # Создаем список значений для каждого столбца
            values_of_interest = [row_data[self.df.columns.get_loc(col)] for col in columns_of_interest]

            # Находим индекс строки, соответствующей значениям интересующих столбцов
            mask = None
            for column_name, value in zip(columns_of_interest, values_of_interest):
                condition = (self.df[column_name] == value)
                if mask is None:
                    mask = condition
                else:
                    mask &= condition

            # Применяем маску для фильтрации DataFrame
            filtered_rows = self.df[mask]

            if len(filtered_rows) > 0:
                row_index = filtered_rows.index[0]  # Получаем индекс первой найденной строки
                if state == 2:
                    self.df.at[row_index, "Проверено"] = "Да"
                else:
                    self.df.at[row_index, "Проверено"] = "Нет"
            else:
                logger.warning("Строка не найдена")

            filtered_df = self.df[self.df["Номер маршрута"] == num_delivery]
            # Проверяем условие: все значения в столбце "Проверено" равны "Да"
            all_checked = (filtered_df['Проверено'] == 'Да').all()

            if all_checked:
                index = self.tabWidget.indexOf(page)

        except Exception as ex:
            logger.error(f"Error handling checkbox change: {ex}")


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w = MainWindow()
    w.show()

    sys.exit(app.exec())

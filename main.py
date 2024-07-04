from pathlib import Path
import os
import qdarkstyle
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QCheckBox, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QProgressBar, \
    QHeaderView
from loguru import logger
from GUI.main_ui import Ui_MainWindow
from read_files import read_excel
import pandas as pd

from styles import tab_style, table_style


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.version = 0.1
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

        # Apply styles to QTabWidget tabs
        self.setStyleSheet(tab_style)

    def reset(self):
        self.filtered_df = self.df.copy()
        self.clear_tabs()
        self.create_driver_tabs()

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
                    elif col_index == 6:  # Седьмой столбец (индекс 6)
                        checkbox = QCheckBox()
                        if value == "да":  # Предположим, что проверяемое значение хранится в строковом формате
                            checkbox.setChecked(True)
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


if __name__ == '__main__':
    import sys

    logger.add(
        f"logs.log",
        rotation="20 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file!s} | {line} | {message}"
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w = MainWindow()
    w.show()

    sys.exit(app.exec())

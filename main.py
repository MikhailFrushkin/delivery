from pathlib import Path
import os
import qdarkstyle
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtWidgets import QProgressBar
from loguru import logger
from GUI.main_ui import Ui_MainWindow
from read_files import read_excel


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.version = 0.1
        self.open_folder = ''
        self.name_doc = ''
        self.current_dir = Path.cwd()
        self.df = None

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 10, 100, 25)
        self.progress_bar.setMaximum(100)
        self.statusbar.addWidget(self.progress_bar, 1)

        self.status_message = QtWidgets.QLabel()
        self.statusbar.addPermanentWidget(self.status_message)

        self.pushButton.clicked.connect(self.evt_btn_open_file_clicked)

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

                # Очищаем verticalLayout_2 перед добавлением новых чекбоксов и вкладок
                self.clear_layout(self.verticalLayout_2)
                self.clear_toolbox()

                # Создаем чекбоксы с датами и таблицы с ФИО водителей
                self.create_date_checkboxes()
                self.create_driver_tabs()

            except Exception as ex:
                logger.error(f'ошибка чтения xlsx {ex}')
                QMessageBox.information(self, 'Инфо', f'ошибка чтения xlsx {ex}')

    def clear_layout(self, layout):
        """Очистка всех элементов в указанном layout"""
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def clear_toolbox(self):
        """Очистка всех вкладок в toolBox"""
        for i in reversed(range(self.toolBox.count())):
            self.toolBox.removeItem(i)

    def create_date_checkboxes(self):
        """Создание чекбоксов для уникальных дат и добавление их в verticalLayout_2"""
        unique_dates = self.df["Дата маршрута"].unique()
        formatted_dates = [date.strftime('%Y-%m-%d') for date in unique_dates]

        for date_str in formatted_dates:
            checkbox = QCheckBox(date_str, parent=self)
            self.verticalLayout_2.addWidget(checkbox)
            checkbox.stateChanged.connect(self.handle_checkbox_change)

    def create_driver_tabs(self):
        """Создание вкладок для каждого уникального водителя в toolBox"""
        unique_drivers = self.df["ФИО водителя"].unique()

        for driver in unique_drivers:
            # Создаем новую страницу для водителя
            page = QtWidgets.QWidget()
            page.setObjectName(driver)  # Имя вкладки как ФИО водителя
            self.toolBox.addItem(page, driver)

            # Создаем таблицу для отображения данных
            table_widget = QTableWidget(parent=page)
            num_columns = len(self.df.columns)
            table_widget.setColumnCount(num_columns)

            # Устанавливаем названия столбцов
            table_widget.setHorizontalHeaderLabels(self.df.columns)

            # Определяем количество строк для данного водителя
            driver_data = self.df[self.df["ФИО водителя"] == driver]
            num_rows = driver_data.shape[0]
            table_widget.setRowCount(num_rows)

            # Заполняем таблицу данными из self.df
            for row_index, row_data in enumerate(driver_data.values):
                for col_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    if self.df.columns[col_index] == "Дата маршрута":
                        item = QTableWidgetItem(str(value.strftime('%Y-%m-%d')))
                    table_widget.setItem(row_index, col_index, item)

            # Растягиваем столбцы по содержимому
            table_widget.resizeColumnsToContents()

            # Распределяем виджеты внутри страницы
            layout = QtWidgets.QVBoxLayout(page)
            layout.addWidget(table_widget)

        # Применяем стили к QToolBox (установка шрифта, цвета и стиля текста для заголовков вкладок)
        self.setStyleSheet("""
            QToolBox::tab {
                font-size: 16px;
                color: yellow;
                font-weight: bold;
            }
        """)

    def handle_checkbox_change(self, state):
        sender = self.sender()
        if state == QtCore.Qt.CheckState.Checked:
            print(f'Checkbox {sender.text()} checked')
        else:
            print(f'Checkbox {sender.text()} unchecked')


if __name__ == '__main__':
    import sys
    import os

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

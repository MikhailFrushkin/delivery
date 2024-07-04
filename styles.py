tab_style = """
            QTabWidget::pane {
                border-top: 2px solid #C2C7CB;
                position: absolute;
                top: -0.5em;
            }

            QTabWidget::tab-bar {
                alignment: center;
            }

            QTabBar::tab {
                border: 3px solid #C4C4C3;
                border-bottom-color: #C2C7CB; 
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 4px;
                font-size: 16px;
                color: yellow;
                font-weight: bold;
                background: None;
                
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background: None;
                color: red;
                font-size: 16px;
            }

            QTabBar::tab:selected {
                border-color: #9B9B9B;
                border-bottom-color: #C2C7CB; 
            }

            QTabBar::tab:!selected {
                margin-top: 2px; 
            }

            QTabBar::tab:selected {
                margin-left: -4px;
                margin-right: -4px;
            }

            QTabBar::tab:first:selected {
                margin-left: 0; 
            }

            QTabBar::tab:last:selected {
                margin-right: 0;
            }

            QTabBar::tab:only-one {
                margin: 5px;
            }
            
            QTabBar::scroller {
                width: 40px;  /* Width of the scroll buttons */
            }
        """

table_style = """
    QHeaderView::section {
        font-size: 12pt; 
    }
    QTableWidget {
        font-size: 12pt; /* Размер шрифта данных в ячейках */
    }
    """

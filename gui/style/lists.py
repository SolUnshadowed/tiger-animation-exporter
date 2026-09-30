list_style = """
QListWidget {
	background-color: #ffffff;
	border: 1px solid #000000;
	outline: 0;
	padding: 5px;
}
QListWidget::item {
	background-color: #ffffff;
	color: #212529;
	border: 1px solid #000000;
	padding: 8px 12px;
}
QListWidget::item:hover {
	background-color: #e8f0fe;
	color: #1a73e8;
}
QListWidget::item:selected {
	background-color: #2563eb;
	color: white;
}
"""


'''
QListWidget::item:selected:!active {
	background-color: #93c5fd;
	color: #1e293b;
}
'''

search_style = """
QLineEdit {
	background-color: #ffffff;
	border: 1px solid #000000;
}
"""
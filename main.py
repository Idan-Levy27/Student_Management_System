from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, \
    QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import mysql.connector
import re


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="123456",
                 database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host,
                                             user=self.user,
                                             password=self.password,
                                             database=self.database)
        return connection




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_iem = self.menuBar().addMenu("&File")
        help_menu_iem = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_iem.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_iem.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_student_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_student_action)
        search_student_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements: search, add
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student_action)

        # Create status bar and add status bar elements: delete, edit
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)


    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """This app is a student management system that the user can add, edit and 
        delete students from the app """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Update Student Data ")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = stu_man_sys.table.currentRow()
        student_name = stu_man_sys.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = stu_man_sys.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course = stu_man_sys.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = stu_man_sys.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        stu_man_sys.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Delete Student Data ")

        self.layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        self.layout.addWidget(confirmation, 0, 0, 1, 2)
        self.layout.addWidget(yes, 1, 0)
        self.layout.addWidget(no, 1, 1)
        self.setLayout(self.layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.no_delete)

    def delete_student(self):

        # Get selected row index and student id
        index = stu_man_sys.table.currentRow()
        student_id = stu_man_sys.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        stu_man_sys.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()

    def no_delete(self):
        self.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.validate_data)
        layout.addWidget(button)

        self.setLayout(layout)


    def validate_data(self):
        if self.student_name.text() == "":
            confirmation_widget = QMessageBox()
            confirmation_widget.setWindowTitle("Error")
            confirmation_widget.setText("You should enter student name!")
            confirmation_widget.exec()
        elif self.mobile.text() == "":
            confirmation_widget = QMessageBox()
            confirmation_widget.setWindowTitle("Error")
            confirmation_widget.setText("You should enter mobile number!")
            confirmation_widget.exec()
        else:
            self.add_student()

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        stu_man_sys.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add a search button
        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def search_student(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name=%s", (name,))
        result = cursor.fetchall()
        rows = list(result)
        items = stu_man_sys.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            stu_man_sys.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
stu_man_sys = MainWindow()
stu_man_sys.show()
stu_man_sys.load_data()
sys.exit(app.exec())





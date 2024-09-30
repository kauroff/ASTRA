import sys
import os
import PyQt5.QtWidgets
import PyQt5.QtCore


class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 1:
            button = QStyleOptionButton()
            button.rect = option.rect
            button.text = "Update"
            QApplication.style().drawControl(QStyle.CE_PushButton, button, painter)
        else:
            super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            button = QPushButton(parent)
            button.setText("Update")
            button.clicked.connect(lambda: self.calculate_folder_size(index))
            return button
        return super().createEditor(parent, option, index)

    def calculate_folder_size(self, index):
        file_model = index.model()
        folder_path = file_model.filePath(index)
        size = self.get_folder_size(folder_path)
        file_model.setData(index, f"{size / (1024 * 1024):.2f} MB", Qt.EditRole)

    def get_folder_size(self, folder):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size


class CustomFileSystemModel(QFileSystemModel):
    def columnCount(self, parent=QModelIndex()):
        return super().columnCount(parent) + 1

    def data(self, index, role=Qt.DisplayRole):
        if index.column() == 1 and role == Qt.DisplayRole:
            return "0 MB"
        return super().data(index, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if section == 1 and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Size"
        return super().headerData(section, orientation, role)


class FileFilterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.model = CustomFileSystemModel()
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden)
        home_dir = QDir.homePath()
        self.model.setRootPath(home_dir)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(home_dir))

        self.tree.setItemDelegateForColumn(1, ButtonDelegate(self.tree))
        self.tree.setColumnWidth(1, 150)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Text for filter: ")
        self.filter_edit.textChanged.connect(self.filter_files)

        layout = QVBoxLayout()
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.tree)

        self.setLayout(layout)
        self.setWindowTitle("Filtered:")
        self.resize(800, 600)

    def filter_files(self, text):
        filter_text = (f"*{text}*")
        self.model.setNameFilters([filter_text])
        self.model.setNameFilterDisables(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileFilterApp()
    window.show()
    sys.exit(app.exec_())

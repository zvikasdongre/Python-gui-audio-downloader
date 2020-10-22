from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
from youtubesearchpython import SearchVideos
import sys
import youtube_dl
import json
import os

class StartQT5(QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_window()
        self.ui.setupUi(self)
        self.setWindowTitle("Audio-Downloader")

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

class Ui_window(object):
    
    # GLOBAL VARIABLES
    
    search_result = []  # Searched audio details
    search_urls = []    # Searched audio urls
    final_links = []    # The final links to download
    quality_options = ['Mp3 (320kbps)', 'Mp3 (256kbps)', 'Mp3 (192kbps)', 'Mp3 (156kbps)']
    preferred_quality = 0
    download_path = ""
    
    def find_quality(self):
        if self.final_links != []:
            current_text = self.quality.currentText()
            if current_text == "Mp3 (320kbps)":
                self.preferred_quality = 320
                self.status.setText("Downloading")
                self.status.show()

            elif current_text == "Mp3 (256kbps)":
                self.preferred_quality = 265
                self.status.setText("Downloading")
                self.status.show()

            elif current_text == "Mp3 (192kbps)":
                self.preferred_quality = 192
                self.status.setText("Downloading")
                self.status.show()

            elif current_text == "Mp3 (156kbps)":
                self.preferred_quality = 156
                self.status.setText("Downloading")
                self.status.show()
                
            else:
                print("nothing")
        else:
            pass
    
    def search(self):
        try:
            self.search_result = []
            self.results.clear()
            self.search_urls = []
            query = self.usr_search.text()
            if query == "":
                print("nothing")
            else:
                self.status.show()
                data = SearchVideos(query, offset=1, mode="dict", max_results=13)
                final_data = data.result()
                for item in final_data['search_result']:
                    titles = item['title']
                    urls = item['link']
                    self.search_result.append(titles)
                    self.search_urls.append(urls)
                if self.search_result == []:
                    print("NOT FOUND")
                else:
                    self.results.addItems(self.search_result)
                for i in range(len(self.search_result)):
                    self.results.item(i).setCheckState(QtCore.Qt.Unchecked)
                self.status.setText("Idle")
        except:
            self.error.show()
            self.error.setText("Please check your connection and Try again...")
            QTimer.singleShot(3000, self.error.hide)
        else:
            self.error.hide()
            self.error.setText("Please select at least one audio to start")
    
    def get_links(self):
        self.final_links = ['https://www.youtube.com/watch?v=RQ0FzwaqLow']
        for index in range(self.results.count()):
            if self.results.item(index).checkState() == QtCore.Qt.Checked:
                self.final_links.append(self.search_urls[index])
        if self.final_links == []:
            self.error.show()
            QTimer.singleShot(3000, self.error.hide)
        else:
            self.error.hide()
        print(self.final_links)
    
    def download(self):
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': self.download_path + '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(self.preferred_quality),
            }],
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(self.final_links)

    def start_functions(self):
        self.get_links()
        self.find_quality()
        self.download()
    
    def my_hook(self, d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')
            self.status.setText("Finished")
            self.status.show()
        if d['status'] == 'downloading':
            self.status.setText("Downloading...")
            self.status.show()
            download_percent = d['_percent_str']
            download_num = download_percent.replace('%','')
            self.download_progress.setValue(float(download_num))
    
    def choose_dir(self):
        dialog = QtWidgets.QFileDialog()
        select_path = dialog.getExistingDirectory(None, "Select Folder") + "/"
        with open('config.json', 'r+') as f:
            data = json.load(f)
            data['download_path'] = select_path
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            self.download_path = data['download_path']
            self.path_text.setText(self.download_path)
    
    def load_path(self):
        with open('config.json', 'r+') as f:
            data = json.load(f)
            self.download_path = data['download_path']
            self.path_text.setText(self.download_path)
    
    def reset_download_path(self):
        default_path = os.path.expanduser("~") + "/Downloads/Audio-downloader/"
        with open('config.json', 'r+') as f:
            data = json.load(f)
            data['download_path'] = default_path
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            self.download_path = data['download_path']
            self.path_text.setText(self.download_path)
            
    def start_up_functions(self):
        self.load_path()
    
    def setupUi(self, window):
        window.setObjectName("window")
        window.resize(500, 420)
        window.setMinimumSize(QtCore.QSize(500, 420))
        window.setMaximumSize(QtCore.QSize(500, 420))
        window.setStyleSheet("font-weight: bold;")
        self.centralwidget = QtWidgets.QWidget(window)
        self.centralwidget.setObjectName("centralwidget")
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setGeometry(QtCore.QRect(0, 0, 501, 421))
        self.tabs.setObjectName("tabs")
        self.downloader = QtWidgets.QWidget()
        self.downloader.setObjectName("downloader")
        self.download_progress = QtWidgets.QProgressBar(self.downloader)
        self.download_progress.setGeometry(QtCore.QRect(19, 345, 461, 31))
        self.download_progress.setStyleSheet("")
        self.download_progress.setProperty("value", 24)
        self.download_progress.setObjectName("download_progress")
        self.download_progress.setValue(0)
        self.results = QtWidgets.QListWidget(self.downloader)
        self.results.setGeometry(QtCore.QRect(19, 60, 461, 201))
        self.results.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.results.setViewMode(QtWidgets.QListView.ListMode)
        self.results.setObjectName("results")
        self.download_btn = QtWidgets.QPushButton(self.downloader)
        self.download_btn.setGeometry(QtCore.QRect(379, 295, 101, 31))
        self.download_btn.setObjectName("download_btn")
        self.quality = QtWidgets.QComboBox(self.downloader)
        self.quality.setGeometry(QtCore.QRect(138, 295, 121, 31))
        self.quality.setObjectName("quality")
        self.quality_label = QtWidgets.QLabel(self.downloader)
        self.quality_label.setGeometry(QtCore.QRect(19, 295, 111, 31))
        self.quality_label.setObjectName("quality_label")
        self.quality.addItems(self.quality_options)
        self.error = QtWidgets.QLabel(self.downloader)
        self.error.setGeometry(QtCore.QRect(19, 260, 461, 31))
        self.error.setStyleSheet("color: rgb(255, 0, 0);\n"
"font-weight: bold;")
        self.error.setAlignment(QtCore.Qt.AlignCenter)
        self.error.setObjectName("error")
        self.error.hide()
        self.status = QtWidgets.QLabel(self.downloader)
        self.status.setGeometry(QtCore.QRect(269, 300, 111, 21))
        self.status.setObjectName("status")
        self.status.hide()
        self.usr_search = QtWidgets.QLineEdit(self.downloader)
        self.usr_search.setGeometry(QtCore.QRect(19, 15, 461, 31))
        self.usr_search.setStyleSheet("padding: 5px 10px;")
        self.usr_search.setObjectName("usr_search")
        self.tabs.addTab(self.downloader, "")
        self.settings = QtWidgets.QWidget()
        self.settings.setObjectName("settings")
        self.setting_label = QtWidgets.QLabel(self.settings)
        self.setting_label.setGeometry(QtCore.QRect(20, 10, 461, 31))
        self.setting_label.setAlignment(QtCore.Qt.AlignCenter)
        self.setting_label.setObjectName("setting_label")
        self.path_label = QtWidgets.QLabel(self.settings)
        self.path_label.setGeometry(QtCore.QRect(20, 50, 121, 21))
        self.path_label.setObjectName("path_label")
        self.path_text = QtWidgets.QLineEdit(self.settings)
        self.path_text.setGeometry(QtCore.QRect(19, 80, 461, 31))
        self.path_text.setObjectName("path_text")
        self.path_text.setReadOnly(True)
        self.reset_path = QtWidgets.QPushButton(self.settings)
        self.reset_path.setGeometry(QtCore.QRect(250, 120, 91, 31))
        self.reset_path.setObjectName("reset_path")
        self.change_path = QtWidgets.QPushButton(self.settings)
        self.change_path.setGeometry(QtCore.QRect(150, 120, 81, 31))
        self.change_path.setObjectName("change_path")
        self.coming_soon = QtWidgets.QLabel(self.settings)
        self.coming_soon.setGeometry(QtCore.QRect(150, 220, 191, 16))
        self.coming_soon.setObjectName("coming_soon")
        self.coming_soon.setAlignment(QtCore.Qt.AlignCenter)
        self.tabs.addTab(self.settings, "")
        self.help = QtWidgets.QWidget()
        self.help.setObjectName("help")
        self.tabs.addTab(self.help, "")
        self.textBrowser = QtWidgets.QTextBrowser(self.help)
        self.textBrowser.setGeometry(QtCore.QRect(-4, -1, 511, 401))
        self.textBrowser.setObjectName("textBrowser")
        window.setCentralWidget(self.centralwidget)

        self.retranslateUi(window)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(window)
        self.usr_search.returnPressed.connect(self.search)
        self.download_btn.clicked.connect(self.start_functions)
        self.change_path.clicked.connect(self.choose_dir)
        self.reset_path.clicked.connect(self.reset_download_path)
        self.start_up_functions()

        
    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "MainWindow"))
        self.usr_search.setPlaceholderText(_translate("window", "Type and Press Enter..."))
        self.results.setSortingEnabled(False)
        __sortingEnabled = self.results.isSortingEnabled()
        self.results.setSortingEnabled(False)
        self.results.setSortingEnabled(__sortingEnabled)
        self.download_btn.setText(_translate("window", "Download"))
        self.quality_label.setText(_translate("window", "Bitrate (Quality) :"))
        self.error.setText(_translate("window", "<html><head/><body><p>Please select at least one audio to start</p></body></html>"))
        self.status.setText(_translate("window", "Searching..."))
        self.usr_search.setPlaceholderText(_translate("window", "Write and Press Enter..."))
        self.tabs.setTabText(self.tabs.indexOf(self.downloader), _translate("window", "Downloader"))
        self.setting_label.setText(_translate("window", "<html><head/><body><p><span style=\" font-size:14pt;\">Settings</span></p></body></html>"))
        self.path_label.setText(_translate("window", "<html><head/><body><p><span style=\" font-size:medium;\">Download Path:</span></p></body></html>"))
        self.change_path.setText(_translate("window", "Change"))
        self.reset_path.setText(_translate("window", "Reset"))
        self.coming_soon.setText(_translate("window", "More settings coming soon..."))
        self.tabs.setTabText(self.tabs.indexOf(self.settings), _translate("window", "Settings"))
        self.tabs.setTabText(self.tabs.indexOf(self.help), _translate("window", "Help"))
        self.textBrowser.setHtml(_translate("window", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600; font-style:normal; padding:10px;\">\n"
"<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">How to use Audio-downloader:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:400;\">Type in the search bar and hit enter to </span><span style=\" font-size:11pt; color:#ff5500;\">search</span><span style=\" font-size:11pt; font-weight:400;\">, after searching a list will appear on the screen, </span><span style=\" font-size:11pt; color:#ff5500;\">check</span><span style=\" font-size:11pt; font-weight:400;\"> the songs/audios you want to </span><span style=\" font-size:11pt; font-weight:400; color:#000000;\">download</span><span style=\" font-size:11pt; font-weight:400;\">, then select the </span><span style=\" font-size:11pt; color:#ff5500;\">quality</span><span style=\" font-size:11pt; font-weight:400;\"> from the drop down.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:400;\">Lastly press the </span><span style=\" font-size:11pt; color:#ff5500;\">download</span><span style=\" font-size:11pt; font-weight:400;\"> button to </span><span style=\" font-size:11pt; font-weight:400; color:#000000;\">start</span><span style=\" font-size:11pt; font-weight:400;\"> downloading.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:400;\">The progress bar will show the</span><span style=\" font-size:11pt; color:#ff5500;\"> progress</span><span style=\" font-size:11pt; font-weight:400;\">.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:400;\">For more info visit: </span><span style=\" font-size:11pt; color:#ff5500;\">https://github.com/zvikasdongre/Python-gui-audio-downloader</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:400;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">This Audio-Downloader was made by:  </span><span style=\" font-size:12pt; color:#ff5500;\">xvikasdongre</span></p></body></html>"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = StartQT5()
    myapp.show()
    sys.exit(app.exec_())

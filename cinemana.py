#!/usr/bin/python


# Import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from PyQt5.uic import loadUiType


# FOR YOUTUBE TRAILERS
from PyQt5.QtWebEngineWidgets import QWebEngineView


from os import path
import subprocess

import requests

from urllib.request import urlopen

import json

from functools import lru_cache
from urllib.parse import urlencode

MAIN_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'ui/main_gui.ui'))



# View Properties
ICON_SIZE = 250

class CinemanaAPI:
    SEARCH_API = 'https://cinemana.shabakaty.com/api/android/AdvancedSearch?'
    VIDEOS_API = 'https://cinemana.shabakaty.com/api/android/transcoddedFiles/id/'
    EPISODES_API = 'https://cinemana.shabakaty.com/api/android/videoSeason/id/'
    ALL_INFO = 'https://cinemana.shabakaty.com/api/android/allVideoInfo/id/'


def getYouTubeHtml(url):
    url = url.replace("watch?v=", "embed/")
    return "<style type=\"text/css\">*{margin: 0px;padding: 0px;};</style>" + '''
        <iframe width="100%" height="100%" src="{}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    '''.format(url)


####################### Right Click Menu #############################

# DATA = (path.join(path.dirname(__file__), 'data/data.json'

# class QRightClickMenu(QMenu):
#     def show(self, position):
#         add_to_favourite = QAction("Add to favourite", self, checkable=True)
#         add_to_watch_later = QAction("Add to Watch Later", self, checkable=True)
#         self.addAction(add_to_favourite)
#         self.addSeparator()
#         self.addAction(add_to_watch_later)
#         self.exec(position)

####################### Right Click Menu #############################


class MainApp(QMainWindow, MAIN_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)


        self.setupUi(self)
        self.setWindowTitle('Cinemana GUI')

        self.handleButtons()
        self.handleTabs(hide='1 2')
        self.handleSearchCombo()
        self.handleSeriesCombo()
        self.handleStatusbar()

        self.e = ''

        self.listWidget.setIconSize(ICON_SIZE * QSize(2, 2))

        self.listWidget.itemClicked.connect(self.viewItem)
        # self.listWidget.itemDoubleClicked.connect(self.viewItem)

        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_4.setEnabled(False)

    #####################################
    #        RIGHT CLICK MENU           #
    #####################################
    #<<<<<<<<<<<<<<<<<<<< ADD THIS FEATURE LATER  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #     # self.listWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #     self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
    #     self.listWidget.customContextMenuRequested.connect(self.myListWidgetContext)

    # def myListWidgetContext(self,position):

    #     #Popup menu
    #     # print("RIGHT CLICKED")
        
    #     if self.listWidget.itemAt(position):
    #         # Get Current Item Position
    #         point = QPoint()
    #         point = self.listWidget.mapToGlobal(position)

    #         # Show The Menu 
    #         right_click_menu = QRightClickMenu()
    #         right_click_menu.show(point)


    # def addToPlayList(self, playlist='favourite'):
    #     pass

    #####################################
    #        RIGHT CLICK MENU           #
    #          CODE END HERE            #
    #####################################        

    def handleStatusbar(self):
    	self.status = QLabel('Status', self)
    	# self.
    	self.statusBar.addWidget(self.status)


    def handleButtons(self):
        self.pushButton.clicked.connect(self.search)
        self.pushButton_2.clicked.connect(self.moreItems)
        self.pushButton_3.clicked.connect(self.playVideo)
        self.pushButton_4.clicked.connect(self.playVideo)

    def handleTabs(self, hide='', show=''):
        if hide != '':
            for i in hide.split():
                self.tabWidget.setTabVisible(int(i), False)

        if show != '':
            for i in show.split():
                self.tabWidget.setTabVisible(int(i), True)
    
    
    def handleSearchCombo(self):
        self.comboBox_4.currentTextChanged.connect(self.search)
        self.comboBox_3.currentTextChanged.connect(self.search)


    def handleSeriesCombo(self):
        self.comboBox_8.currentTextChanged.connect(self.setEpisodes)
        self.comboBox_9.currentTextChanged.connect(self.getEpisodeVideos)

    def playVideo(self):
        self.setCursor(Qt.WaitCursor)

        playLineArgs = ['mpv']
        if self.comboBox_2.currentText() != 'Quality':
            for i in self.videos:
                if self.comboBox_2.currentText() == i['resolution']:
                    video = i['videoUrl'].replace("\\", '')
                    playLineArgs.append(video)
                    break

        elif self.comboBox_6.currentText() != 'Quality':
            for i in self.videos:
                if self.comboBox_6.currentText() == i['resolution']:
                    video = i['videoUrl'].replace("\\", '')
                    playLineArgs.append(video)
                    break


        if self.comboBox_5.currentText() != 'Subtitle':                    
            for i in self.subtiles:
                if self.comboBox_5.currentText() == i['name']:
                    subtitle = i['file'].replace("\\", '')
                    playLineArgs.append(f'--sub-file={subtitle}')
                    # playLineArgs.append(subtile)
                    break

                
        if self.comboBox_7.currentText() != 'Subtitle':
            for i in self.subtiles:
                if self.comboBox_7.currentText() == i['name']:
                    subtitle = i['file'].replace("\\", '')
                    playLineArgs.append(f'--sub-file={subtitle}')
                    # playLineArgs.append(subtile)
                    break

        if len(playLineArgs) > 1:
            options = ["--use-filedir-conf"]
            
            for i in options:
                playLineArgs.append(i)

            print(playLineArgs)

            # Playing Video With Externel player        
            player = subprocess.Popen(playLineArgs)
            output, error = player.communicate()
            
            player.wait()
            print(output)
            print(error)
            
        self.unsetCursor()
                
                    

    def viewItem(self, item):
        self.setCursor(Qt.WaitCursor)
        
        if self.comboBox_3.currentText() == 'Movie':
            self.viewMovie(item.data(Qt.UserRole))

        else:
            self.viewSeries(item.data(Qt.UserRole))

        self.unsetCursor()

        # print(item.data(Qt.UserRole))

    def search(self):
        if self.lineEdit.text():
            self.pushButton_2.setEnabled(True)

            params = {}
            params['videoTitle'] = self.lineEdit.text()
            params['type'] = self.comboBox_3.currentText().lower()

            # if self.spinBox.value() != 'Year':
            #     params['year'] = int(self.spinBox.value())

            if self.comboBox_4.currentText() != 'Stars':
                params['star'] = int(self.comboBox_4.currentText())

            param = urlencode(params)
            
            self.param = param
            self.page = 1

            self.setCursor(Qt.WaitCursor)
            resp = self.getResult(param)
            self.unsetCursor()
            
            if resp:
                self.showResults(resp)

    def setEpisodes(self):
        # print('CHANGED SEASON')
        if currentSeason := self.comboBox_8.currentText():
            if currentSeason != 'Seasons':
                e = self.episodes[str(currentSeason)]
                # print(e)
                self.comboBox_9.clear()
                self.comboBox_9.addItem('Episodes')
                for i in e:
                    self.comboBox_9.addItem(str(i[0]))

                # Current Season Episodes
                self.e = e


    def getEpisodeVideos(self):
        self.setCursor(Qt.WaitCursor)

        ep = self.comboBox_9.currentText()
        resp = ''
        for i in self.e:
            if i[0] == ep:
                ID = i[1]
                if resp := self.getVideos(str(ID)):
                    break
        if resp != '':
            videos_json_data = json.loads(resp)
            self.videos = videos_json_data
        

            # Set video qualities
            self.comboBox_6.clear()
            self.comboBox_6.addItem('Quality')
            for i in videos_json_data:
               self.comboBox_6.addItem(i['resolution'])
                
            
            if resp := self.getInfo(str(ID)):
                episode_json_info = json.loads(resp)

                # Add subtitles
                try:
                    subtiles = episode_json_info['translations']
                    self.subtiles = subtiles
                    self.comboBox_7.clear()
                    self.comboBox_7.addItem('Subtitle')

                    added = []
                    # ADD SUBTITLES
                    for i in subtiles:
                        if i['name'] not in added:
                            self.comboBox_7.addItem(i['name'])
                            added.append(i['name'])

                except:
                    print('No Subtitle Available')

        self.unsetCursor()
                

    def viewSeries(self, id):    
        if resp := self.getInfo(id):
            series_json_info = json.loads(resp)

            self.handleTabs(show='2', hide='1')
            self.tabWidget.setCurrentIndex(2)
            self.pushButton_4.setEnabled(True)
            
            # Set Poster
            if data := self.get_poster_data((series_json_info['imgObjUrl'])):
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                self.label_10.setPixmap(pixmap.scaled(300 , 400, Qt.KeepAspectRatio))


            # Name
            self.label_15.setText(series_json_info['en_title'])
            self.name = series_json_info['en_title']

            #Year
            self.label_16.setText(series_json_info['year'])

            # Stars
            self.label_17.setText(series_json_info['stars'])

            # info url (imdbUrlRef)
            if info_link := series_json_info['imdbUrlRef']:
                urlLink =f"<a href=\"{info_link}\">{info_link}</a>"

                self.label_22.setText(urlLink)
                self.label_22.setOpenExternalLinks(True)

            else:
                print("NO INFO FOUND")
                self.label_21.hide()
                self.label_22.hide()

            # Story:
            self.label_18.setText(series_json_info['en_content'])
            self.label_18.setWordWrap(True)


            # Trailer (trailer)
            if video_link := series_json_info['trailer']:
                if html := getYouTubeHtml(video_link):
                    print(html)
                    self.webEngineView.setHtml(html)
                    self.webEngineView.setFixedSize(QSize(450, 250))
                    # self.webEngineView.setBackground(QColor(0, 0, 0))

            else:
                print("NO TRAILER FOUND")
                self.webEngineView.hide()
                self.label_19.hide()
            
            if resp := self.getEpisodes(id):
                series_episodes = json.loads(resp)

                episodes = {}
                seasons = []

                self.comboBox_6.clear() # Quality
                self.comboBox_7.clear() # Subtitle

                self.comboBox_8.clear() # Seasons 
                self.comboBox_9.clear() # Episodes

                self.comboBox_8.addItem('Seasons')

                for i in series_episodes:
                    if i['season'] not in seasons:
                        episodes[f"{i['season']}"] = []
                        seasons.append(i['season'])

                
                for i in series_episodes:                   
                    episodes[f"{i['season']}"].append([str(i['episodeNummer']), i['nb']])
                
                # Add to seasons
                seasons = sorted(seasons)
                for s in seasons:
                    self.comboBox_8.addItem(str(s))
                    
                self.episodes = episodes

    def viewMovie(self, id):
        if resp := self.getVideos(id):
            videos_json_data = json.loads(resp)
            self.videos = videos_json_data

            self.handleTabs(show='1', hide='2')
            self.tabWidget.setCurrentIndex(1)
            self.pushButton_3.setEnabled(True)

            # Set video qualities
            self.comboBox_2.clear()
            self.comboBox_2.addItem('Quality')
            for i in videos_json_data:
               self.comboBox_2.addItem(i['resolution'])
                
            
            if resp := self.getInfo(id):
                movie_json_info = json.loads(resp)
                
                # Set Poster
                if data := self.get_poster_data((movie_json_info['imgObjUrl'])):
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    self.label.setPixmap(pixmap.scaled(300 , 400, Qt.KeepAspectRatio))
    

                # Name
                self.label_6.setText(movie_json_info['en_title'])

                #Year
                self.label_7.setText(movie_json_info['year'])

                # Stars
                self.label_8.setText(movie_json_info['stars'])

                # info url (imdbUrlRef)
                if info_link := movie_json_info['imdbUrlRef']:
                    urlLink =f"<a href=\"{info_link}\">{info_link}</a>"

                    self.label_24.setText(urlLink)
                    self.label_24.setOpenExternalLinks(True)

                else:
                    print("NO INFO FOUND")
                    self.label_23.hide()
                    self.label_24.hide()


                # Story:
                self.label_9.setText(movie_json_info['en_content'])
                self.label_9.setWordWrap(True)

                # Trailer (trailer)
                if video_link := movie_json_info['trailer']:
                    if html := getYouTubeHtml(video_link):
                        print(html)
                        self.webEngineView_2.setHtml(html)
                        self.webEngineView_2.setFixedSize(QSize(500, 300))

                else:
                    print("NO TRAILER FOUND")
                    self.webEngineView_2.hide()
                    self.label_20.hide()

                # Add subtitles
                try:
                    subtiles = movie_json_info['translations']
                    self.subtiles = subtiles
                    self.comboBox_5.clear()
                    self.comboBox_5.addItem('Subtitle')

                    added = []
                    # ADD SUBTITLES
                    for i in subtiles:
                        if i['name'] not in added:
                            self.comboBox_5.addItem(i['name'])
                            added.append(i['name'])
                except:
                    print('No Subtitle Available')
    def success(self):
        self.status.setText('Data fetched successfully')
        # self.status.styleSheet('QLabel{ background-color: green; color: white; };')
        self.status.setStyleSheet('background-color: green; color: white;')

    def fail(self, msg=''):
        print(msg)
        self.status.setText('Data fetching failed: please check your network connection')
        # self.status.styleSheet('QLabel{ background-color: red; color: white; };')
        self.status.setStyleSheet('background-color: red; color: white;')


    @lru_cache(10)
    def getInfo(self, id):
        try:
            resp = requests.get(CinemanaAPI.ALL_INFO + id)
        except Exception as e:
            self.fail(e)
        else:
            self.success()
            return resp.text

    @lru_cache(10)
    def get_poster_data(self, url):
        try:
            data = urlopen(url).read()
        except Exception as e:
            self.fail(e)
            return False
        else:
            self.success()
            return data

    @lru_cache(10)
    def getEpisodes(self, id):
        try:
            resp = requests.get(CinemanaAPI.EPISODES_API + id)
        except Exception as e:
            self.fail(e)
        else:
            self.success()
            return resp.text

    @lru_cache(10)
    def getVideos(self, id):
        try:
            resp = requests.get(CinemanaAPI.VIDEOS_API + id)
        except Exception as e:
            self.fail(e)
        else:
            self.success()
            return resp.text
        

    def moreItems(self):
        self.page += 1
        param = self.param + f'&page={self.page}'

        if resp := self.getResult(param):
            json_data = json.loads(resp)
        

        if len(json_data) > 1:
            for i in json_data:
                self.setCursor(Qt.WaitCursor)

                name = i['en_title']

                name += f"\n({i['year']})" 

                # Name
                it = QListWidgetItem(name)

                # Set id number
                it.setData(Qt.UserRole, i['nb'])

                # Set on hover
                it.setToolTip(i['stars'])

                # # Set background
                # it.setBackground(QColor('sea green'))

                # Poster
                data = self.get_thumb_image(i['imgThumbObjUrl'])
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                
                it.setIcon(QIcon(pixmap))

                # Set Item not selectable
                it.setFlags(it.flags() | ~Qt.ItemIsSelectable)
                
                self.listWidget.addItem(it)

            self.unsetCursor()
        
        else:
            self.pushButton_2.setEnabled(False)        
                
    def showResults(self, search_result_data):
        json_data = json.loads(search_result_data)

        # Clear the items
        self.listWidget.clear()

        for i in json_data:
            self.setCursor(Qt.WaitCursor)

            name = i['en_title']

            name += f" ({i['year']})" 

            # Name
            it = QListWidgetItem(name)

            # Set id number
            it.setData(Qt.UserRole, i['nb'])

            # # Set background
            # it.setBackground(QColor('sea green'))

            # Set on hover
            it.setToolTip(i['stars'])

            # Poster
            if data := self.get_thumb_image(i['imgThumbObjUrl']):
                pixmap = QPixmap()
                pixmap.loadFromData(data)    
                it.setIcon(QIcon(pixmap))
            
            self.listWidget.addItem(it)
        
        self.unsetCursor()


    @lru_cache(30)
    def get_thumb_image(self, url):
        try:
            data = urlopen(url).read()
        except Exception as e:
            self.fail(e)
        else:
            self.success()
            return data

    @lru_cache(30)
    def getResult(self, param):
        try:
            resp = requests.get(CinemanaAPI.SEARCH_API + param)
        except Exception as e:
            # raise e
            self.fail(e)
        else:
            self.success()
            # self.url = resp.url
            # print(resp.url)
            return resp.text

if __name__ == "__main__":
    app = QApplication([])
    window  = MainApp()
    window.show()
    app.exec_()


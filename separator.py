import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '768')


Builder.load_string("""

#:import utils kivy.utils

<Button>
    font_size: 14
    size_hint: (1, None)
    height: 30
    background_normal: ""
    background_color: utils.get_color_from_hex("#333333")
    color: (1, 1, 1, 1)

<MyLayout>
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            size: self.size
            pos: self.pos

    log: log
    pathToPhoto: pathToPhoto

    BoxLayout:
        orientation: "horizontal"
        size: root.width, root.height


        BoxLayout:
            orientation: "vertical"
            BoxLayout:
                orientation: "horizontal"
                canvas.before:
                    Color:
                        rgba: (0.5, 0.5, 0.5, 1)
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint: (1, None)
                height: 100
                padding: 20
                BoxLayout:
                    orientation: "vertical"
                    Label:
                        id: pathToPhoto
                        text: "не выбрано"
                        color: (0, 0, 0, 1)
                    Button:
                        text: "Выберите папку с фото"
                        on_press: root.show_load('folderIn')
                BoxLayout:
                    orientation: "vertical"

                    Label:
                        text: "Субдиректории"

                    Switch:
                        id: subfolderSwitch
                        active: False
                        on_active: root.toggleSubfolder(self, self.active)
                Button:
                    id: selectCategor
                    text: "Категории"
                    size_hint: (None, None)
                    width: 140
                    height: 60
                    pos_hint: {'center_x': 0.5}
                    on_press: root.show_load('folderDir')


            BoxLayout:
                orientation: "vertical"
                Image:
                    id: vis_img

            BoxLayout:
                id: boxGrid
                orientation: "vertical"
                size_hint: (1, None)
                height: 90
                padding: 10
                background_color: (140/255, 140/255, 140/255, 1)
                canvas.before:
                    Color:
                        rgba: self.background_color
                    Rectangle:
                        size: self.size
                        pos: self.pos

        BoxLayout:
            orientation: "vertical"
            size_hint: (None, 1)
            width: 250
            background_color: (240/255, 540/255, 240/255, 1)
            canvas.before:
                Color:
                    rgba: self.background_color
                Rectangle:
                    size: self.size
                    pos: self.pos
            Label:
                text: "Журнал событий"
                size_hint: (1, None)
                height: 40
                color: (51/255.0, 51/255.0, 51/255.0, 1)
            TextInput:
                id: log
                multiline: True
                font_size: 10
                color: (134/255.0, 140/255.0, 147/255.0, 0.5)
                background_normal: ""
                background_color: (1, 1, 1, 0)
                padding: 5
                font_size: 12
            Button:
                text: "Очистить"
                on_press: root.clearLog()



""")

import os
import sys
import shutil

from os.path import sep, expanduser, isdir, dirname
from kivy_garden.filebrowser import FileBrowser


class WindowVideoFolder(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    reRootDir = ObjectProperty(None)

class MyLayout(Widget):
    list_img = []
    index = 0
    brouzerpath = ''

    path_kategor = ""

    log = ObjectProperty(None)

    def on_parent(self, widget, parent):
        self.no_foto()

    def writeLog(self, line):
        self.ids.log.text += (line + "\n")

    def clearLog(self):
        self.ids.log.text = ""

    def dismiss_popup(self):
        self._popup.dismiss()

    def parseFile(self):
        self.list_img = []
        self.index = 0
        path = self.ids.pathToPhoto.text
        subfolder = self.ids.subfolderSwitch.active
        print(f'Стартовая папка {path} Проваливаемся в субдиректории {subfolder}')

        if subfolder:
            for rootdir, dirs, files in os.walk(path):
                for file in files:
                    if (file.endswith("jpg") or file.endswith("png") or file.endswith("jpeg")):
                        self.list_img.append(os.path.join(rootdir, file))
        else:
            for file in os.listdir(path):
                if (file.endswith("jpg") or file.endswith("png") or file.endswith("jpeg")):
                    self.list_img.append(os.path.join(path, file))


        if (len(self.list_img)):
            self.writeLog("Найдено рисунков: " + str(len(self.list_img)))
            self.renderImg()
        else:
            self.writeLog("Рисунков не найдено. выберите другую папку")
            self.no_foto()
            self.list_img = []
            self.index = 0




    def renderImg(self, ind=0):
        self.ids.vis_img.source = self.list_img[ind]

    def toggleSubfolder(self, switchObject, switchValue):
        if (switchValue):
            self.writeLog("Режим анализа субдиректорий включен")
        else:
            self.writeLog("Режим анализа субдиректорий выключен")

        if (self.brouzerpath):
            self.parseFile()

    def show_load(self, folder):

        # print(self.get_disklist())
        # content = WindowVideoFolder(load=self.load, cancel=self.dismiss_popup)
        if sys.platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
        browser = FileBrowser(select_string='Выбрать',
                              dirselect=True,
                              cancel_string="Отмена",
                              favorites=[(user_path, 'Documents')])
        if(self.brouzerpath):
            browser.path = self.brouzerpath
        if (folder == 'folderIn'):
            browser.bind(
                        on_success=self._fbrowser_successIn,
                        on_canceled=self._fbrowser_canceled)
        else:
            browser.bind(
                on_success=self._fbrowser_successCat,
                on_canceled=self._fbrowser_canceled)

        self._popup = Popup(title="Выберите папку", content=browser,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        print('*'*50)
        print(folder)
        print()

    def _fbrowser_canceled(self, instance):
        self.dismiss_popup()

    def stebBackUrl(self, url):
        backUrl = '\\'.join(str(url).split('\\')[:-1])
        if (backUrl[-1] == ":"):
            backUrl += "\\"
        return backUrl


    def _fbrowser_successIn(self, instance):
        print("Выбор папки")
        if (instance.selection):
            self.ids.pathToPhoto.text = str(instance.selection[0])
            self.writeLog("Выбрана директория " + str(instance.selection[0]))
            self.brouzerpath = self.stebBackUrl(instance.selection[0])
            self.list_img = []
            self.index = 0
            self.dismiss_popup()
            self.parseFile()

    def _fbrowser_successCat(self, instance):
        print("Выбор категорий")
        if (instance.selection):
            dir = str(instance.selection[0])
            self.writeLog("Папка с категориями " + str(instance.selection[0]))
            self.path_kategor = str(instance.selection[0])
            self.brouzerpath = self.stebBackUrl(instance.selection[0])
            # self.ids.btn_wrapper.clear_widgets()
            self.dismiss_popup()
            self.createBtnCategir(dir)

    def createBtnCategir(self, dir):
        listCategor = os.listdir(dir)
        contCat = 0
        listCat = []
        self.ids.boxGrid.clear_widgets()
        gl = GridLayout(
            spacing =  10,
            padding = 0,
            rows = 1,
            size_hint = (None, 1),
            width = 600,
            pos_hint = {'center_x': 0.5})
        for i in range(len(listCategor)):
            if ( not ('.' in listCategor[i])):
                listCat.append(listCategor[i])
        contCat = len(listCat)
        for i in range(contCat):
            button = Button(text=listCat[i], height=70, on_press=self.go_folder)
            gl.add_widget(button)
        self.writeLog("Обнаружены категорий " + str(contCat))

        # self.ids.btn_wrapper.remove_widget(self.ids.selectCategor)
        if (contCat <= 5):
            gl.cols = None
            gl.rows = 1
            self.ids.boxGrid.height = 90
        elif ( 5 < contCat <= 10):
            gl.cols = None
            gl.rows = 2
            self.ids.boxGrid.height = 170
        else:
            gl.cols = None
            gl.rows = 3
            self.ids.boxGrid.height = 250
        self.ids.boxGrid.add_widget(gl)

    def remaneFile(self, nameFile, path):
        # name = nameFile.split(".")
        filename, file_extension = os.path.splitext(nameFile)
        print()
        print()
        print(filename)
        print(file_extension)
        ind = 0
        while True:
            if (ind == 0):
                index = ''
            else:
                index = "_"+str(ind)
            fin_filename = filename+str(index)+file_extension
            print(f"Имя файла {fin_filename}")
            print(f"Ищем по адресу {os.path.join(path, fin_filename)}")
            if (os.path.isfile(os.path.join(path, fin_filename))):
                print("Файл с таким именем есть, меняем имя")
                ind += 1
            else:
                break
        # time.sleep(0.2)
        return fin_filename

    def go_folder(self, instance):
        print(self.ids.vis_img.source)
        if ('no-pfoto.jpg' in self.ids.vis_img.source):
            self.show_load('folderIn')
        else:
            full_path = os.path.join(str(self.path_kategor), instance.text)
            file_name = os.path.basename(self.list_img[self.index])

            new_name = self.remaneFile(nameFile=file_name, path=full_path)
            self.writeLog("Перемещаем файл " + self.list_img[self.index] + " в директорию " + full_path )
            shutil.move(self.list_img[self.index], os.path.join(full_path, new_name))
            self.writeLog(str(self.index+1) + " из " + str(len(self.list_img)))

            if (self.index+1 != len(self.list_img)):
                self.index += 1
                self.renderImg(self.index)
            else:
                self.no_foto()

    def no_foto(self):
        self.ids.vis_img.source = self.resource_path("no-pfoto.jpg")



    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)



class testApp(App):
    def build(self):
        return MyLayout()

if __name__ == "__main__":
    testApp().run()


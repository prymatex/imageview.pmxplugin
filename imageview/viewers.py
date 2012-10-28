#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from PIL import Image
import random
from bisect import bisect

from prymatex.qt import QtCore, QtGui
from prymatex.core import PMXBaseEditor

class PMXImageViewer(QtGui.QWidget, PMXBaseEditor):
    ZOOM_MAX = 2
    ZOOM_MIN = .1
    qimage = QtGui.QImage()
    def __init__(self, parent = None):
        QtGui.QLabel.__init__(self, parent)
        PMXBaseEditor.__init__(self)
        self.setupUi(self)
        self.setupZoom()

    def setupUi(self, ImageViewWidget):
        ImageViewWidget.setObjectName("ImageViewWidget")
        self.verticalLayout = QtGui.QVBoxLayout(ImageViewWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtGui.QScrollArea(ImageViewWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.labelImage = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.labelImage.setText("")
        self.labelImage.setObjectName("labelImage")
        self.verticalLayout_2.addWidget(self.labelImage)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(ImageViewWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.sliderZoom = QtGui.QSlider(ImageViewWidget)
        self.sliderZoom.setMinimum(1)
        self.sliderZoom.setProperty("value", 50)
        self.sliderZoom.setOrientation(QtCore.Qt.Horizontal)
        self.sliderZoom.setInvertedAppearance(False)
        self.sliderZoom.setTickPosition(QtGui.QSlider.TicksBelow)
        self.sliderZoom.setObjectName("sliderZoom")
        self.horizontalLayout.addWidget(self.sliderZoom)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.scrollAreaWidgetContents.setStyleSheet("background-color: black;")
        
        QtCore.QMetaObject.connectSlotsByName(ImageViewWidget)

    def setupZoom(self):
        self.slidemin, self.slidemax = self.sliderZoom.minimum(), self.sliderZoom.maximum()
        self.slidemed = (self.slidemax - self.slidemin) / 2

        self.zoom_under = (1 - self.ZOOM_MIN) / float(self.slidemax - self.slidemed)
        self.zoom_over = (self.ZOOM_MAX - 1) / float(self.slidemax - self.slidemed)
    
    _zoom = 1
    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if self.qimage.isNull():
            return
        h, w = self.qimage.width() * value, self.qimage.height() * value
        zoomedPixmap = QtGui.QPixmap(self.qimage).scaled(h, w)
        self.labelImage.setPixmap(zoomedPixmap)

    @classmethod
    def acceptFile(cls, filePath, mimetype):
        return re.compile("image/.*").match(mimetype) is not None

    def open(self, filePath):
        self.application.fileManager.openFile(filePath)
        self.setFilePath(filePath)

    def setFilePath(self, filePath):
        PMXBaseEditor.setFilePath(self, filePath)
        qimg = QtGui.QImage(filePath)
        if not qimg.isNull():
            self.qimage = qimg
            self.labelImage.setPixmap(QtGui.QPixmap(qimg))
        else:
            print "No es una imagen valida"
        
    @classmethod
    def contributeToMainMenu(cls, addonsClasses):
        return { "Image": { 'title': "Images", 
                            'items': [ 
                            {   'title': "Convert To ASCII",
                                'callback': cls.on_actionConvertToASCII_toggled
                            },
                            { 'title': "Opcion2" },
                            { 'title': "Opcion3" },
                            ]
                        }
                }
             
    def on_sliderZoom_sliderReleased(self):
        value = self.sliderZoom.value()
        if value == self.slidemed:
            self.zoom = 1
        elif value > self.slidemed:
            self.zoom = self.zoom_over * value
        else:
            self.zoom = self.zoom_under * value

    def on_actionConvertToASCII_toggled(self):
        """
        ASCII Art maker
        Creates an ascii art image from an arbitrary image
        Created on 7 Sep 2009
        
        @author: Steven Kay
        """
        # greyscale.. the following strings represent
        # 7 tonal ranges, from lighter to darker.
        # for a given pixel tonal level, choose a character
        # at random from that range.
        
        greyscale = [
                    " ",
                    " ",
                    ".,-",
                    "_ivc=!/|\\~",
                    "gjez2]/(YL)t[+T7Vf",
                    "mdK4ZGbNDXY5P*Q",
                    "W8KMA",
                    "#%$"
                    ]
        
        # using the bisect class to put luminosity values
        # in various ranges.
        # these are the luminosity cut-off points for each
        # of the 7 tonal levels. At the moment, these are 7 bands
        # of even width, but they could be changed to boost
        # contrast or change gamma, for example.
        
        zonebounds=[36,72,108,144,180,216,252]
        
        # open image and resize
        # experiment with aspect ratios according to font
        
        im = Image.open(self.filePath)
        im = im.resize((160, 75), Image.BILINEAR)
        im = im.convert("L") # convert to mono
        
        # now, work our way over the pixels
        # build up str
        
        imageASCII = ""
        for y in range(0, im.size[1]):
            for x in range(0, im.size[0]):
                lum = 255 - im.getpixel((x,y))
                row = bisect(zonebounds,lum)
                possibles = greyscale[row]
                imageASCII += possibles[random.randint(0,len(possibles)-1)]
            imageASCII += "\n"

        #TODO: Una forma menos promiscua de hacer esto
        editor = self.application.getEditorInstance()
        editor.setPlainText(imageASCII)
        self.application.mainWindow.addEditor(editor, True)

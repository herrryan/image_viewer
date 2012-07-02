'''
Created on Mar 23, 2011

@author: guof
'''

from PyQt4 import QtGui, QtCore
from main_auto import *
import glob
import json
import os
import sys



class ClassImage(object):


    def __init__(self):
        
        self.classifications = {'scene':[]}
    
    def to_file(self, file):
    
        '''Serialize object to file.'''
        with open(file,'w') as f:
            json.dump(self.classifications, f)

    def from_file(self, file):
        
        '''Read serialized object from file.'''
        with open(file,'r') as f:
            return json.load(f)

class ClassificationWindow(Ui_Dialog):

    def __init__(self):
        
        self.current_image = None
        self.image_folder = '.'
        self.classification_folder = '.'
        self.file_name = ''
        self.current_index = 0

    def setupUi(self, Dialog):
        
        self.qt_window = Dialog

        Ui_Dialog.setupUi(self,Dialog)
        QtCore.QObject.connect(self.commandLinkButton,QtCore.SIGNAL("clicked()"), self.next)
        QtCore.QObject.connect(self.commandLinkButton_2, QtCore.SIGNAL("clicked()"), self.prev)
        QtCore.QObject.connect(self.rb_inside, QtCore.SIGNAL("clicked()"), self._in)
        QtCore.QObject.connect(self.rb_outside, QtCore.SIGNAL("clicked()"), self._out)
        QtCore.QObject.connect(self.rb_junk, QtCore.SIGNAL("clicked()"), self._junk)
        QtCore.QObject.connect(self.btn_open, QtCore.SIGNAL("clicked()"), self.choose_image_folder_dialog)
        QtCore.QObject.connect(self.btn_classdir, QtCore.SIGNAL("clicked()"), self.choose_classification_folder_dialog)
        QtCore.QObject.connect(self.cb_unlassified, QtCore.SIGNAL('stateChanged(int)'), self.class_or_unclass)
        scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(scene)
    def retranslateUi(self, Dialog):
        Ui_Dialog.retranslateUi(self,Dialog)
        
    def class_or_unclass(self):
        
        if self.cb_unlassified.isChecked():
            self.show_unclassified_image()
        else:
            self.populate_images_from_folder()
            self.show_current_image()

    def choose_image_folder_dialog(self):
        
        self.image_folder = str(QtGui.QFileDialog.getExistingDirectory(self.qt_window, 'Choose image folder', QtCore.QDir.currentPath(), QtGui.QFileDialog.ShowDirsOnly))
        self.populate_images_from_folder()
        self.show_current_image()
            
    def choose_classification_folder_dialog(self):
        
        self.classification_folder = str(QtGui.QFileDialog.getExistingDirectory(self.qt_window, 'Choose classification file folder', QtCore.QDir.currentPath(), QtGui.QFileDialog.ShowDirsOnly))
        img_id, _ = os.path.splitext(os.path.basename(self.image_files[self.current_index]))
        self.file_name = os.path.join(self.classification_folder, img_id+'.json')  
        self.populate_classfiles_from_folder()

    def next(self):
        
        self.current_index = (self.current_index + 1) % len(self.image_files)
        if self.current_index % len(self.image_files) == 0:
            self.graphicsView.scene().clear()
        else:
            self.show_current_image()

    def prev(self):

        self.current_index = ((self.current_index - 1) + len(self.image_files)) % len(self.image_files)
        self.show_current_image()
        
    def show_unclassified_image(self):
        
        self.graphicsView.scene().clear()
        self.populate_classfiles_from_folder()
        for file_name in self.class_files:
            file = os.path.basename(file_name)
            img_id, _ = os.path.splitext(file)
            self.image_files.remove(os.path.join(self.image_folder, img_id+'.jpg'))
        if len(self.image_files) == 0:
            QtGui.QMessageBox.information(self.qt_window, 'Congratulations', 'You have classified all images', QtGui.QMessageBox.Ok)
        else:
            self.show_current_image()
        
    def show_current_image(self):
        img = os.path.basename(self.image_files[self.current_index])
        self.fileName.setPlainText(img)
        # reset classification group
        self.rb_inside.setAutoExclusive(False)
        self.rb_outside.setAutoExclusive(False)
        self.rb_junk.setAutoExclusive(False)
        self.rb_inside.setChecked(False)
        self.rb_outside.setChecked(False)
        self.rb_junk.setChecked(False)
        self.rb_inside.setAutoExclusive(True)
        self.rb_outside.setAutoExclusive(True)
        self.rb_junk.setAutoExclusive(True)
        # if already classified -> toggle right button        
        if os.path.exists(self.file_name):
            scene = self.current_image.from_file(self.file_name)
            if scene == {'scene':'in'}:
                self.rb_inside.setChecked(True)
            if scene == {'scene':'out'}:
                self.rb_outside.setChecked(True)
            if scene == {'scene':'junk'}:
                self.rb_junk.setChecked(True)
        
        self.current_image = ClassImage()
        
        self.graphicsView.scene().clear()
        img = QtGui.QPixmap(self.image_files[self.current_index])
        img_scaled = img.scaled(
            self.graphicsView.size(),
            QtCore.Qt.KeepAspectRatio)
        self.graphicsView.scene().addPixmap(img_scaled)
        
    def populate_classfiles_from_folder(self):
        
        self.class_files = glob.glob('%s/*.json' % self.classification_folder)
        if not self.class_files:
            QtGui.QMessageBox.critical(self.qt_window, 'Oops', 'Didn\'t not find any json files, it is a fresh start' , QtGui.QMessageBox.Ok)     
            
    def populate_images_from_folder(self):
        
        self.image_files = glob.glob('%s/*.jpg' % self.image_folder)
        if not self.image_files:
            self.graphicsView.scene().clear()
            self.grp_class_controls.setEnabled(False)
            self.control_buttons.setEnabled(False)
            QtGui.QMessageBox.critical(self.qt_window,'Error',
                                     'Didn\'t find any images',
                                     QtGui.QMessageBox.Ok)
        else:
            self.current_index = 0
            
            self.grp_class_controls.setEnabled(True)
            self.control_buttons.setEnabled(True)


    def _in(self):
        
        self._set_scene_class('in')
        next(self)

    def _out(self):
        
        self._set_scene_class('out')
        next(self)

    def _junk(self):
        
        self._set_scene_class('junk')
        next(self)

    def _set_scene_class(self, scene):
        
        if self.current_image:
            self.current_image.classifications['scene'] = scene
            img = os.path.basename(self.image_files[self.current_index])
            img_id, _ = os.path.splitext(img)
            self.current_image.to_file('%s/%s.json' % (self.classification_folder, img_id))


app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QDialog()
ui = ClassificationWindow()
ui.setupUi(MainWindow)
MainWindow.show()



# Now we can start it.
sys.exit(app.exec_())

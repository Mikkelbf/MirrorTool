from Qt import QtCore, QtWidgets
from functools import partial
from exportcharactertool import ExportCharacterTool
import pymel.core as pm
import mirrorfunctions as mf
import os
import json
import utilities


class MirrorTool(QtWidgets.QMainWindow):

    def __init__(self):

        super(MirrorTool, self).__init__(parent=utilities.get_maya_main_window())

        self.setMaximumSize(0, 0)  # good thing, Qt's accommodating to ignorance

        self._dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'characters\\')

        self._plane = None
        self._planeMtl = None
        self._planeSg = None

        self._internal_ui_change = False

        self.__setup_ui()
        self.__set_namespaces()
        self.__set_frame_range()
        self.__load_characters()

    def closeEvent(self, event):
        # deletes plane, if it exists, on close

        super(MirrorTool, self).closeEvent(event)

        if self._plane is not None and self._planeMtl is not None and self._planeSg is not None:
            utilities.delete_mirror(self._plane, self._planeMtl, self._planeSg)

        try:
            ExportCharacterToolWin.close()
        except:
            pass

    def __setup_ui(self):

        self.setWindowTitle('Mirror Tool')
        self.setObjectName('MirrorToolWindow')

        # some widget I can use as parent for the main layout
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)

        # main vertical layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        ###############################################################

        # character layout
        self.characterLayout = QtWidgets.QHBoxLayout()
        self.characterLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.characterLayout)

        # character label
        self.characterLabel = QtWidgets.QLabel('Character:')
        self.characterLabel.setMaximumWidth(60)
        self.characterLabel.setMinimumWidth(60)
        self.characterLayout.addWidget(self.characterLabel)

        # character combobox
        self.characterComboBox = QtWidgets.QComboBox()
        self.characterLayout.addWidget(self.characterComboBox)

        # character export button
        self.characterExportBtn = QtWidgets.QPushButton('New character')
        self.characterExportBtn.setObjectName("characterBrowseBtn")
        self.characterExportBtn.setMaximumWidth(90)
        self.characterExportBtn.setMinimumWidth(90)
        self.characterLayout.addWidget(self.characterExportBtn)
        self.characterExportBtn.clicked.connect(self.__show_export_character_tool)

        # character reload button
        self.characterReloadBtn = QtWidgets.QPushButton('Reload')
        self.characterReloadBtn.setObjectName("characterBrowseBtn")
        self.characterReloadBtn.setMaximumWidth(50)
        self.characterReloadBtn.setMinimumWidth(50)
        self.characterLayout.addWidget(self.characterReloadBtn)
        self.characterReloadBtn.clicked.connect(self.__load_characters)

        # namespace layout
        self.nameSpaceLayout = QtWidgets.QHBoxLayout()
        self.nameSpaceLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.nameSpaceLayout)

        # namespace label
        self.nameSpaceLabel = QtWidgets.QLabel('Namespace:')
        self.nameSpaceLabel.setMaximumWidth(60)
        self.nameSpaceLabel.setMinimumWidth(60)
        self.nameSpaceLayout.addWidget(self.nameSpaceLabel)

        # namespace combobox
        self.nameSpaceComboBox = QtWidgets.QComboBox()
        self.nameSpaceLayout.addWidget(self.nameSpaceComboBox)

        # namespace reload button
        self.nameSpaceReloadBtn = QtWidgets.QPushButton('Reload')
        self.nameSpaceReloadBtn.setObjectName("nameSpaceReloadBtn")
        self.nameSpaceReloadBtn.setMaximumWidth(50)
        self.nameSpaceReloadBtn.setMinimumWidth(50)
        self.nameSpaceLayout.addWidget(self.nameSpaceReloadBtn)
        self.nameSpaceReloadBtn.clicked.connect(self.__set_namespaces)

        # line separator
        self.lineBelowCharacter = QtWidgets.QFrame()
        self.lineBelowCharacter.setFrameShape(QtWidgets.QFrame.HLine)
        self.mainLayout.addWidget(self.lineBelowCharacter)

        ###############################################################

        # mirror options layout
        self.mirrorOptionsLayout = QtWidgets.QHBoxLayout()
        self.mirrorOptionsLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.mirrorOptionsLayout)

        # yz label
        self.yzLabel = QtWidgets.QLabel('yz')
        self.yzLabel.setMaximumWidth(10)
        self.yzLabel.setMinimumWidth(10)
        self.mirrorOptionsLayout.addWidget(self.yzLabel)

        # yz checkbox
        self.yzCheckBox = QtWidgets.QCheckBox()
        self.mirrorOptionsLayout.addWidget(self.yzCheckBox)
        # yz checked as default
        self.yzCheckBox.setCheckState(QtCore.Qt.Checked)

        # xz label
        self.xzLabel = QtWidgets.QLabel('xz')
        self.xzLabel.setMaximumWidth(10)
        self.xzLabel.setMinimumWidth(10)
        self.mirrorOptionsLayout.addWidget(self.xzLabel)

        # xz checkbox
        self.xzCheckBox = QtWidgets.QCheckBox()
        self.mirrorOptionsLayout.addWidget(self.xzCheckBox)

        # xy label
        self.xyLabel = QtWidgets.QLabel('xy')
        self.xyLabel.setMaximumWidth(10)
        self.xyLabel.setMinimumWidth(10)
        self.mirrorOptionsLayout.addWidget(self.xyLabel)

        # xy checkbox
        self.xyCheckBox = QtWidgets.QCheckBox()
        self.mirrorOptionsLayout.addWidget(self.xyCheckBox)

        # custom plane label
        self.customLabel = QtWidgets.QLabel('custom plane')
        self.customLabel.setMaximumWidth(70)
        self.customLabel.setMinimumWidth(70)
        self.mirrorOptionsLayout.addWidget(self.customLabel)

        # custom plane checkbox
        self.customCheckBox = QtWidgets.QCheckBox()
        self.mirrorOptionsLayout.addWidget(self.customCheckBox)
        self.customCheckBox.stateChanged.connect(self.__set_plane)

        # line separator
        self.lineBelowMirrorOptions = QtWidgets.QFrame()
        self.lineBelowMirrorOptions.setFrameShape(QtWidgets.QFrame.HLine)
        self.mainLayout.addWidget(self.lineBelowMirrorOptions)

        ######################## UI call back #########################
        # only one checkbox can be set at a time

        self.yzCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                     self.yzCheckBox,
                                                     [self.xzCheckBox,
                                                      self.xyCheckBox,
                                                      self.customCheckBox]))

        self.xzCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                     self.xzCheckBox,
                                                     [self.yzCheckBox,
                                                      self.xyCheckBox,
                                                      self.customCheckBox]))

        self.xyCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                     self.xyCheckBox,
                                                     [self.yzCheckBox,
                                                      self.xzCheckBox,
                                                      self.customCheckBox]))

        self.customCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                         self.customCheckBox,
                                                         [self.yzCheckBox,
                                                          self.xyCheckBox,
                                                          self.xzCheckBox]))

        ###############################################################

        # in range layout
        self.inRangeLayout = QtWidgets.QHBoxLayout()
        self.inRangeLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.inRangeLayout)

        # in range label
        self.inRangeLabel = QtWidgets.QLabel('In range')
        self.inRangeLabel.setMaximumWidth(45)
        self.inRangeLabel.setMinimumWidth(45)
        self.inRangeLayout.addWidget(self.inRangeLabel)

        # in range checkbox
        self.inRangeCheckBox = QtWidgets.QCheckBox()
        self.inRangeLayout.addWidget(self.inRangeCheckBox)

        # frame range layout
        self.frameRangeLayout = QtWidgets.QHBoxLayout()
        self.frameRangeLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.frameRangeLayout)

        # start frame
        self.startFrameTextBox = QtWidgets.QLineEdit()
        self.startFrameTextBox.setMaximumWidth(50)
        self.startFrameTextBox.setMinimumWidth(50)
        self.frameRangeLayout.addWidget(self.startFrameTextBox)
        self.startFrameTextBox.setEnabled(False)

        # end frame
        self.endFrameTextBox = QtWidgets.QLineEdit()
        self.endFrameTextBox.setMaximumWidth(50)
        self.endFrameTextBox.setMinimumWidth(50)
        self.frameRangeLayout.addWidget(self.endFrameTextBox)
        self.endFrameTextBox.setEnabled(False)

        # frame range button
        self.frameRangeBtn = QtWidgets.QPushButton('From scene')
        self.frameRangeBtn.setObjectName("frameRangeBtn")
        self.frameRangeBtn.setMaximumWidth(60)
        self.frameRangeBtn.setMinimumWidth(60)
        self.frameRangeLayout.addWidget(self.frameRangeBtn)
        self.frameRangeBtn.clicked.connect(self.__set_frame_range)
        self.frameRangeBtn.setEnabled(False)

        # line separator
        self.lineBelowFrameRangeOptions = QtWidgets.QFrame()
        self.lineBelowFrameRangeOptions.setFrameShape(QtWidgets.QFrame.HLine)
        self.mainLayout.addWidget(self.lineBelowFrameRangeOptions)

        ######################## UI call back #########################
        # frame range should only be enabled when box is checked

        self.inRangeCheckBox.stateChanged.connect(partial(self.__uicb_match_state_of_box,
                                                          self.inRangeCheckBox,
                                                          self.startFrameTextBox))

        self.inRangeCheckBox.stateChanged.connect(partial(self.__uicb_match_state_of_box,
                                                          self.inRangeCheckBox,
                                                          self.endFrameTextBox))

        self.inRangeCheckBox.stateChanged.connect(partial(self.__uicb_match_state_of_box,
                                                          self.inRangeCheckBox,
                                                          self.frameRangeBtn))

        ###############################################################

        # mirror button
        self.mirrorBtn = QtWidgets.QPushButton('mirror')
        self.mirrorBtn.setObjectName("mirrorBtn")
        self.mirrorBtn.setMaximumWidth(60)
        self.mirrorBtn.setMinimumWidth(60)
        self.mainLayout.addWidget(self.mirrorBtn)
        self.mirrorBtn.clicked.connect(self.__mirror)

    def __uicb_set_boxes(self, driver, boxList=[], *args):
        # since this function will be called on the checkbox the user is checking
        # and consequently on all checkboxes the function is checking, on the first
        # run through I set the _internal_ui_change variable to True in order to
        # break out of the function on all other calls than the first one.

        if self._internal_ui_change:
            return

        self._internal_ui_change = True
        for box in boxList:
            box.setCheckState(QtCore.Qt.Unchecked)
        self._internal_ui_change = False

        # if the driver box was unchecked, check it back on. One box must be checked
        driver.setCheckState(QtCore.Qt.Checked)

    def __uicb_match_state_of_box(self, driver, driven, *args):
        # checks the state of the driver and sets the state of the driven to match it

        state = driver.checkState()

        try:
            driven.setCheckState(state)
        except AttributeError:
            if state == QtCore.Qt.CheckState.Unchecked:
                state = False
            else:
                state = True
            driven.setEnabled(state)

    def __load_characters(self):
        self.characterComboBox.clear()

        characters = os.listdir(self._dir)

        for character in characters:
            character = character.split('.')[0]
            self.characterComboBox.addItem(character)

    def __set_plane(self, *args):
        # creates mirror plane if it does not exist, deletes it if it does

        if self._plane is None and self._planeMtl is None and self._planeSg is None:
            self._plane, self._planeMtl, self._planeSg = utilities.create_mirror()
        else:
            utilities.delete_mirror(self._plane, self._planeMtl, self._planeSg)
            self._plane = None
            self._planeMtl = None
            self._planeSg = None

    def __set_frame_range(self, *args):
        # gets frame range from scene and puts it to the start and end frame textboxes

        frameRange = utilities.get_scene_range()

        self.startFrameTextBox.setText(str(frameRange[0]))
        self.endFrameTextBox.setText(str(frameRange[1]))

    def __set_namespaces(self, *args):
        # fills the namespace combobox with namespaces from the scene
        self.nameSpaceComboBox.clear()

        namespaces = utilities.get_namespaces()

        for name in namespaces:
            self.nameSpaceComboBox.addItem(name)

    def __get_namespace(self):
        namespace = self.nameSpaceComboBox.currentText()

        if namespace != 'None':
            return '%s:' % namespace
        else:
            return ''

    def __get_plane(self):
        if self.yzCheckBox.isChecked():
            return 'yz'
        elif self.xyCheckBox.isChecked():
            return 'xy'
        elif self.xzCheckBox.isChecked():
            return 'xz'
        else:
            return self._plane

    def __get_character_dict(self):
        with open(os.path.join(self._dir, self.characterComboBox.currentText() + '.json')) as f:
            objectDict = json.load(f)

        return objectDict

    def __get_frame_range(self):
        if self.inRangeCheckBox.isChecked():
            return int(self.startFrameTextBox.text().split('.')[0]), int(self.endFrameTextBox.text().split('.')[0])
        else:
            return int(pm.currentTime()), int(pm.currentTime())

    def __mirror(self, *args):
        # get transform objectDict, namespace, frameRange, plane
        # set transform transformList, frameRange

        characterDict = self.__get_character_dict()
        nameSpace = self.__get_namespace()
        frameRange = self.__get_frame_range()
        plane = self.__get_plane()

        transformations = mf.get_objects_mirror_transformations(characterDict, nameSpace, frameRange, plane)

        mf.set_transformations(transformations, frameRange)

    def __show_export_character_tool(self, *args):
        global ExportCharacterToolWin
        try:
            ExportCharacterToolWin.close()
        except:
            pass
        ExportCharacterToolWin = ExportCharacterTool(self._dir, parent=self)
        ExportCharacterToolWin.show()


def show():
    global MirrorToolWin
    try:
        MirrorToolWin.close()
    except:
        pass
    MirrorToolWin = MirrorTool()
    MirrorToolWin.show()
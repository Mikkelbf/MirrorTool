from PySide import QtGui, QtCore
from maya import cmds
from functools import partial
import pymel.core as pm
import difflib
import os
import json
import utilities_2016 as utilities


class ExportCharacterTool(QtGui.QMainWindow):
    def __init__(self, _dir, parent=None):
        super(ExportCharacterTool, self).__init__(parent)

        self._internal_ui_change = False

        self._dir = _dir

        self.objects = list()
        self.objectsOnLeft = list()
        self.objectsOnRight = list()

        self.entries = list()
        self.comboBoxesLeft = list()
        self.comboBoxesRight = list()

        self.__setup_ui()

    def __setup_ui(self):

        self.setWindowTitle("Character Mirror Definition")

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)

        self.orientationLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.orientationLayout)

        self.forwardLayout = QtGui.QHBoxLayout()
        self.forwardLayout.setAlignment(QtCore.Qt.AlignTop)
        self.forwardLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.forwardLayout)

        self.forwardLabel = QtGui.QLabel('character forward:')
        self.forwardLabel.setMinimumWidth(100)
        self.forwardLayout.addWidget(self.forwardLabel)

        self.forwardXLabel = QtGui.QLabel('X:')
        self.forwardXLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.forwardLayout.addWidget(self.forwardXLabel)

        self.forwardXCheckBox = QtGui.QCheckBox()
        self.forwardLayout.addWidget(self.forwardXCheckBox)

        self.forwardYLabel = QtGui.QLabel('Y:')
        self.forwardYLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.forwardLayout.addWidget(self.forwardYLabel)

        self.forwardYCheckBox = QtGui.QCheckBox()
        self.forwardLayout.addWidget(self.forwardYCheckBox)

        self.forwardZLabel = QtGui.QLabel('Z:')
        self.forwardZLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.forwardLayout.addWidget(self.forwardZLabel)

        self.forwardZCheckBox = QtGui.QCheckBox()
        self.forwardZCheckBox.setCheckState(QtCore.Qt.Checked)
        self.forwardLayout.addWidget(self.forwardZCheckBox)

        self.upLayout = QtGui.QHBoxLayout()
        self.upLayout.setAlignment(QtCore.Qt.AlignTop)
        self.upLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.upLayout)

        self.upLabel = QtGui.QLabel('character up:')
        self.upLabel.setMinimumWidth(100)
        self.upLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.upLayout.addWidget(self.upLabel)

        self.upXLabel = QtGui.QLabel('X:')
        self.upXLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.upLayout.addWidget(self.upXLabel)

        self.upXCheckBox = QtGui.QCheckBox()
        self.upLayout.addWidget(self.upXCheckBox)

        self.upYLabel = QtGui.QLabel('Y:')
        self.upYLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.upLayout.addWidget(self.upYLabel)

        self.upYCheckBox = QtGui.QCheckBox()
        self.upYCheckBox.setCheckState(QtCore.Qt.Checked)
        self.upLayout.addWidget(self.upYCheckBox)

        self.upZLabel = QtGui.QLabel('Z:')
        self.upZLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.upLayout.addWidget(self.upZLabel)

        self.upZCheckBox = QtGui.QCheckBox()
        self.upLayout.addWidget(self.upZCheckBox)

        # UI Callback
        self.forwardXCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                           self.forwardXCheckBox,
                                                           self.upXCheckBox,
                                                           [self.forwardYCheckBox,
                                                            self.forwardZCheckBox]))

        self.forwardYCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                           self.forwardYCheckBox,
                                                           self.upYCheckBox,
                                                           [self.forwardXCheckBox,
                                                            self.forwardZCheckBox]))

        self.forwardZCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                           self.forwardZCheckBox,
                                                           self.upZCheckBox,
                                                           [self.forwardXCheckBox,
                                                            self.forwardYCheckBox]))

        self.upXCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                      self.upXCheckBox,
                                                      self.forwardXCheckBox,
                                                      [self.upYCheckBox,
                                                       self.upZCheckBox]))

        self.upYCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                      self.upYCheckBox,
                                                      self.forwardYCheckBox,
                                                      [self.upXCheckBox,
                                                       self.upZCheckBox]))

        self.upZCheckBox.stateChanged.connect(partial(self.__uicb_set_boxes,
                                                      self.upZCheckBox,
                                                      self.forwardZCheckBox,
                                                      [self.upXCheckBox,
                                                       self.upYCheckBox]))

        self.listLayout = QtGui.QHBoxLayout()
        self.listLayout.setAlignment(QtCore.Qt.AlignTop)
        self.mainLayout.addLayout(self.listLayout)

        self.listOneLayout = QtGui.QVBoxLayout()
        self.listOneLayout.setAlignment(QtCore.Qt.AlignTop)

        self.listOneScroll = QtGui.QScrollArea()
        self.listOneScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listOneScroll.setMinimumWidth(350)
        self.listOneScroll.setMinimumHeight(500)
        self.listOneScroll.setWidgetResizable(True)

        self.listOneScrollWidget = QtGui.QWidget(self.listOneScroll)
        self.listOneScrollWidget.setLayout(self.listOneLayout)

        self.listOneScroll.setWidget(self.listOneScrollWidget)
        self.listLayout.addWidget(self.listOneScroll)

        self.addLayout = QtGui.QHBoxLayout()
        self.addLayout.setAlignment(QtCore.Qt.AlignTop)

        self.addButton = QtGui.QPushButton('Add')
        self.addLayout.addWidget(self.addButton)
        self.addButton.clicked.connect(self.__add_entry)

        self.removeButton = QtGui.QPushButton('Remove All')
        self.addLayout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(self.__remove_all_entries)

        self.listOneLayout.addLayout(self.addLayout)

        self.listTwoLayout = QtGui.QVBoxLayout()
        self.listTwoLayout.setAlignment(QtCore.Qt.AlignTop)
        self.listLayout.addLayout(self.listTwoLayout)

        self.infoBox = QtGui.QPlainTextEdit()
        self.infoBox.setMinimumWidth(200)
        self.infoBox.setMaximumWidth(200)
        self.infoBox.setMinimumHeight(400)
        self.listTwoLayout.addWidget(self.infoBox)

        self.matchButton = QtGui.QPushButton('Auto Match')
        self.listTwoLayout.addWidget(self.matchButton)
        self.matchButton.clicked.connect(self.__auto_match)

        self.addSelectedButton = QtGui.QPushButton('Add Selected')
        self.addSelectedButton.clicked.connect(self.__add_selected)
        self.listTwoLayout.addWidget(self.addSelectedButton)

        self.exportButton = QtGui.QPushButton('Export')
        self.exportButton.setMaximumWidth(50)
        self.exportButton.clicked.connect(self.__export)
        self.mainLayout.addWidget(self.exportButton)

    def __add_entry(self):
        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.entries.append(layout)

        # add remove button
        button = QtGui.QPushButton('Remove')
        layout.addWidget(button)
        button.clicked.connect(partial(self.__remove_entry, layout))

        # add comboboxes
        comboBoxOne = QtGui.QComboBox()
        comboBoxTwo = QtGui.QComboBox()

        self.comboBoxesLeft.append(comboBoxOne)
        self.comboBoxesRight.append(comboBoxTwo)

        comboBoxOne.activated.connect(self.__update)
        comboBoxTwo.activated.connect(self.__update)

        layout.addWidget(comboBoxOne)
        layout.addWidget(comboBoxTwo)

        self.listOneLayout.insertLayout(self.listOneLayout.count() - 1, layout)

        self.__update()

    def __uicb_set_boxes(self, driver, match, boxList=[], *args):
        # since this function will be called on the checkbox the user is checking
        # and consequently on all checkboxes the function is checking, on the first
        # run through I set the _internal_ui_change variable to True in order to
        # break out of the function on all other calls than the first one.

        if self._internal_ui_change:
            return

        if match.checkState() == QtCore.Qt.CheckState.Checked:
            # can't have character with forward and up as the same
            self._internal_ui_change = True
            driver.setCheckState(QtCore.Qt.Unchecked)
            self._internal_ui_change = False

        else:
            self._internal_ui_change = True
            for box in boxList:
                box.setCheckState(QtCore.Qt.Unchecked)
            # if the driver box was unchecked, check it back on. One box must be checked
            driver.setCheckState(QtCore.Qt.Checked)
            self._internal_ui_change = False

    def __remove_all_entries(self):
        for layout in self.entries:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

            layout.deleteLater()

        self.entries = list()
        self.comboBoxesLeft = list()
        self.comboBoxesRight = list()
        self.checkBoxes = list()

        self.__update()

    def __remove_entry(self, layout):
        index = self.entries.index(layout)
        self.entries.pop(index)
        self.comboBoxesLeft.pop(index)
        self.comboBoxesRight.pop(index)
        self.checkBoxes.pop(index)

        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        layout.deleteLater()

        self.__update()

    def __update_lists(self):
        self.objectsOnLeft = list()
        self.objectsOnRight = list()

        i = True
        for boxList in self.comboBoxesLeft, self.comboBoxesRight:
            for comboBox in boxList:
                if i:
                    self.objectsOnLeft.append(comboBox.currentText())
                else:
                    self.objectsOnRight.append(comboBox.currentText())
            i = False

    def __update_info(self):
        noMatch = list()
        matchedWithSelf = list()
        multipleMatch = list()

        # no match
        for obj in self.objects:
            if obj not in self.objectsOnLeft and obj not in self.objectsOnRight:
                noMatch.append(obj)

        # matched with self
        for i in range(len(self.objectsOnLeft)):
            if self.objectsOnLeft[i] == self.objectsOnRight[i]:
                matchedWithSelf.append(self.objectsOnLeft[i])

        # multiple matches

        # this is a bit convoluted
        # first I gather the objects that are listed more than once in both lists combined
        seen = list()
        for objList in self.objectsOnLeft, self.objectsOnRight:
            for obj in objList:
                if obj in seen:
                    multipleMatch.append(obj)
                else:
                    seen.append(obj)

        # then I count how many times each object is listed and put it in a dictionary {object : count}
        # note that the count is actually one less than the actual occurrence, since I lose one object to the seen list
        mulCount = {obj: multipleMatch.count(obj) for obj in multipleMatch}

        # count how many times each object is listed in the matchedWithSelf list and put that in a matching dictionary
        selfCount = {obj: matchedWithSelf.count(obj) for obj in matchedWithSelf}

        # clearing list
        multipleMatch = list()

        # the two dictionaries are then compared and if objects occur more often than they are matched with self or if
        # they are not matched at all they are appended to the multipleMatch list
        for obj in mulCount:
            if obj in selfCount:
                if mulCount[obj] - selfCount[obj] > 0:
                    multipleMatch.append(obj)
            else:
                multipleMatch.append(obj)

        matchedWithSelf = utilities.remove_duplicates_from_list(matchedWithSelf)

        info = ''

        info += 'Not matched:\n\n'
        for obj in noMatch:
            if obj != '':
                info += '   %s%s' % (obj, '\n')

        info += '\nMatched with self:\n\n'
        for obj in matchedWithSelf:
            if obj != '':
                info += '   %s%s' % (obj, '\n')

        info += '\nMatched more than once:\n\n'
        for obj in multipleMatch:
            if obj != '':
                info += '   %s%s' % (obj, '\n')

        self.infoBox.setPlainText(info)

    def __update_entries(self):
        for boxList in self.comboBoxesLeft, self.comboBoxesRight:
            for comboBox in boxList:
                tekst = comboBox.currentText()

                comboBox.clear()

                for obj in sorted(self.objects):
                    comboBox.addItem(obj)

                comboBox.setCurrentIndex(comboBox.findText(tekst))

    def __update(self):
        self.__update_entries()
        self.__update_lists()
        self.__update_info()

    def __auto_match_objects(self):
        wordList = sorted(list(self.objects))

        matches = dict()

        while len(wordList) > 0:
            try:
                match = difflib.get_close_matches(wordList[0], wordList[1:], 1, 0.6)[0]
                matches[wordList[0]] = match
                wordList.pop(0)
                wordList.pop(wordList.index(match))
            except IndexError:
                matches[wordList[0]] = wordList[0]
                wordList.pop(0)

        return matches

    def __auto_match(self):

        self.__remove_all_entries()

        matches = self.__auto_match_objects()

        i = 0
        for match in matches:
            self.__add_entry()
            self.comboBoxesLeft[i].setCurrentIndex(self.comboBoxesLeft[i].findText(match))
            self.comboBoxesRight[i].setCurrentIndex(self.comboBoxesLeft[i].findText(matches[match]))
            i += 1

        self.__update()

    def __add_selected(self, *args):
        l = cmds.ls(selection=True)
        l = [str(x) for x in l]
        self.objects.extend(l)

        self.__update()

    def __get_hierarchy(self):
        hierarchy = list()

        object = self.objects[0]

        # traverses the hierarchy until top parent is found - until the object doesn't have a parent
        parent = cmds.listRelatives(object, allParents=True, fullPath=True)
        while parent:
            parent = cmds.listRelatives(object, allParents=True, fullPath=True)
            if parent:
                object = parent

        # lists all children and appends to hierarchy if part of character
        for obj in cmds.ls(object, dag=True, allPaths=True):
            if obj in self.objects:
                hierarchy.append(obj)

        return hierarchy

    def __get_top_hierarchy(self):
        # finding parents of modules in the rig
        tophierarcy = list()

        # checks if the parent hierarchy of each selected object is one of the selected objects
        # adds to tophierarchy list if not
        for object in self.objects:
            hasParent = False
            currentObject = object
            parent = cmds.listRelatives(object, allParents=True, fullPath=True)
            while parent:
                parent = cmds.listRelatives(object, allParents=True, fullPath=True)
                if parent:
                    if str(parent[0]).split('|')[-1] in self.objects:
                        hasParent = True
                    object = parent

            if not hasParent:
                tophierarcy.append(currentObject)

        return tophierarcy

    def __get_transformation(self):
        data = dict()

        for obj in self.objects:
            pyObj = pm.PyNode(obj)
            quat = pyObj.getRotation('world').asQuaternion()
            vec = pyObj.getTranslation('world')
            data[obj] = ((quat.x, quat.y, quat.z, quat.w), (vec.x, vec.y, vec.z))

        return data

    def __get_character_orientation(self):
        str = ''

        axis = ['x', 'y', 'z']
        boxes = [[self.forwardXCheckBox, self.forwardYCheckBox, self.forwardZCheckBox],
                 [self.upXCheckBox, self.upYCheckBox, self.upZCheckBox]]

        for i in range(2):
            for j in range(3):
                if boxes[i][j].isChecked():
                    str += axis[j]

        if 'y' in str:
            if 'z' in str:
                return 'yz'
            else:
                return 'xy'
        else:
            return 'xz'

    def __get_matches(self):
        listOne = list()
        listTwo = list()

        i = True
        for boxList in self.comboBoxesLeft, self.comboBoxesRight:
            for comboBox in boxList:
                if i:
                    listOne.append(comboBox.currentText())
                else:
                    listTwo.append(comboBox.currentText())
            i = False

        listOne.extend(listTwo)
        listTwo.extend(listOne)

        data = {listOne[i]: listTwo[i] for i in range(len(listOne))}

        return data

    def __get_file_dir(self):
        chr = str(QtGui.QInputDialog.getText(self, '', 'Name:')[0])

        return os.path.join(self._dir, chr + '.json')

    def __export(self, *args):
        matchData = self.__get_matches()
        hierarchyData = self.__get_hierarchy()
        topHiearchyData = self.__get_top_hierarchy()
        transformationData = self.__get_transformation()
        characterOrientationData = self.__get_character_orientation()
        chrDir = self.__get_file_dir()

        data = {'matches': matchData,
                'transformation': transformationData,
                'hierarchy': hierarchyData,
                'topHierarchy': topHiearchyData,
                'chrOrientation': characterOrientationData}

        with open(chrDir, 'w') as chrFile:
            json.dump(data, chrFile)

        global MirrorToolWin
        try:
            MirrorToolWin.__load_characters()
        except:
            pass
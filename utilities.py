import maya.OpenMayaUI as omui
import pymel.core as pm
from Qt import QtWidgets
try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance


def get_maya_main_window():
    # gets current instance of maya's ui interface

    mainWindowPointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPointer), QtWidgets.QWidget)


def get_namespaces():
    # gets the namespaces from the scene
    # returns list of strings

    names = ['None']

    for name in pm.namespaceInfo(listOnlyNamespaces=True, recurse=True):
        if name not in ['UI', 'shared']:
            names.append(name)

    return names


def get_scene_range():
    # gets the current frame range from the scene
    # returns tuple of floats

    return pm.playbackOptions(query=True, minTime=True), pm.playbackOptions(query=True, maxTime=True)


def browse_dir(path):
    # opens browser window and returns the selected file
    # returns string

    if path is not None:
        fileName = QtWidgets.QFileDialog.getOpenFileName(caption='open character file', dir=path)
    else:
        fileName = QtWidgets.QFileDialog.getOpenFileName(caption='open character file')

    return fileName[0]


def create_mirror_plane():
    # returns transform node

    plane = pm.polyPlane(name='MirrorToolPlane',
                          axis=(1.0, 0.0, 0.0),
                          subdivisionsHeight=1,
                          subdivisionsWidth=1,
                          height=100,
                          width=100)[0]

    return plane


def create_mirror_plane_material():
    # returns material and shadergroup

    mtl = pm.shadingNode('lambert', asShader=True, name='MirrorToolPlane_Mtl')

    sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='MirrorToolPlane_Sg')

    pm.connectAttr((mtl + '.outColor'), (sg + '.surfaceShader'), force=1)

    pm.setAttr(mtl + ".color", 0, 1, 1)
    pm.setAttr(mtl + ".transparency", 0.5, 0.5, 0.5)

    return mtl, sg


def create_mirror():
    # creates the mirror plane and assigns half transparent blue material
    # returns planes transform node, material and shader group

    plane = create_mirror_plane()
    mtl, sg = create_mirror_plane_material()

    pm.sets(sg, edit=True, forceElement=plane)

    return plane, mtl, sg


def delete_mirror(mirror, mtl, sg):
    # deletes the planes transform node, material and shader group

    pm.delete(mirror)
    pm.delete(mtl)
    pm.delete(sg)


def remove_duplicates_from_list(listIn):
    # what the name says

    listOut = list()
    for i in listIn:
        if i not in listOut:
            listOut.append(i)
    return listOut
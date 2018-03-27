import pymel.core as pm
import vectorfunctions as vf


def double_no_twist_quaternion_from_plane(plane):
    # get plane direction as rotation
    # we need the planes rotation in addition to the planes rotation relative to the object(s) we're mirroring
    # so double quat
    # returns Quaternion

    vector = pm.datatypes.Vector([1.0, 0.0, 0.0])
    vector = vector.rotateBy(plane.getRotation('world'))

    quat = pm.datatypes.Quaternion(vf.shortest_arc_quaternion([1.0, 0.0, 0.0], vector))
    quat = quat * quat

    return quat


def mirror_translation(vector, senderTranslation, receiverTranslation, chrOrientation, plane):
    # removes sender translation
    # negates either x, y or z value of vector depending on chrOrientation
    # adds receiver translation
    # rotated vector 180 around appropriate axis if plane != chrOrientation
    # returns Vector

    vector = pm.datatypes.Vector(vector) - pm.datatypes.Vector(senderTranslation)

    if chrOrientation == 'yz':
        vector.x = -vector.x
        vector = vector + pm.datatypes.Vector(receiverTranslation)
        if plane == 'xz':
            vector = vector.rotateBy(pm.datatypes.Quaternion([0.0, 0.0, 1.0, 0.0]))
        elif plane == 'xy':
            vector = vector.rotateBy(pm.datatypes.Quaternion([0.0, 1.0, 0.0, 0.0]))

    elif chrOrientation == 'xz':
        vector.y = -vector.y
        vector = vector + pm.datatypes.Vector(receiverTranslation)
        if plane == 'yz':
            vector = vector.rotateBy(pm.datatypes.Quaternion([0.0, 0.0, 1.0, 0.0]))
        elif plane == 'xy':
            vector = vector.rotateBy(pm.datatypes.Quaternion([1.0, 0.0, 0.0, 0.0]))

    else:
        vector.z = -vector.z
        vector = vector + pm.datatypes.Vector(receiverTranslation)
        if plane == 'yz':
            vector = vector.rotateBy(pm.datatypes.Quaternion([0.0, 1.0, 0.0, 0.0]))
        elif plane == 'xz':
            vector = vector.rotateBy(pm.datatypes.Quaternion([1.0, 0.0, 0.0, 0.0]))

    return vector


def mirror_translation_relative_to_plane(object, senderTranslation, receiverTranslation, chrOrientation, planeVector, planeQuat):
    # gets translation from object as vector
    # subtracts planeVector to get translation relative to plane
    # mirror vector over plane defined by character orientation
    # rotate vector by plane rotation
    # add planeVector to vector
    # returns Vector

    objectVector = object.getTranslation('world')
    objectVector = pm.datatypes.Vector(objectVector)
    objectVector = objectVector - planeVector
    objectVector = mirror_translation(objectVector, senderTranslation, receiverTranslation, chrOrientation, chrOrientation)
    objectVector = objectVector.rotateBy(planeQuat)
    objectVector = objectVector + planeVector

    return objectVector


def mirror_rotation(object, tophierarchy, senderOrientation, receiverOrientation, chrOrientation, plane, planeQuat=None):
    # gets rotation from object as quaternion
    # changes the basis of the rotation to world space
    # negates w and either x, y or z value of object's rotation
    # changes the basis of the rotation to the receiver objects local space
    # returns Quaternion

    # Quaternion and MQuaternion apparently multiply differently
    # so I have to create a new Quaternion instance from what I get from getRotation()


    quat = object.getRotation().asQuaternion()
    quat = pm.datatypes.Quaternion(quat)

    quat = senderOrientation.inverse() * quat * senderOrientation

    quat.w = -quat.w

    # https://www.youtube.com/watch?v=poz6W0znOfk
    if chrOrientation == 'yz':
        quat.x = -quat.x
        if plane == 'yz':
            if object in tophierarchy:
                if planeQuat:
                    quat = quat * planeQuat
            quat = receiverOrientation * quat * receiverOrientation.inverse()

        elif plane == 'xz':
            if object in tophierarchy:
                quat = quat * pm.datatypes.Quaternion([0.0, 0.0, 1.0, 0.0])
            quat = receiverOrientation * quat * receiverOrientation.inverse()

        else:
            if object in tophierarchy:
                quat = quat * pm.datatypes.Quaternion([0.0, 1.0, 0.0, 0.0])
            quat = receiverOrientation * quat * receiverOrientation.inverse()

    elif chrOrientation == 'xz':
        quat.y = -quat.y
        if plane == 'yz':
            if object in tophierarchy:
                quat = quat * pm.datatypes.Quaternion([0.0, 0.0, 1.0, 0.0])
            quat = receiverOrientation * quat * receiverOrientation.inverse()

        elif plane == 'xz':
            if object in tophierarchy:
                if planeQuat:
                    quat = quat * planeQuat
            quat = receiverOrientation * quat * receiverOrientation.inverse()

        else:
            if object in tophierarchy:
                quat = quat * pm.datatypes.Quaternion([1.0, 0.0, 0.0, 0.0])
            quat = receiverOrientation * quat * receiverOrientation.inverse()

    else:
        quat.z = -quat.z
        if plane == 'yz':
            if object in tophierarchy:
                quat = quat * pm.datatypes.Quaternion([0.0, 1.0, 0.0, 0.0])
            quat = receiverOrientation * quat * receiverOrientation.inverse()

        elif plane == 'xz':
            if object in tophierarchy:
                quat = quat * pm.datatypes.Quaternion([1.0, 0.0, 0.0, 0.0])
            quat = receiverOrientation * quat * receiverOrientation.inverse()

        else:
            if object in tophierarchy:
                if planeQuat:
                    quat = quat * planeQuat
            quat = receiverOrientation * quat * receiverOrientation.inverse()

    return quat


def get_user_defined_attributes(object):
    # gets keyable user defined attributes visible in the objects channelbox
    # returns list of lists

    obj = pm.PyNode(object)

    allAttrs = obj.listAttr(userDefined=True)

    attrs = list()
    for attr in allAttrs:
        if pm.getAttr(attr, keyable=True) is True and pm.getAttr(attr, lock=True) is False:
            attrs.append([attr.split('.')[-1], pm.getAttr(attr)])

    return attrs


def calculate_mirror_transformation(object, tophierarchy, chrOrientation, senderOrientation, receiverOrientation, senderTranslation, receiverTranslation, plane):
    # gets rotation and translation from object
    # mirrors over either world yz, xz, xy plane or an arbitrary plane in the scene
    # returns [Quaternion, Vector3]

    # plane can be string 'yz', 'xz' or 'xy' or a PyNode

    if isinstance(plane, pm.PyNode):
        planeQuat = double_no_twist_quaternion_from_plane(plane)
        planeVector = plane.getTranslation('world')

        rot = mirror_rotation(object, tophierarchy, senderOrientation, receiverOrientation, chrOrientation, chrOrientation, planeQuat)
        trans = mirror_translation_relative_to_plane(object, senderTranslation, receiverTranslation, chrOrientation, planeVector, planeQuat)

    else:
        rot = mirror_rotation(object, tophierarchy, senderOrientation, receiverOrientation, chrOrientation, plane)
        trans = mirror_translation(object.getTranslation('world'), senderTranslation, receiverTranslation, chrOrientation, plane)

    userAttrs = get_user_defined_attributes(object)

    return [rot, trans, userAttrs]


def get_objects_mirror_transformations(chrDict, namespace, frameRange, plane):
    # gets the mirrored transformation of all objects specified in objectDict in the frames specified in frameRange
    # returns list of lists

    transformList = list()
    hierarchy = chrDict['hierarchy']

    for obj in hierarchy:
        # first value in tList is the name of the object the transformations should be applied to

        tList = ['%s%s' % (namespace, obj)]
        transformList.append(tList)

    for i in range(frameRange[0], frameRange[1] + 1):

        pm.currentTime(i)

        j = 0
        for obj in hierarchy:
            tList = transformList[j]
            pyObj = pm.PyNode('%s%s' % (namespace, chrDict['matches'][obj]))

            receiverTranslation = chrDict['transformation'][obj][1]
            senderTranslation = chrDict['transformation'][chrDict['matches'][obj]][1]
            chrOrientation = chrDict['chrOrientation']
            receiverOrientation = pm.datatypes.Quaternion(chrDict['transformation'][obj][0])
            senderOrientation = pm.datatypes.Quaternion(chrDict['transformation'][chrDict['matches'][obj]][0])
            tophierarchy = chrDict['topHierarchy']

            tList.append(calculate_mirror_transformation(pyObj, tophierarchy, chrOrientation, senderOrientation, receiverOrientation, senderTranslation, receiverTranslation, plane))

            j += 1


    return transformList


def set_transformations(transformList, frameRange):
    # transforms each object as specified and sets a key on each frame in frameRange

    pm.undoInfo(openChunk=True)

    j = 1

    for i in range(frameRange[0], frameRange[1] + 1):
        pm.currentTime(i)

        for tList in transformList:
            obj = pm.PyNode(tList[0])

            obj.setRotation(tList[j][0])
            obj.setTranslation(tList[j][1], 'world')

            for attr in tList[j][2]:
                try:
                    pm.setAttr('%s.%s' % (tList[0], attr[0]), attr[1])
                except AttributeError:
                    continue

            pm.setKeyframe(obj)

        j += 1

    pm.undoInfo(closeChunk=True)
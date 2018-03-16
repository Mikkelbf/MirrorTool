import math


def cross(vA, vB):
    # takes two three dimensional vectors as arguments
    # orthogonal vector to the plane of the two vectors
    # returns three dimensional vector

    cross = [vA[1] * vB[2] - vA[2] * vB[1],
             vA[2] * vB[0] - vA[0] * vB[2],
             vA[0] * vB[1] - vA[1] * vB[0]]

    return cross


def dot(vA, vB):
    # takes two vectors as arguments
    # the sum of the product of each value of each vector
    # returns float

    dot = sum(float(vA[i]) * float(vB[i]) for i in range(len(vA)))
    return dot


def magnitude(v):
    # takes vector as argument
    # pythagorean theorem
    # returns float

    mag = math.sqrt(sum(float(v[i]) * float(v[i]) for i in range(len(v))))
    return mag


def normalize(v):
    # takes vector as argument
    # each value of vector divided by the vector's magnitude
    # returns vector

    mag = magnitude(v)
    v = [val / mag for val in v]

    return v


def orthogonal(v):
    # takes three dimensional vector as argument
    # finds the basis vector that is the most orthogonal to the vector
    # i.e. the basis vector in the direction of the vectors lowest value
    # returns three dimensional vector

    if v[0] < v[1]:
        if v[0] < v[2]:
            other = [1,0,0]
    elif v[1] < v[2]:
        other = [0,1,0]
    else:
        other = [0,0,1]

    # cross product of the vector and the most orthogonal basis vector
    return cross(v, other)


def shortest_arc_quaternion(vA, vB):
    # takes two three dimensional vectors as argument
    # returns quaternion in the form [x, y, z, w]

    # magnitude = math.sqrt(magnitude(vectorA)**2 * magnitude(vectorB)**2)
    # w   = dot(vectorA, vectorB) + magnitude
    # xyz = cross(vectorA, vectorB)

    vA = normalize(vA)
    vB = normalize(vB)

    cosine = dot(vA, vB) + 1.0

    if cosine > 0.00001:
        xyz = cross(vA, vB)
        return normalize([xyz[0], xyz[1], xyz[2], cosine])

    # dot < -0.99999
    # pointing in the opposite direction
    xyz = normalize((orthogonal(vA)))
    return [xyz[0], xyz[1], xyz[2], 0.0]
import math



def round_int(val):
    return int(round(val))



def fastMax(a, b):
    if(a > b):
        return a
    else:
        return b


def fastMin(a, b):
    if(a < b):
        return a
    else:
        return b






def getFullHumanBoudingBox(keypoints, leftboudind, rightbounding, threshold=0.2):
    xs = []
    ys = []

    for keypoint in keypoints:
        if keypoint[2] > threshold:
            x = keypoint[0]
            y = keypoint[1]
            points = [round_int(x), round_int(y), 2]
            xs.append(points[0])
            ys.append(points[1])

    if leftboudind[0] is not 0 and leftboudind[1] is not 0:
        xs.append(leftboudind[0])
        ys.append(leftboudind[1])
        xs.append(leftboudind[2])
        ys.append(leftboudind[3])



    if rightbounding[0] is not 0 and rightbounding[1] is not 0:
        xs.append(rightbounding[0])
        ys.append(rightbounding[1])
        xs.append(rightbounding[2])
        ys.append(rightbounding[3])


    head = getFaceFromPoseKeypoints(keypoints, 15, 16, 17, 18, 0.1)

    if(head[0] != 0 and head[1] != 0 and head[2] != 0 and head[3] != 0):
        xs.append(head[0])
        ys.append(head[1])
        xs.append(head[2])
        ys.append(head[3])


    xmin = int(min(xs))
    ymin = int(min(ys))
    xmax = int(max(xs))
    ymax = int(max(ys))

    return xmin, ymin, xmax, ymax





def getDistance(keypoints,  elementA, elementB):
    pixelX = keypoints[elementA][0] - keypoints[elementB][0]
    pixelY = keypoints[elementA][1] - keypoints[elementB][1]
    return math.sqrt(pixelX*pixelX+pixelY*pixelY)


def getFaceFromPoseKeypoints(keypoints, REye, LEye, REar, LEar, threshold=0.2):
    """
    :param keypoints:
    :param Nose:
    :param Neck:
    :param threshold:
    :return:
    """
    REarkeypoints = keypoints[REar]
    LEarkeypoints = keypoints[LEar]
    REyekeypoints = keypoints[REye]
    LEyekeypoints = keypoints[LEye]

    if(REarkeypoints[2] > threshold and LEarkeypoints[2] > threshold):
        xmin = (REarkeypoints[0] + LEarkeypoints[0]) / 2
        ymin = (REarkeypoints[1] + LEarkeypoints[1]) / 2
        xmax = xmin
        ymax = ymin
        width = round(2.1 * getDistance(keypoints, REar, LEar));
        height = width

        xmin -= width / float(2)
        ymin -= height / float(2)
        xmax += width / float(2)
        ymax += height / float(2)

        return round_int(xmin),  round_int(ymin), round_int(xmax), round_int(ymax)


    elif REarkeypoints[2] > threshold and LEyekeypoints[2] > threshold:
        xmin = (REarkeypoints[0] + LEyekeypoints[0]) / 2
        ymin = (REarkeypoints[1] + LEyekeypoints[1]) / 2
        xmax = xmin
        ymax = ymin
        width = round(2.1 * getDistance(keypoints, REar, LEye));
        height = width

        xmin -= width / float(2)
        ymin -= height / float(2)
        xmax += width / float(2)
        ymax += height / float(2)

        return round_int(xmin),  round_int(ymin), round_int(xmax), round_int(ymax)

    elif LEarkeypoints[2] > threshold and  REyekeypoints[2] > threshold:
        xmin = (LEarkeypoints[0] + REyekeypoints[0]) / 2
        ymin = (LEarkeypoints[1] + REyekeypoints[1]) / 2
        xmax = xmin
        ymax = ymin
        width = round(2.1 * getDistance(keypoints, LEar, REye));
        height = width

        xmin -= width / float(2)
        ymin -= height / float(2)
        xmax += width / float(2)
        ymax += height / float(2)

        return round_int(xmin),  round_int(ymin), round_int(xmax), round_int(ymax)

    elif LEarkeypoints[2] > threshold and  LEyekeypoints[2] > threshold:
        xmin = (LEarkeypoints[0] + LEyekeypoints[0]) / 2
        ymin = (LEarkeypoints[1] + LEyekeypoints[1]) / 2
        xmax = xmin
        ymax = ymin
        width = round(6 * getDistance(keypoints, LEar, LEye));
        height = width

        xmin -= width / float(2)
        ymin -= height / float(2)
        xmax += width / float(2)
        ymax += height / float(2)

        return round_int(xmin),  round_int(ymin), round_int(xmax), round_int(ymax)

    elif REarkeypoints[2] > threshold and REyekeypoints[2] > threshold:
        xmin = (REarkeypoints[0] + REyekeypoints[0]) / 2
        ymin = (REarkeypoints[1] + REyekeypoints[1]) / 2
        xmax = xmin
        ymax = ymin
        width = round(6 * getDistance(keypoints, REar, REye));
        height = width

        xmin -= width / float(2)
        ymin -= height / float(2)
        xmax += width / float(2)
        ymax += height / float(2)

        return round_int(xmin),  round_int(ymin), round_int(xmax), round_int(ymax)

    else:
        return 0,0,0,0










def getHandFromPoseIndexes(keyspoints, wrist, elbow, shoulder, threshold=0.2):
    """
    :param keyspoints:
    :param wrist:
    :param elbow:
    :param shoulder:
    :param threshold:
    :return:
    """
    wristkeypoints = keyspoints[wrist]
    elbowkeypoints = keyspoints[elbow]
    shouledkeypoints = keyspoints[shoulder]

    if(wristkeypoints[2] > threshold and elbowkeypoints[2] > threshold and shouledkeypoints[2] > threshold):


        ratioWristElbow = 0.50

        xmin = wristkeypoints[0] + ratioWristElbow * (wristkeypoints[0] - elbowkeypoints[0])
        ymin = wristkeypoints[1] + ratioWristElbow * (wristkeypoints[1] - elbowkeypoints[1])
        xmax = xmin
        ymax = ymin

        distanceWristElbow = round(getDistance(keyspoints, wrist, elbow))
        distanceElbowShoulder = round(getDistance(keyspoints, elbow, shoulder))


        width = round(float(1.2) * fastMax(distanceWristElbow, float(0.9) * distanceElbowShoulder))
        height = width;

        xmin -= width / float(2)
        ymin -= height / float(2)
        xmax += width / float(2)
        ymax += height / float(2)

        return round_int(xmin),  round_int(ymin), round_int(xmax), round_int(ymax)
    else:
        return 0, 0, 0, 0

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:28:21 2017
@author: Hriddhi Dey

This module contains the ApplyMakeup class.
"""
from scipy import interpolate
from pylab import *
import itertools
import scipy.interpolate
import cv2
import numpy as np
import os.path
import sys
from urllib.request import urlretrieve
import dlib
import numpy
from skimage import color

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
CASC_PATH = "haarcascade_frontalface_default.xml"
intensivity = 0.5

class DetectLandmarks(object):
    """
    This is the class responsible for landmark detection on a human face.

    Functions available for use:
        1. get_face_data: Returns all detected landmarks for a face.
        2. get_lips: Returns points of lips for a face.
        3. get_upper_eyelids: Returns points of eyeliner for a face.
    """

    IMAGE_DATA = 'IMAGE_DATA'
    FILE_READ = 'FILE_READ'
    NETWORK_BYTE_STREAM = 'NETWORK_BYTE_STREAM'



    def __init__(self):
        """ Initiator for DetectLandmarks class.
        Downloads the predictor file if not available.
        Raises:
            `Exception`, if download of predictor fails.
        """
        if not os.path.isfile(PREDICTOR_PATH):
            try:
                print ('Predictor not found. Downloading...this may take a while...')
                url = 'https://github.com/hriddhidey/visage/blob/master/visage/shape_predictor_68_face_landmarks.dat?raw=true'
                def dl_progress(count, block_size, total_size):
                    """ Show download progress bar. """
                    percent = int(count*block_size*100/total_size)
                    sys.stdout.write("\r" + 'Progress:' + "...%d%%" % percent)
                    sys.stdout.flush()
                urlretrieve(
                    url,
                    PREDICTOR_PATH,
                    reporthook=dl_progress
                )
                print ('Predictor downloaded.')
            except IOError:
                print ('Download failed. Try again with reliable network connection.')
                raise IOError
        self.predictor = dlib.shape_predictor(PREDICTOR_PATH)
        self.cascade = cv2.CascadeClassifier(CASC_PATH)
        self.detector = dlib.get_frontal_face_detector()



    def __get_landmarks(self, image):
        """ Extract the landmarks from a given image. 
        Returns `None` if no landmarks found.
        """
        try:
            rects = self.detector(image, 1)
            size = len(rects)
            if size == 0:
                return None, None
            return numpy.matrix([[p.x, p.y] for p in self.predictor(image, rects[0]).parts()])
        except Exception:
            return None



    def get_face_data(self, image_file, flag):
        """
        Returns all facial landmarks in a given image.
        ______________________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network request.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of face.

        Error:
            Returns `None` if face not found in image.

        """
        image = 0
        if flag == self.FILE_READ:
            image = cv2.imread(image_file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif flag == self.NETWORK_BYTE_STREAM:
            image = cv2.imdecode(
                numpy.fromstring(image_file.read(), numpy.uint8), cv2.IMREAD_UNCHANGED
            )
        elif flag == self.IMAGE_DATA or flag is None:
            image = image_file
        landmarks = self.__get_landmarks(image)
        if landmarks[0] is None or landmarks[1] is None:
            return None
            
        return landmarks



    def get_lips(self, image_file, list_points, flag=None):
        """
        Returns points for lips in given image.
        _______________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network reqeust.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of lips.

        Error:
            Returns `None` if face not found in image.

        """
        landmarks = list_points
        if landmarks is None:
            return None
        lips = ""
        for point in landmarks[48:]:
            lips += str(point).replace('[', '').replace(']', '') + '\n'
        return lips

    def get_blushs_right(self, image_file, list_points, flag=None):
        """
        Returns points for blushs in given image.
        _______________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network reqeust.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of blushs.

        Error:
            Returns `None` if face not found in image.

        """
        
        landmarks = list_points
        if landmarks is None:
            return None
        blushs = []
        for point in landmarks[48]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        for point in landmarks[0:3]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        for point in landmarks[31]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        for point in landmarks[48]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        
        xc = 0
        yc = 0
        
        for point in blushs:
            xc += point[0]
            yc += point[1]
        
        xc = xc / len(blushs)
        yc = yc / len(blushs)
        
        for point in blushs:
            point[0] = (xc + point[0]) * 0.5
            point[1] = (yc + point[1]) * 0.5
        
        blushs = np.asmatrix(blushs)
        
        return np.asarray(blushs[0:6, 1]).reshape(-1), np.asarray(blushs[0:6, 0]).reshape(-1)

    def get_blushs_left(self, image_file, list_points, flag=None):
        """
        Returns points for blushs in given image.
        _______________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network reqeust.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of blushs.

        Error:
            Returns `None` if face not found in image.

        """
        landmarks = list_points
        if landmarks is None:
            return None
        blushs = []
        for point in landmarks[54]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        for point in landmarks[13:16]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        for point in landmarks[35]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
        for point in landmarks[54]:
            blushs = [*blushs, np.asarray(point).reshape(-1)]
            
        xc = 0
        yc = 0
        
        for point in blushs:
            xc += point[0]
            yc += point[1]
        
        xc = xc / len(blushs)
        yc = yc / len(blushs)
        
        for point in blushs:
            point[0] = (xc + point[0]) * 0.5
            point[1] = (yc + point[1]) * 0.5
              
        blushs = np.asmatrix(blushs)
            
        return np.asarray(blushs[0:6, 1]).reshape(-1), np.asarray(blushs[0:6, 0]).reshape(-1)
        
    def get_eyeshadows_right(self, image_file, list_points, flag=None):
        """
        Returns points for eyeshadows in given image.
        _______________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network reqeust.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of eyeshadows.

        Error:
            Returns `None` if face not found in image.

        """
        
        landmarks = list_points
        if landmarks is None:
            return None
        eyeshadows = []
        for point in landmarks[17:21]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[39]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[38]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[37]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[36]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[17]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        

        eyeshadows = np.asmatrix(eyeshadows)
        
        return np.asarray(eyeshadows[0:9, 1]).reshape(-1), np.asarray(eyeshadows[0:9, 0]).reshape(-1)

    def get_eyeshadows_left(self, image_file, list_points, flag=None):
        """
        Returns points for eyeshadows in given image.
        _______________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network reqeust.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of eyeshadows.

        Error:
            Returns `None` if face not found in image.

        """
        landmarks = list_points
        if landmarks is None:
            return None
        eyeshadows = []
        for point in landmarks[26]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[25]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[24]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[23]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[22]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[42:45]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]
        for point in landmarks[26]:
            eyeshadows = [*eyeshadows, np.asarray(point).reshape(-1)]


        eyeshadows = np.asmatrix(eyeshadows)
            
        return np.asarray(eyeshadows[0:9, 1]).reshape(-1), np.asarray(eyeshadows[0:9, 0]).reshape(-1)
        
    def get_upper_eyelids(self, image_file, list_points, flag=None):
        """
        Returns points for upper eyelids in given image.
        ________________________________________________
        Args:
            1. `image_file`:
                Either of three options:\n
                    a. (int) Image data after being read with cv2.imread()\n
                    b. File path of locally stored image file.\n
                    c. Byte stream being received over multipart network reqeust.\n\n
            2. `flag`:
                Used to denote the type of image_file parameter being passed.
                Possible values are IMG_DATA, FILE_READ, NETWORK_BYTE_STREAM respectively.
                By default its value is IMAGE_DATA, and assumes imread() image is passed.

        Returns:
            String with list of detected points of lips.

        Error:
            Returns `None` if face not found in image.

        """
        landmarks = list_points
        if landmarks is None:
            return None
        liner = ""
        for point in landmarks[36:40]:
            liner += str(point).replace('[', '').replace(']', '') + '\n'
        liner += '\n'
        for point in landmarks[42:46]:
            liner += str(point).replace('[', '').replace(']', '') + '\n'
        return liner


class ApplyMakeup(DetectLandmarks):
    """
    Class that handles application of color, and performs blending on image.

    Functions available for use:
        1. apply_lipstick: Applies lipstick on passed image of face.
        2. apply_liner: Applies black eyeliner on passed image of face.
    """

    def __init__(self):
        """ Initiator method for class """
        DetectLandmarks.__init__(self)
        self.red_l = 0
        self.green_l = 0
        self.blue_l = 0
        
        self.red_e = 0
        self.green_e = 0
        self.blue_e = 0
        
        self.red_b = 0
        self.green_b = 0
        self.blue_b = 0
        
        self.debug = 0
        self.image = 0
        self.width = 0
        self.height = 0
        self.im_copy = 0
        self.lip_x = []
        self.lip_y = []


    def __read_image(self, filename):
        """ Read image from path forwarded """
        self.image = cv2.imread(filename)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.im_copy = self.image.copy()
        self.height, self.width = self.image.shape[:2]
        self.debug = 0


    def __draw_curve(self, points):
        """ Draws a curve alone the given points by creating an interpolated path. """
        x_pts = []
        y_pts = []
        curvex = []
        curvey = []
        self.debug += 1
        for point in points:
            x_pts.append(point[0])
            y_pts.append(point[1])
        curve = scipy.interpolate.interp1d(x_pts, y_pts, 'cubic')
        if self.debug == 1 or self.debug == 2:
            for i in np.arange(x_pts[0], x_pts[len(x_pts) - 1] + 1, 1):
                curvex.append(i)
                curvey.append(int(curve(i)))
        else:
            for i in np.arange(x_pts[len(x_pts) - 1] + 1, x_pts[0], 1):
                curvex.append(i)
                curvey.append(int(curve(i)))
        return curvex, curvey


    def __fill_lip_lines(self, outer, inner):
        """ Fills the outlines of a lip with colour. """
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        count = len(inner[0]) - 1
        last_inner = [inner[0][count], inner[1][count]]
        for o_point, i_point in itertools.zip_longest(
                outer_curve, inner_curve, fillvalue=last_inner
            ):
            line = scipy.interpolate.interp1d(
                [o_point[0], i_point[0]], [o_point[1], i_point[1]], 'linear')
            xpoints = list(np.arange(o_point[0], i_point[0], 1))
            self.lip_x.extend(xpoints)
            self.lip_y.extend([int(point) for point in line(xpoints)])
        return


    def __fill_lip_solid(self, outer, inner):
        """ Fills solid colour inside two outlines. """
        inner[0].reverse()
        inner[1].reverse()
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        points = []
        for point in outer_curve:
            points.append(np.array(point, dtype=np.int32))
        for point in inner_curve:
            points.append(np.array(point, dtype=np.int32))
        points = np.array(points, dtype=np.int32)
        self.red_l = int(self.red_l)
        self.green_l = int(self.green_l)
        self.blue_l = int(self.blue_l)
        cv2.fillPoly(self.image, [points], (self.red_l, self.green_l, self.blue_l))


    def __smoothen_color(self, outer, inner):
        """ Smoothens and blends colour applied between a set of outlines. """
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        x_points = []
        y_points = []
        for point in outer_curve:
            x_points.append(point[0])
            y_points.append(point[1])
        for point in inner_curve:
            x_points.append(point[0])
            y_points.append(point[1])
        img_base = np.zeros((self.height, self.width))
        cv2.fillConvexPoly(img_base, np.array(np.c_[x_points, y_points], dtype='int32'), 1)
        img_mask = cv2.GaussianBlur(img_base, (81, 81), 0) #51,51
        img_blur_3d = np.ndarray([self.height, self.width, 3], dtype='float')
        img_blur_3d[:, :, 0] = img_mask
        img_blur_3d[:, :, 1] = img_mask
        img_blur_3d[:, :, 2] = img_mask
        self.im_copy = (img_blur_3d * self.image * 0.7 + (1 - img_blur_3d * 0.7) * self.im_copy).astype('uint8')


    def __draw_liner(self, eye, kind):
        """ Draws eyeliner. """
        eye_x = []
        eye_y = []
        x_points = []
        y_points = []
        for point in eye:
            x_points.append(int(point.split()[0]))
            y_points.append(int(point.split()[1]))
        curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
        for point in np.arange(x_points[0], x_points[len(x_points) - 1] + 1, 1):
            eye_x.append(point)
            eye_y.append(int(curve(point)))
        if kind == 'left':
            y_points[0] -= 1
            y_points[1] -= 1
            y_points[2] -= 1
            x_points[0] -= 5
            x_points[1] -= 1
            x_points[2] -= 1
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
            count = 0
            for point in np.arange(x_points[len(x_points) - 1], x_points[0], -1):
                count += 1
                eye_x.append(point)
                if count < (len(x_points) / 2):
                    eye_y.append(int(curve(point)))
                elif count < (2 * len(x_points) / 3):
                    eye_y.append(int(curve(point)) - 1)
                elif count < (4 * len(x_points) / 5):
                    eye_y.append(int(curve(point)) - 2)
                else:
                    eye_y.append(int(curve(point)) - 3)
        elif kind == 'right':
            x_points[3] += 5
            x_points[2] += 1
            x_points[1] += 1
            y_points[3] -= 1
            y_points[2] -= 1
            y_points[1] -= 1
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
            count = 0
            for point in np.arange(x_points[len(x_points) - 1], x_points[0], -1):
                count += 1
                eye_x.append(point)
                if count < (len(x_points) / 2):
                    eye_y.append(int(curve(point)))
                elif count < (2 * len(x_points) / 3):
                    eye_y.append(int(curve(point)) - 1)
                elif count < (4 * len(x_points) / 5):
                    eye_y.append(int(curve(point)) - 2)
                elif count:
                    eye_y.append(int(curve(point)) - 3)
        curve = zip(eye_x, eye_y)
        points = []
        for point in curve:
            points.append(np.array(point, dtype=np.int32))
        points = np.array(points, dtype=np.int32)
        self.red_e = int(self.red_e)
        self.green_e = int(self.green_e)
        self.blue_e = int(self.blue_e)
        cv2.fillPoly(self.im_copy, [points], (self.red_e, self.green_e, self.blue_e))
        return


    def __add_color(self, intensity):
        """ Adds base colour to all points on lips, at mentioned intensity. """
        val = color.rgb2lab(
            (self.image[self.lip_y, self.lip_x] / 255.)
            .reshape(len(self.lip_y), 1, 3)
        ).reshape(len(self.lip_y), 3)
        l_val, a_val, b_val = np.mean(val[:, 0]), np.mean(val[:, 1]), np.mean(val[:, 2])
        l1_val, a1_val, b1_val = color.rgb2lab(
            np.array(
                (self.red_l / 255., self.green_l / 255., self.blue_l / 255.)
                ).reshape(1, 1, 3)
            ).reshape(3,)
        l_final, a_final, b_final = (l1_val - l_val) * \
            intensity, (a1_val - a_val) * \
            intensity, (b1_val - b_val) * intensity
        val[:, 0] = np.clip(val[:, 0] + l_final, 0, 100)
        val[:, 1] = np.clip(val[:, 1] + a_final, -127, 128)
        val[:, 2] = np.clip(val[:, 2] + b_final, -127, 128)
        self.image[self.lip_y, self.lip_x] = color.lab2rgb(val.reshape(
            len(self.lip_y), 1, 3)).reshape(len(self.lip_y), 3) * 255


    def __get_points_lips(self, lips_points):
        """ Get the points for the lips. """
        uol = []
        uil = []
        lol = []
        lil = []
        for i in range(0, 14, 2):
            uol.append([int(lips_points[i]), int(lips_points[i + 1])])
        for i in range(12, 24, 2):
            lol.append([int(lips_points[i]), int(lips_points[i + 1])])
        lol.append([int(lips_points[0]), int(lips_points[1])])
        for i in range(24, 34, 2):
            uil.append([int(lips_points[i]), int(lips_points[i + 1])])
        for i in range(32, 40, 2):
            lil.append([int(lips_points[i]), int(lips_points[i + 1])])
        lil.append([int(lips_points[24]), int(lips_points[25])])
        return uol, uil, lol, lil


    def __get_curves_lips(self, uol, uil, lol, lil):
        """ Get the outlines of the lips. """
        uol_curve = self.__draw_curve(uol)
        uil_curve = self.__draw_curve(uil)
        lol_curve = self.__draw_curve(lol)
        lil_curve = self.__draw_curve(lil)
        return uol_curve, uil_curve, lol_curve, lil_curve

    def __get_curves_blushs(self, uol, uil, lol, lil):
        """ Get the outlines of the lips. """
        uol_curve = self.__draw_curve(uol)
        uil_curve = self.__draw_curve(uil)
        lol_curve = self.__draw_curve(lol)
        lil_curve = self.__draw_curve(lil)
        return uol_curve, uil_curve, lol_curve, lil_curve

    def __fill_color(self, uol_c, uil_c, lol_c, lil_c):
        """ Fill colour in lips. """
        self.__fill_lip_lines(uol_c, uil_c)
        self.__fill_lip_lines(lol_c, lil_c)
        self.__add_color(1)
        self.__fill_lip_solid(uol_c, uil_c)
        self.__fill_lip_solid(lol_c, lil_c)
        self.__smoothen_color(uol_c, uil_c)
        self.__smoothen_color(lol_c, lil_c)


    def __create_eye_liner(self, eyes_points):
        """ Apply eyeliner. """
        left_eye = eyes_points[0].split('\n')
        right_eye = eyes_points[1].split('\n')
        right_eye = right_eye[0:4]
        self.__draw_liner(left_eye, 'left')
        self.__draw_liner(right_eye, 'right')


    def get_boundary_points(self, x, y):
        tck, u = interpolate.splprep([x, y], s=0, per=1)
        unew = np.linspace(u.min(), u.max(), 1000)
        xnew, ynew = interpolate.splev(unew, tck, der=0)
        tup = c_[xnew.astype(int), ynew.astype(int)].tolist()
        coord = list(set(tuple(map(tuple, tup))))
        coord = np.array([list(elem) for elem in coord])
        return np.array(coord[:, 0], dtype=np.int32), np.array(coord[:, 1], dtype=np.int32)


    def get_interior_points(self, x, y):
        intx = []
        inty = []

        def ext(a, b, i):
            a, b = round(a), round(b)
            intx.extend(arange(a, b, 1).tolist())
            inty.extend((ones(b - a) * i).tolist())

        x, y = np.array(x), np.array(y)
        xmin, xmax = amin(x), amax(x)
        xrang = np.arange(xmin, xmax + 1, 1)
        for i in xrang:
            ylist = y[where(x == i)]
            ext(amin(ylist), amax(ylist), i)
        return np.array(intx, dtype=np.int32), np.array(inty, dtype=np.int32)


    def apply_blush_color(self, r, g, b):
        val = color.rgb2lab((self.image / 255.)).reshape(self.width * self.height, 3)
        L, A, B = mean(val[:, 0]), mean(val[:, 1]), mean(val[:, 2])
        L1, A1, B1 = color.rgb2lab(np.array((r / 255., g / 255., b / 255.)).reshape(1, 1, 3)).reshape(3, )
        ll, aa, bb = (L1 - L) * intensivity, (A1 - A) * intensivity, (B1 - B) * intensivity
        val[:, 0] = np.clip(val[:, 0] + ll, 0, 100)
        val[:, 1] = np.clip(val[:, 1] + aa, -127, 128)
        val[:, 2] = np.clip(val[:, 2] + bb, -127, 128)
        self.image = color.lab2rgb(val.reshape(self.height, self.width, 3)) * 255

    def apply_eyeshadow_color(self, r, g, b):
        val = color.rgb2lab((self.image / 255.)).reshape(self.width * self.height, 3)
        L, A, B = mean(val[:, 0]), mean(val[:, 1]), mean(val[:, 2])
        L1, A1, B1 = color.rgb2lab(np.array((r / 255., g / 255., b / 255.)).reshape(1, 1, 3)).reshape(3, )
        ll, aa, bb = (L1 - L) * 0.5, (A1 - A) * 0.5, (B1 - B) * 0.5
        val[:, 0] = np.clip(val[:, 0] + ll, 0, 100)
        val[:, 1] = np.clip(val[:, 1] + aa, -127, 128)
        val[:, 2] = np.clip(val[:, 2] + bb, -127, 128)
        self.image = color.lab2rgb(val.reshape(self.height, self.width, 3)) * 255

    def smoothen_blush(self, x, y):
        imgBase = zeros((self.height, self.width))
        cv2.fillConvexPoly(imgBase, np.array(c_[x, y], dtype='int32'), 1)
        imgMask = cv2.GaussianBlur(imgBase, (201, 201), 0)
        imgBlur3D = np.ndarray([self.height, self.width, 3], dtype='float')
        imgBlur3D[:, :, 0] = imgMask
        imgBlur3D[:, :, 1] = imgMask
        imgBlur3D[:, :, 2] = imgMask
        self.im_copy = (imgBlur3D * self.image + (1 - imgBlur3D) * self.im_copy).astype('uint8')

    def smoothen_eyeshadow(self, x, y):
        imgBase = zeros((self.height, self.width))
        cv2.fillConvexPoly(imgBase, np.array(c_[x, y], dtype='int32'), 1)
        imgMask = cv2.GaussianBlur(imgBase, (51, 51), 0)
        imgBlur3D = np.ndarray([self.height, self.width, 3], dtype='float')
        imgBlur3D[:, :, 0] = imgMask
        imgBlur3D[:, :, 1] = imgMask
        imgBlur3D[:, :, 2] = imgMask
        self.im_copy = (imgBlur3D * self.image + (1 - imgBlur3D) * self.im_copy).astype('uint8')
        
    def apply_eyeshadow(self, filename, list_points, reyeshadow, geyeshadow, beyeshadow):
        self.red_eye = reyeshadow
        self.green_eye = geyeshadow
        self.blue_eye = beyeshadow
        self.__read_image(filename)
        
        eyeshadow_rigth_x, eyeshadow_rigth_y = self.get_eyeshadows_right(self.image, list_points)
        eyeshadow_left_x, eyeshadow_left_y = self.get_eyeshadows_left(self.image, list_points)
        
        eyeshadow_left_x, eyeshadow_left_y = self.get_boundary_points(eyeshadow_left_x, eyeshadow_left_y)
        eyeshadow_rigth_x, eyeshadow_rigth_y = self.get_boundary_points(eyeshadow_rigth_x, eyeshadow_rigth_y)
        eyeshadow_left_x, eyeshadow_left_y = self.get_interior_points(eyeshadow_left_x, eyeshadow_left_y)
        eyeshadow_rigth_x, eyeshadow_rigth_y = self.get_interior_points(eyeshadow_rigth_x, eyeshadow_rigth_y)
        
        self.apply_eyeshadow_color(reyeshadow, geyeshadow, beyeshadow)
        self.smoothen_eyeshadow(eyeshadow_left_x, eyeshadow_left_y)
        self.smoothen_eyeshadow(eyeshadow_rigth_x, eyeshadow_rigth_y)

        self.im_copy = cv2.cvtColor(self.im_copy, cv2.COLOR_BGR2RGB)
        name = '_color_' + str(self.red_b) + '_' + str(self.green_b) + '_' + str(self.blue_b)
        file_name = 'output_' + name + '.jpg'
        cv2.imwrite(file_name, self.im_copy)
        return file_name
    
    def apply_blush(self, filename, list_points, rblush, gblush, bblush):
        self.red_b = rblush
        self.green_b = gblush
        self.blue_b = bblush
        self.__read_image(filename)
        
        blush_rigth_x, blush_rigth_y = self.get_blushs_right(self.image, list_points)
        blush_left_x, blush_left_y = self.get_blushs_left(self.image, list_points)
        
        blush_left_x, blush_left_y = self.get_boundary_points(blush_left_x, blush_left_y)
        blush_rigth_x, blush_rigth_y = self.get_boundary_points(blush_rigth_x, blush_rigth_y)
        blush_left_x, blush_left_y = self.get_interior_points(blush_left_x, blush_left_y)
        blush_rigth_x, blush_rigth_y = self.get_interior_points(blush_rigth_x, blush_rigth_y)
        
        self.apply_blush_color(rblush, gblush, bblush)
        self.smoothen_blush(blush_left_x, blush_left_y)
        self.smoothen_blush(blush_rigth_x, blush_rigth_y)

        self.im_copy = cv2.cvtColor(self.im_copy, cv2.COLOR_BGR2RGB)
        name = '_color_' + str(self.red_b) + '_' + str(self.green_b) + '_' + str(self.blue_b)
        file_name = 'output_' + name + '.jpg'
        cv2.imwrite(file_name, self.im_copy)
        return file_name
        
    def apply_lipstick(self, filename, list_points, rlips, glips, blips):

        self.red_l = rlips
        self.green_l = glips
        self.blue_l = blips
        self.__read_image(filename)
        lips = self.get_lips(self.image, list_points)
        lips = list([point.split() for point in lips.split('\n')])
        lips_points = [item for sublist in lips for item in sublist]
        uol, uil, lol, lil = self.__get_points_lips(lips_points)
        uol_c, uil_c, lol_c, lil_c = self.__get_curves_lips(uol, uil, lol, lil)
        self.__fill_color(uol_c, uil_c, lol_c, lil_c)
        self.im_copy = cv2.cvtColor(self.im_copy, cv2.COLOR_BGR2RGB)
        name = 'color_' + str(self.red_l) + '_' + str(self.green_l) + '_' + str(self.blue_l)
        file_name = 'output_' + name + '.jpg'
        cv2.imwrite(file_name, self.im_copy)
        return file_name

    def apply_liner(self, filename, list_points):
        """
        Applies lipstick on an input image.
        ___________________________________
        Args:
            1. `filename (str)`: Path for stored input image file.

        Returns:
            `filepath (str)` of the saved output file, with applied lipstick.

        """
        self.__read_image(filename)
        liner = self.get_upper_eyelids(self.image, list_points)
        eyes_points = liner.split('\n\n')
        self.__create_eye_liner(eyes_points)
        self.im_copy = cv2.cvtColor(self.im_copy, cv2.COLOR_BGR2RGB)
        name = '_color_' + str(self.red_l) + '_' + str(self.green_l) + '_' + str(self.blue_l)
        file_name = 'output_' + name + '.jpg'
        cv2.imwrite(file_name, self.im_copy)
        return file_name

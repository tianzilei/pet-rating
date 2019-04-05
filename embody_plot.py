#!/usr/bin/env python

"""
Visualize emBODY data

This python script is based on matlab code found from:
https://version.aalto.fi/gitlab/eglerean/embody/tree/master/matlab

Data is loaded from hardcoded experiment (exp_id)
-> TODO: create argument parser where user determines which 
         experiment is used or if data is loaded from all answers

Requirements:
    - python 3+
    - matplotlib
    - numpy
    - scipy

Run:
python embody_plot.py
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import scipy.ndimage as ndimage
import sys
import time
import json
import resource
import mysql.connector as mariadb

mariadb_connection = mariadb.connect(
    user='rating', 
    password='rating_passwd', 
    database='rating_db'
    )
cursor = mariadb_connection.cursor()

start = time.time()

def matlab_style_gauss2D(shape=(1,1),sigma=5):
    """2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])"""

    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h

# Hard coded image size
WIDTH = 207
HEIGHT = 600

# import image
image_path = './app/static/img/dummy_600.png'
image_path_mask = './app/static/img/dummy_600_mask.png'

# Load image to a plot
image = mpimg.imread(image_path)
image_mask = mpimg.imread(image_path_mask)

# Interpolation methods
methods = ['none','bilinear', 'bicubic', 'gaussian']

SELECT_ALL = ("SELECT coordinates from embody_answer")
SELECT_BY_EXP_ID = 'select coordinates from embody_answer as em JOIN (SELECT idanswer_set FROM answer_set as a JOIN experiment as e ON a.experiment_idexperiment=e.idexperiment AND e.idexperiment=%s) as ida ON em.answer_set_idanswer_set=ida.idanswer_set'

exp_id = 2
cursor.execute(SELECT_BY_EXP_ID, (exp_id,))

# Init coordinate arrays
x=[]
y=[]

# Loop through all of the saved coordinates and push them to coordinates arrays
for coordinate in cursor:
    coordinates = json.loads(coordinate[0])
    x.extend(coordinates['x'])
    y.extend(coordinates['y'])


def map_coordinates(a,b):
    return [a,b]

coordinates = list(map(map_coordinates, x,y))

# Plot coordinates as points
plt.subplot2grid((2, 2), (0, 0))
plt.title("raw points")
plt.plot(x,y, 'ro', alpha=0.2)
plt.imshow(image)
plt.grid(True)

# Draw circles from coordinates (imshow don't need interpolation)
plt.subplot2grid((2, 2), (0, 1))
plt.title("gaussian disk around points")
frame = np.zeros((HEIGHT,WIDTH))
for point in coordinates:
    frame[point[1], point[0]] = 1
    point = ndimage.gaussian_filter(frame, sigma=5)
    plt.imshow(point, cmap='hot', interpolation='none')

plt.imshow(image_mask)
plt.grid(True)

# Draw a gaussian heatmap on the whole image
# NOT USABLE
x_min = min(x)
x_max = max(x)
y_min = min(y)
y_max = max(y)
extent=[x_min, x_max, y_min, y_max]
extent_all = [0,WIDTH,0,HEIGHT]
plt.subplot2grid((2, 2), (1, 1))
plt.title('gaussian heatmap')
plt.imshow(image)
plt.imshow(coordinates, extent=extent, cmap='hot', interpolation='gaussian')
plt.imshow(image_mask)

end = time.time()
print("Drawing image took:", end - start)

mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()


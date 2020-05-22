'''
Script for testing embody drawing results from onni.utu.fi

Install requirements:
pip install numpy
pip install matplotlib

Usage:
Export data from onni.utu.fi and after that run the script in the same folder
by passing exported_file as a parameter to the script

$ python plot_image.py <exported_file>.csv

Program prints header of the file, from which you must select column where the 
image data is. After you have selected the right column, program prints the 
drawing results from embody answers.

If you want the program to draw default embody image to the background, then 
you must put a copy of the 'dummy_6000.png' -file (this is the same that is used 
in onni.utu.fu) to the same path as the script.

'''

import copy

import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
import json

csv.field_size_limit(sys.maxsize)


def show_images(images, cols=1, titles=None):
    """Display a list of images in a single figure with matplotlib.
    Parameters
    ---------
    images: List of np.arrays compatible with plt.imshow.

    cols (Default = 1): Number of columns in figure (number of rows is 
                        set to np.ceil(n_images/float(cols))).

    titles: List of titles corresponding to each image. Must have
            the same length as titles.
    """

    # default embody image for the background

    try:
        background = True
        default_img = plt.imread("./dummy_600.png")
    except FileNotFoundError:
        background = False

    # get a copy of the gray color map
    my_cmap = copy.copy(plt.cm.get_cmap('gray'))
    # set how the colormap handles 'bad' values
    my_cmap.set_bad(alpha=0)  


    assert((titles is None) or (len(images) == len(titles)))
    n_images = len(images)
    if titles is None:
        titles = ['Image (%d)' % i for i in range(1, n_images + 1)]
    fig = plt.figure()
    for n, (image, title) in enumerate(zip(images, titles)):

        a = fig.add_subplot(cols, np.ceil(n_images/float(cols)), n + 1)

        # draw points from users answers
        plt.imshow(image, cmap=my_cmap)

        # draw default background image with transparency on top of the points
        if background:
            plt.imshow(default_img, extent=[0, 200, 600, 0], alpha=0.33)

        a.set_title(title)

    fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
    plt.show()


if __name__ == '__main__':

    images = []
    titles = []

    # filename = 'experiment_1_2020-05-20.csv'
    filename = sys.argv[1]

    with open(filename, 'r+') as csvfile:
        for row_no, row in enumerate(csv.reader(csvfile, delimiter=';')):

            # parse header
            if row_no == 0:
                for column, title in enumerate(row):
                    print("Column (no. {}): {}".format(column, title))

                print('Enter the column number which has image data:')
                x = int(input())
                continue

            try:
                np_array = np.array(eval(row[x]))
            except NameError:
                print(
                    "Column didn't contain image data. Try again with different column number.")

            np_array = np.transpose(np_array)
            images.append(np_array)

            # add id of the answerer to the image
            titles.append(row[0])

    show_images(images, titles=titles)

'''
Script for testing embody drawing results from onni.utu.fi

Install requirements:
pip install tqdm
pip install numpy
pip install matplotlib

Usage:
Export data from onni.utu.fi and after that run the script in the same folder
by passing exported_file as a parameter to the script (NOTE that you must have
the default background image <dummy_600.png> also in the same path as the script).

$ python plot_image.py <exported_file>.csv

Program prints header of the file, from which you must select column where the 
image data is. After you have selected the right column, program prints the 
drawing results from embody answers.

'''

import copy
import csv
import sys
import subprocess

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

csv.field_size_limit(sys.maxsize)


def show_one_image_per_answer(images, cols=1, titles=None):
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


def show_images(images):
    """Display all data from list of images in a single figure with matplotlib.
    Parameters
    ---------
    images: List of np.arrays compatible with plt.imshow.
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
    n_images = len(images)
    fig = plt.figure()
    all_images = np.zeros(shape=(602,207)) 
    for n, (image, title) in enumerate(zip(images, titles)):
        all_images += image

    plt.imshow(all_images, cmap=my_cmap)

    if background:
        plt.imshow(default_img, extent=[0, 200, 600, 0], alpha=0.33)

    fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
    plt.show()


if __name__ == '__main__':

    filename = sys.argv[1]

    skipped = 0
    empty = 0
    rows = 0
    images = []
    titles = []

    # count the file length
    output = subprocess.check_output(f"wc -l {filename}", shell=True, stderr=subprocess.STDOUT)
    wc = output.decode("utf-8").split(" ")[0]

    with open(filename, 'r+') as csvfile:
        csv_rows = csv.reader(csvfile, delimiter=';')

        for row_no, row in enumerate(tqdm(csv_rows, total=int(wc))):
            rows += 1

            # parse header
            if row_no == 0:
                for column, title in enumerate(row):
                    if "embody_question" in title:
                        print("Column (ID {}): {}".format(column, title))

                print('\nEnter the column ID from which you want to see image data:')
                x = int(input())
                print("\n...processing images...\n")
                continue

            try:
                # skip empty rows (no answer at all)
                if not row[x]:
                    skipped += 1
                    continue

                np_array = np.array(eval(row[x]))

                # skip empty answers (user hasn't drawed on the picture at all)
                if np.all((np_array == 0)):
                    empty += 1
                    continue
            except NameError:
                print(
                    "Column didn't contain image data. Try again with different column ID.")
            except SyntaxError as err:
                continue
            except IndexError as err:
                continue

            np_array = np.transpose(np_array)
            images.append(np_array)

            # add id of the answerer to the image
            titles.append(row[0])

        print(f"\nExperiment started {rows} times")
        print(f"from which users has skipped {skipped + empty} times this question\n")

        # show all answers from one column in one image
        show_images(images)

        # show all answer from one column in own images
        # OBS: this works decently only with small amount of answers
        # show_one_image_per_answer(images, titles=titles)

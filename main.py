# Ryan Bercich
# University of St. Thomas - SCALE Microelectronics
# 20 July 2026
# main.py

# This program intends to detect coordinates of the chip relative to the teeth of the robotic arm.

import cv2 as cv
import numpy as np


def prepare_panel(image, label, width=1280):
    """Convert an image to BGR, resize it, and add a label."""
    if len(image.shape) == 2:
        image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)

    scale = width / image.shape[1]
    panel = cv.resize(image, (width, round(image.shape[0] * scale)))
    cv.rectangle(panel, (0, 0), (panel.shape[1], 42), (0, 0, 0), -1)
    cv.putText(panel, label, (12, 29), cv.FONT_HERSHEY_SIMPLEX,
               0.8, (255, 255, 255), 2, cv.LINE_AA)
    return panel


def main():
    # Load an image from file
    image = cv.imread('benilde.jpg')

    # Check if the image was loaded successfully
    if image is None:
        print("Error: Could not load image.")
        return

    # Convert the image to grayscale
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the grayscale image
    blurred_image = cv.GaussianBlur(gray_image, (5, 5), 0)

    # Perform edge detection using Canny
    edges = cv.Canny(blurred_image, 100, 200)

    # Put all four images into one labeled 2x2 display.
    original_panel = prepare_panel(image, 'Original')
    gray_panel = prepare_panel(gray_image, 'Grayscale')
    blurred_panel = prepare_panel(blurred_image, 'Gaussian Blur')
    edges_panel = prepare_panel(edges, 'Canny Edges')

    top_row = np.hstack((original_panel, gray_panel))
    bottom_row = np.hstack((blurred_panel, edges_panel))
    combined_view = np.vstack((top_row, bottom_row))

    cv.imshow('Chip Vision - Four Views', combined_view)

    # Wait for a key press and close the windows
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()

# Ryan Bercich
# University of St. Thomas - SCALE Microelectronics
# 20 July 2026

# This program intends to detect coordinates of the chip relative to the teeth of the robotic arm.

import cv2 as cv
import numpy as np

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

    # Display the original and processed images
    cv.imshow('Original Image', image)
    cv.imshow('Grayscale Image', gray_image)
    cv.imshow('Blurred Image', blurred_image)
    cv.imshow('Edges', edges)

    # Wait for a key press and close the windows
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
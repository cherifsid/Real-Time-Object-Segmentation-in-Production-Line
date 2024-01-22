import argparse
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt

# Function to plot the input image and the corresponding mask side by side
def plot_image_and_mask(image_path, mask_path):
    # Read the original image and mask
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    # Convert to RGB for matplotlib
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Plot the original image and mask side by side
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(image)
    axs[0].set_title('Original Image')
    axs[0].axis('off')

    axs[1].imshow(mask, cmap='gray')
    axs[1].set_title('Generated Mask')
    axs[1].axis('off')

    plt.show()




# Function to create mask with adjusted HSV
def create_mask_with_adjusted_hsv(image_path, output_path, lower_hsv, upper_hsv):
    # Read the image
    image = cv2.imread(image_path)

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # Invert the mask to have the object in white
    mask_inv = cv2.bitwise_not(mask)

    # Apply morphological operations to clean up the mask
    kernel = np.ones((10, 10), np.uint8)
    mask_cleaned = cv2.morphologyEx(mask_inv, cv2.MORPH_OPEN, kernel)
    mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)

    # Save the mask to the specified output path
    cv2.imwrite(output_path, mask_cleaned)


# Setup argument parsing
parser = argparse.ArgumentParser(description="Image Segmentation Script")
parser.add_argument('--input_dir', type=str, help="Path to the input image directory")
parser.add_argument('--output_dir', type=str, help="Path to the output mask directory")

# Parse arguments
args = parser.parse_args()

# Use the provided arguments
input_dir = args.input_dir or 'default/input/directory/path'
output_dir = args.output_dir or 'default/output/directory/path'

if __name__ == "__main__":
    # Define the provided RGB values (to calculate the mean ranage of the green background with different luminosity)
    rgb_values = [
        (0, 121, 110), (1, 117, 108), (1, 129, 116), (0, 123, 102),
        (0, 126, 105), (0, 130, 118), (0, 130, 118), (0, 125, 104),
        (1, 129, 114), (1, 129, 114)
    ]

    # Convert RGB to HSV
    hsv_values = [cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0] for rgb in rgb_values]

    # Calculate the min and max HSV values
    min_hsv = np.min(hsv_values, axis=0)
    max_hsv = np.max(hsv_values, axis=0)

    # Adjust the HSV range to be a bit more tolerant
    adjusted_lower_hsv = min_hsv.copy()
    adjusted_upper_hsv = max_hsv.copy()

    # (Based on servel experimentation )
    # Increase the tolerance for the hue
    adjusted_lower_hsv[0] -= 10
    adjusted_upper_hsv[0] += 10

    # Decrease the saturation threshold to include slightly less saturated greens
    adjusted_lower_hsv[1] -= 80

    # Increase the value range to accommodate different lighting conditions
    adjusted_lower_hsv[2] -= 82
    adjusted_upper_hsv[2] += 82

    # Clear the output directory if it is not empty
    if os.listdir(output_dir):
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))

    # Process all images in the input directory
    for image_file in os.listdir(input_dir):
        image_path = os.path.join(input_dir, image_file)
        if os.path.isfile(image_path) and image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            output_path = os.path.join(output_dir, os.path.splitext(image_file)[0] + '_mask.jpg')
            create_mask_with_adjusted_hsv(image_path, output_path, adjusted_lower_hsv, adjusted_upper_hsv)

    print("Processing complete. Masks saved to", output_dir)

    # After creating all masks, plot each image and its mask side by side
    for image_file in os.listdir(input_dir):
        image_path = os.path.join(input_dir, image_file)
        mask_file = os.path.splitext(image_file)[0] + '_mask.jpg'
        mask_path = os.path.join(output_dir, mask_file)

        if os.path.isfile(image_path) and image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            plot_image_and_mask(image_path, mask_path)

    print("All images and masks have been processed and plotted.")

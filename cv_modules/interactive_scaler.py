"""
Module for interactive scaling of images.

This module provides a class to allow users to define a scale for an image
by selecting two points and providing a known real-world distance.
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import logging

logger = logging.getLogger(__name__)

class InteractiveScaler:
    """
    A class to determine the scale of an image interactively.
    """

    def __init__(self, image_path: str):
        """
        Initialize the InteractiveScaler.

        Args:
            image_path: Path to the image file.
        """
        self.image_path = image_path
        self.points = []
        self.image = None
        self.original_image = None
        self.tk_image = None
        self.scale = None

    def _click_event(self, event):
        """
        Callback function for mouse clicks.
        """
        if len(self.points) < 2:
            self.points.append((event.x, event.y))
            logger.info(f"Point {len(self.points)} selected: ({event.x}, {event.y})")
            # Draw a circle on the image to mark the point
            if self.image is not None:
                cv2.circle(self.image, (event.x, event.y), 5, (0, 255, 0), -1)
                self.tk_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        if len(self.points) == 2:
            self.root.after(100, self.get_distance_and_calculate_scale)


    def get_distance_and_calculate_scale(self):
        """
        Get the real-world distance from the user and calculate the scale.
        """
        distance_str = simpledialog.askstring("Input", "Enter the real-world distance in meters:", parent=self.root)
        if distance_str:
            try:
                distance_m = float(distance_str)
                if distance_m <= 0:
                    raise ValueError("Distance must be positive.")

                pixel_distance = np.linalg.norm(np.array(self.points[0]) - np.array(self.points[1]))
                self.scale = pixel_distance / distance_m
                logger.info(f"Pixel distance: {pixel_distance}, Real-world distance: {distance_m}m, Scale: {self.scale} px/m")
                messagebox.showinfo("Success", f"Scale calculated: {self.scale:.2f} pixels/meter")
                self.root.quit()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
                self.points = [] # Reset points
                self.image = self.original_image.copy() # Reset image
                self.tk_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        else:
            self.points = [] # Reset points if user cancels
            self.image = self.original_image.copy() # Reset image
            self.tk_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)


    def get_scale(self) -> float:
        """
        Display the image and get the scale from the user.

        Returns:
            The calculated scale in pixels per meter, or None if the user cancels.
        """
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            logger.error(f"Failed to load image: {self.image_path}")
            return None
        self.original_image = self.image.copy()

        self.root = tk.Tk()
        self.root.title("Interactive Scaler - Select two points")

        # Convert image for tkinter
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)))

        self.canvas = tk.Canvas(self.root, width=self.image.shape[1], height=self.image.shape[0])
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.bind("<Button-1>", self._click_event)

        self.root.mainloop()

        return self.scale

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Interactively determine the scale of an image.")
    parser.add_argument('-i', '--input', required=True, help="Path to the input image.")
    parser.add_argument('-o', '--output', required=True, help="Path to save the scale information (e.g., scale.txt).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    scaler = InteractiveScaler(args.input)
    scale = scaler.get_scale()

    if scale is not None:
        with open(args.output, 'w') as f:
            f.write(str(scale))
        logger.info(f"Scale saved to {args.output}")
    else:
        logger.warning("Scale calculation was cancelled.")

"""
Tests for the InteractiveScaler module.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import numpy as np
from cv_modules.interactive_scaler import InteractiveScaler

class TestInteractiveScaler(unittest.TestCase):
    """
    Test suite for the InteractiveScaler class.
    """

    def setUp(self):
        """
        Set up a dummy image file for testing.
        """
        self.test_image_path = 'test_image.png'
        # Create a dummy image file
        with open(self.test_image_path, 'w') as f:
            f.write('dummy image data')

    def tearDown(self):
        """
        Remove the dummy image file after tests.
        """
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)

    @patch('cv_modules.interactive_scaler.tk.Tk')
    @patch('cv_modules.interactive_scaler.cv2.imread')
    def test_initialization(self, mock_imread, mock_tk):
        """
        Test that the InteractiveScaler class initializes correctly.
        """
        mock_imread.return_value = MagicMock()
        scaler = InteractiveScaler(self.test_image_path)
        self.assertEqual(scaler.image_path, self.test_image_path)
        self.assertEqual(scaler.points, [])
        self.assertIsNone(scaler.scale)

    @patch('cv_modules.interactive_scaler.ImageTk.PhotoImage')
    @patch('cv_modules.interactive_scaler.tk.Tk')
    @patch('cv_modules.interactive_scaler.cv2.imread')
    @patch('cv_modules.interactive_scaler.simpledialog.askstring', return_value='2.5')
    def test_get_scale(self, mock_askstring, mock_imread, mock_tk, mock_photo_image):
        """
        Test the get_scale method with mocked GUI interaction.
        """
        # Mock the image to have a shape
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image

        scaler = InteractiveScaler(self.test_image_path)

        # Simulate two points being selected
        scaler.points = [(10, 10), (110, 10)]

        # Since the mainloop will be called, we need to mock it to prevent it from blocking
        mock_tk.return_value.mainloop.side_effect = lambda: None

        # To simulate the dialog and calculation, we can call the method that would be called after the second point is clicked
        scaler.get_distance_and_calculate_scale = MagicMock(side_effect=scaler.get_distance_and_calculate_scale)

        scale = scaler.get_scale()

        # We can't easily test the full flow with the mainloop, but we can check the result
        # To do this, let's manually set the root and call the calculation method
        scaler.root = mock_tk()
        scaler.get_distance_and_calculate_scale()

        self.assertIsNotNone(scaler.scale)
        self.assertAlmostEqual(scaler.scale, 40.0) # pixel_distance is 100, distance is 2.5, so 100/2.5 = 40

    @patch('cv_modules.interactive_scaler.ImageTk.PhotoImage')
    @patch('cv_modules.interactive_scaler.tk.Tk')
    @patch('cv_modules.interactive_scaler.cv2.imread')
    @patch('cv_modules.interactive_scaler.simpledialog.askstring', return_value='invalid')
    @patch('cv_modules.interactive_scaler.messagebox.showerror')
    def test_invalid_input(self, mock_showerror, mock_askstring, mock_imread, mock_tk, mock_photo_image):
        """
        Test that invalid input is handled gracefully.
        """
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image

        scaler = InteractiveScaler(self.test_image_path)
        scaler.root = mock_tk()
        scaler.canvas = MagicMock()
        scaler.original_image = mock_image.copy()
        scaler.points = [(10, 10), (110, 10)]

        scaler.get_distance_and_calculate_scale()

        self.assertEqual(scaler.points, [])
        self.assertIsNone(scaler.scale)
        mock_showerror.assert_called_once()

    @patch('cv_modules.interactive_scaler.ImageTk.PhotoImage')
    @patch('cv_modules.interactive_scaler.tk.Tk')
    @patch('cv_modules.interactive_scaler.cv2.imread')
    @patch('cv_modules.interactive_scaler.simpledialog.askstring', return_value=None)
    def test_cancel_input(self, mock_askstring, mock_imread, mock_tk, mock_photo_image):
        """
        Test that canceling the input dialog is handled gracefully.
        """
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image

        scaler = InteractiveScaler(self.test_image_path)
        scaler.root = mock_tk()
        scaler.canvas = MagicMock()
        scaler.original_image = mock_image.copy()
        scaler.points = [(10, 10), (110, 10)]

        scaler.get_distance_and_calculate_scale()

        self.assertEqual(scaler.points, [])
        self.assertIsNone(scaler.scale)


if __name__ == '__main__':
    unittest.main()

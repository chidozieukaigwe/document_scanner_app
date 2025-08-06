import cv2
import numpy as np
from imutils.perspective import four_point_transform

import settings
from utils import get_today_date_as_as_string


class DocumentScanner:
    def __init__(self):
        self.size = None
        self.image = None

    @staticmethod
    def resizer(image, width=500):
        # Compute Height - get width and height
        h, w, c = image.shape
        height = int((h / w) * width)
        size = (width, height)
        image = cv2.resize(image, (width, height))
        return image, size

    @staticmethod
    def apply_brightness_contrast(input_img, brightness=0, contrast=0):
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow

            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()

        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)

            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

        return buf

    def document_scanner(self, image_path):

        # Read Image
        global four_points
        self.image = cv2.imread(image_path)

        # resize image
        img_re, self.size = self.resizer(self.image)

        filename = 'resize_image_' + get_today_date_as_as_string() + '.jpg'

        resized_image_path = settings.join_path(settings.MEDIA_DIR, filename)

        cv2.imwrite(resized_image_path, img_re)

        try:
            # Enhance Image
            detail = cv2.detailEnhance(img_re, sigma_s=20, sigma_r=0.15)
            # Grayscale Image
            gray = cv2.cvtColor(detail, cv2.COLOR_BGR2GRAY)
            # Blur Image
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            # Edge Detection
            edge_image = cv2.Canny(blur, 75, 200)
            # Morphological Transform
            kernel = np.ones((5, 5), np.uint8)
            dilate = cv2.dilate(edge_image, kernel, iterations=1)
            closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)

            # Find The Contours
            contours, hierarchy = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)  # sorting all values in DESC order

            for contour in contours:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

                if len(approx) == 4:
                    four_points = np.squeeze(approx)
                    break
            return four_points, self.size, resized_image_path
        except (RuntimeError, TypeError, NameError):
            return None, self.size

    def calibrate_to_original_size(self, four_points):
        # @todo wrap this in a try catch + produce an exception
        # Find four points for original image
        multiplier = self.image.shape[1] / self.size[0]
        four_points_orig = four_points * multiplier
        four_points_orig = four_points_orig.astype(int)

        # Crop Image
        wrap_image = four_point_transform(self.image, four_points_orig)

        # apply magic color to wrap image
        magic_color = self.apply_brightness_contrast(wrap_image, brightness=40, contrast=60)

        return magic_color

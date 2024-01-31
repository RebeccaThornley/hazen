import cv2
import scipy
import skimage
import numpy as np


class ACRObject:
    """Base class for performing tasks on image sets of the ACR phantom.
    acquired following the ACR Large phantom guidelines
    """

    def __init__(self, dcm_list):
        """Initialise an ACR object instance

        Args:
            dcm_list (list): list of pydicom.Dataset objects - DICOM files loaded
        """

        # # Initialise an ACR object from a stack of images of the ACR phantom
        # self.dcm_list =
        # Perform sorting of the input file list

        for dcm in dcm_list:
            print(dcm.InstanceNumber)
            print(dcm.ImagePositionPatient)
            # The x, y, and z coordinates of the upper left hand corner (center of the first voxel transmitted) of the image, in mm
            # eg [28.364610671997, -88.268096923828, 141.94101905823]
            print(dcm.ImageOrientationPatient)
            # The direction cosines of the first row and the first column with respect to the patient.
            # eg
            # [1, 0, 0, 0, 1, 0]  transverse/axial
            # [1, 0, 0, 0, 0, -1] coronal
            # [0, 1, 0, 0, 0, -1] sagittal
            print(dcm.PixelSpacing)
            # Physical distance in the patient between the center of each pixel, specified by a numeric pair - adjacent row spacing (dx) (delimiter) adjacent column spacing (dy) in mm.
            print(dcm.SliceThickness)
            # Nominal slice thickness, in mm
        # Store file content as pyDICOM objects 'dcms'
        # and their pixel arrays as 'images'
        self.dcms, self.images = self.sort_images(dcm_list)
        # Store the pixel spacing value from the first image (expected to be the same for all)
        self.pixel_spacing = self.dcms[0].PixelSpacing
        # Check whether images of the phantom are the correct orientation
        self.orientation_checks()
        # Determine whether image rotation is necessary
        self.rot_angle = self.determine_rotation()
        for dcm in dcm_list:
            print(dcm.InstanceNumber)
        # Find the centre coordinates of the phantom (circle) on slice 7 only:
        self.centre, self.radius = self.find_phantom_center(self.images[6])
        print(self.centre)
        # Store the DCM object of slice 7 as it is used often
        self.slice7_dcm = self.dcms[6]
        # Store a mask image of slice 7 for reusability
        self.mask_image = self.get_mask_image(self.images[6])

    def sort_images(self, dcm_list):
        """Sort a stack of images based on slice position.

        Args:
            dcm_list (list): list of file paths

        Returns:
            tuple of lists: dcm_stack and img_stack
                dcm_stack - list of pydicom.Dataset objects. \n
                img_stack - list of np.array of dcm.pixel_array: A sorted stack of images, where each image is represented as a 2D numpy array.
        """
        # TODO: implement a check if phantom was placed in other than axial position
        # This is to be able to flag to the user the caveat of measurments if deviating from ACR guidance

        x = np.array([dcm.ImagePositionPatient[0] for dcm in dcm_list])
        y = np.array([dcm.ImagePositionPatient[1] for dcm in dcm_list])
        z = np.array([dcm.ImagePositionPatient[2] for dcm in dcm_list])
        print("x")  # SAG
        print(set(x))
        print(len(set(x)))
        print()

        print("y")  # COR
        print(set(y))
        print(len(set(y)))

        print("z")  # TRA
        print(set(z))
        print(len(set(z)))

        dicom_stack = [dcm_list[i] for i in np.argsort(z)]
        img_stack = [dicom.pixel_array for dicom in dicom_stack]

        return img_stack, dicom_stack

    def orientation_checks(self):
        """Perform orientation checks on a set of images to determine if slice order inversion
        or an LR orientation swap is required. \n

        This function analyzes the given set of images and their associated DICOM objects to determine if any
        adjustments are needed to restore the correct slice order and view orientation.
        """
        first_image = self.images[0]
        last_image = self.images[-1]
        dx = self.pixel_spacing[0]

        normalised_first_image = cv2.normalize(
            src=first_image,
            dst=None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX,
            dtype=cv2.CV_8U,
        )
        normalised_last_image = cv2.normalize(
            src=last_image,
            dst=None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX,
            dtype=cv2.CV_8U,
        )
        print(self.images[0].shape)
        print(dx)
        print(180 / dx)
        print(16 / dx)
        print(5 / dx)

        # search for circle in first slice of ACR phantom dataset with radius of ~11mm
        detected_circles_first = cv2.HoughCircles(
            normalised_first_image,
            cv2.HOUGH_GRADIENT,
            1,
            param1=50,
            param2=30,
            minDist=int(180 / dx),
            minRadius=int(5 / dx),
            maxRadius=int(16 / dx),
        )
        print(detected_circles_first.shape)
        # returns x_centre, y_centre, radius

        detected_circles_last = cv2.HoughCircles(
            normalised_last_image,
            cv2.HOUGH_GRADIENT,
            1,
            param1=50,
            param2=30,
            minDist=int(180 / dx),
            minRadius=int(5 / dx),
            maxRadius=int(16 / dx),
        )

        if detected_circles_first is not None:
            true_circle = detected_circles_first.flatten()
            print("kitty")
        else:
            true_circle = detected_circles_last.flatten()
            print("cat")

        if detected_circles_first is None and detected_circles_last is not None:
            print("Performing slice order inversion to restore correct slice order.")
            self.images.reverse()
            self.dcms.reverse()
            print("kitty")
        else:
            print("Slice order inversion not required.")
            print("cat")

        print(true_circle[0])
        print(self.images[0].shape[0] // 2)
        print(true_circle[0] > self.images[0].shape[0] // 2)
        if true_circle[0] > self.images[0].shape[0] // 2:
            print("Performing LR orientation swap to restore correct view.")
            flipped_images = [np.fliplr(image) for image in self.images]
            for index, dcm in enumerate(self.dcms):
                dcm.PixelData = flipped_images[index].tobytes()
            print("kitty")
        else:
            print("LR orientation swap not required.")
            print("cat")

    def determine_rotation(self):
        """Determine the rotation angle of the phantom using edge detection and the Hough transform.

        Returns:
            float: The rotation angle in degrees.
        """

        thresh = cv2.threshold(self.images[0], 127, 255, cv2.THRESH_BINARY)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilate = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
        diff = cv2.absdiff(dilate, thresh)

        h, theta, d = skimage.transform.hough_line(diff)
        _, angles, _ = skimage.transform.hough_line_peaks(h, theta, d)

        # mode_result = stats.mode(central_roi, axis=None, keepdims=False)

        angle = np.rad2deg(scipy.stats.mode(angles, keepdims=False).mode)
        rot_angle = angle + 90 if angle < 0 else angle - 90

        return rot_angle

    def rotate_images(self):
        """Rotate the images by a specified angle. The value range and dimensions of the image are preserved.

        Returns:
            np.array: The rotated images.
        """

        return skimage.transform.rotate(
            self.images, self.rot_angle, resize=False, preserve_range=True
        )

    def find_phantom_center(self, img):
        """
        Find the center of the ACR phantom by filtering the input slice and using the Hough circle detector.
        Args:
            img (np.array): pixel array of the dicom


        Returns:
            tuple of ints: representing the (x, y) coordinates of the center of the image
        """
        dx, dy = self.pixel_spacing

        img_blur = cv2.GaussianBlur(img, (1, 1), 0)
        img_grad = cv2.Sobel(img_blur, 0, dx=1, dy=1)

        detected_circles = cv2.HoughCircles(
            img_grad,
            cv2.HOUGH_GRADIENT,
            1,
            param1=50,
            param2=30,
            minDist=int(180 / dy),
            minRadius=int(180 / (2 * dy)),
            maxRadius=int(200 / (2 * dx)),
        ).flatten()
        centre = [int(i) for i in detected_circles[:2]]
        radius = int(detected_circles[2])
        return centre, radius

    def get_mask_image(self, image, mag_threshold=0.07, open_threshold=500):
        """Create a masked pixel array \n
        Mask an image by magnitude threshold before applying morphological opening to remove small unconnected
        features. The convex hull is calculated in order to accommodate for potential air bubbles.

        Args:
            image (np.array): pixel array of the dicom
            mag_threshold (float, optional): magnitude threshold. Defaults to 0.07.
            open_threshold (int, optional): open threshold. Defaults to 500.

        Returns:
            np.array: the masked image
        """
        test_mask = self.circular_mask(
            self.centre, (80 // self.pixel_spacing[0]), image.shape
        )
        test_image = image * test_mask
        test_vals = test_image[np.nonzero(test_image)]
        if np.percentile(test_vals, 80) - np.percentile(test_vals, 10) > 0.9 * np.max(
            image
        ):
            print(
                "Large intensity variations detected in image. Using local thresholding!"
            )
            initial_mask = skimage.filters.threshold_sauvola(
                image, window_size=3, k=0.95
            )
        else:
            initial_mask = image > mag_threshold * np.max(image)

        opened_mask = skimage.morphology.area_opening(
            initial_mask, area_threshold=open_threshold
        )
        final_mask = skimage.morphology.convex_hull_image(opened_mask)

        return final_mask

    @staticmethod
    def circular_mask(centre, radius, dims):
        """Sort a stack of images based on slice position.

        Args:
            centre (tuple): centre coordinates of the circular mask.
            radius (int): radius of the circular mask.
            dims (tuple): dimensions of the circular mask.

        Returns:
            np.array: A sorted stack of images, where each image is represented as a 2D numpy array.
        """
        # Define a circular logical mask
        x = np.linspace(1, dims[0], dims[0])
        y = np.linspace(1, dims[1], dims[1])

        X, Y = np.meshgrid(x, y)
        mask = (X - centre[0]) ** 2 + (Y - centre[1]) ** 2 <= radius**2

        return mask

    def measure_orthogonal_lengths(self, mask, slice_index):
        """Compute the horizontal and vertical lengths of a mask, based on the centroid.

        Args:
            mask (np.array): Boolean array of the image where pixel values meet threshold

        Returns:
            dict: a dictionary with the following
                'Horizontal Start'      | 'Vertical Start' : tuple of int
                    Horizontal/vertical starting point of the object.
                'Horizontal End'        | 'Vertical End' : tuple of int
                    Horizontal/vertical ending point of the object.
                'Horizontal Extent'     | 'Vertical Extent' : ndarray of int
                    Indices of the non-zero elements of the horizontal/vertical line profile.
                'Horizontal Distance'   | 'Vertical Distance' : float
                    The horizontal/vertical length of the object.
        """
        dims = mask.shape
        dx, dy = self.pixel_spacing
        [(vertical, horizontal), radius] = self.find_phantom_center(
            self.images[slice_index]
        )

        horizontal_start = (horizontal, 0)
        horizontal_end = (horizontal, dims[0] - 1)
        horizontal_line_profile = skimage.measure.profile_line(
            mask, horizontal_start, horizontal_end
        )
        horizontal_extent = np.nonzero(horizontal_line_profile)[0]
        horizontal_distance = (horizontal_extent[-1] - horizontal_extent[0]) * dx

        vertical_start = (0, vertical)
        vertical_end = (dims[1] - 1, vertical)
        vertical_line_profile = skimage.measure.profile_line(
            mask, vertical_start, vertical_end
        )
        vertical_extent = np.nonzero(vertical_line_profile)[0]
        vertical_distance = (vertical_extent[-1] - vertical_extent[0]) * dy

        length_dict = {
            "Horizontal Start": horizontal_start,
            "Horizontal End": horizontal_end,
            "Horizontal Extent": horizontal_extent,
            "Horizontal Distance": horizontal_distance,
            "Vertical Start": vertical_start,
            "Vertical End": vertical_end,
            "Vertical Extent": vertical_extent,
            "Vertical Distance": vertical_distance,
        }

        return length_dict

    @staticmethod
    def rotate_point(origin, point, angle):
        """Compute the horizontal and vertical lengths of a mask, based on the centroid.

        Args:
            origin (tuple): The coordinates of the point around which the rotation is performed.
            point (tuple): The coordinates of the point to rotate.
            angle (int): Angle in degrees.

        Returns:
            tuple of float: x_prime and y_prime
                Floats representing the x and y coordinates of the input point
                after being rotated around an origin.
        """
        theta = np.radians(angle)
        c, s = np.cos(theta), np.sin(theta)

        x_prime = origin[0] + c * (point[0] - origin[0]) - s * (point[1] - origin[1])
        y_prime = origin[1] + s * (point[0] - origin[0]) + c * (point[1] - origin[1])
        return x_prime, y_prime

    @staticmethod
    def find_n_highest_peaks(data, n, height=1):
        """Find the indices and amplitudes of the N highest peaks within a 1D array.

        Args:
            data (np.array): pixel array containing the data to perform peak extraction on
            n (int): The coordinates of the point to rotate
            height (int, optional): The amplitude threshold for peak identification. Defaults to 1.

        Returns:
            tuple of np.array: peak_locs and peak_heights
                peak_locs: A numpy array containing the indices of the N highest peaks identified. \n
                peak_heights: A numpy array containing the amplitudes of the N highest peaks identified.

        """
        peaks = scipy.signal.find_peaks(data, height)
        pk_heights = peaks[1]["peak_heights"]
        pk_ind = peaks[0]

        peak_heights = pk_heights[
            (-pk_heights).argsort()[:n]
        ]  # find n highest peak amplitudes
        peak_locs = pk_ind[(-pk_heights).argsort()[:n]]  # find n highest peak locations

        return np.sort(peak_locs), np.sort(peak_heights)

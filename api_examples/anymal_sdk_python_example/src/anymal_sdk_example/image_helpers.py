import numpy as np
import cv2 as cv
import logging
from typing import Optional

import anymal_api_proto as api


def convert_image_to_numpy(image: api.Image) -> np.ndarray:
    """
    Convert image to numpy.
    :param image: Input image.
    :return: Numpy image.
    """
    # Interpret the image from the buffer.
    if image.encoding == "mono16":
        # Mono16 encoding -> uint16 data type.
        np_buffer = np.frombuffer(image.data, "uint16")
        np_image = np.ndarray(shape=(image.height, image.width, 1), dtype="uint16", buffer=np_buffer)
    elif image.encoding == "bgr8":
        # BGR encoding -> unit8 with 3 channels.
        np_buffer = np.frombuffer(image.data, "uint8")
        np_image = np.ndarray(shape=(image.height, image.width, 3), dtype="uint8", buffer=np_buffer)
    elif image.encoding == "rgb8":
        # RGB8 encoding -> unit8 with 3 channels.
        np_buffer = np.frombuffer(image.data, "uint8")
        np_image = np.ndarray(shape=(image.height, image.width, 3), dtype="uint8", buffer=np_buffer)
        np_image = np_image[:, :, ::-1]  # RGB to BRG
    elif image.encoding.endswith(",jpeg") or image.encoding.endswith(",jpg") or image.encoding.endswith(",png"):
        # Decode the image using OpenCV. This will by default return a BGR image.
        np_buffer = np.frombuffer(image.data, "uint8")
        np_image = cv.imdecode(np_buffer, cv.IMREAD_UNCHANGED)
    else:
        raise RuntimeError(f"Encoding '{image.encoding}' not supported.")

    return np_image


def convert_thermal_image_to_numpy(
    thermal_image: api.ThermalImage,
) -> np.ndarray:
    """
    Convert the thermal image to a color gradient image.
    :param thermal_image: Thermal image.
    :return: Numpy temperature image.
    """
    image = thermal_image.image

    # Transform the image from mono16 to a gradient image for display.
    np_image = convert_image_to_numpy(image)
    # Convert to temperatures using the linear mapping.
    np_image_temperature = np_image * thermal_image.gain + thermal_image.offset

    return np_image_temperature


def convert_thermal_image_to_opencv_with_legend(
    thermal_image: api.ThermalImage,
    temperature_image: np.ndarray,
    inspected_max: Optional[float] = None,
) -> np.ndarray:
    """
    Get a thermal image with annotated min and max temperature.
    :param thermal_image: Thermal image.
    :param temperature_image: Temperature image.
    :param inspected_max: Max temperature detected by the onboard inspection.
    :return: Numpy gradient image
    """
    image = thermal_image.image

    # Normalize the image as the temperatures are in a narrow range.
    norm_image = cv.normalize(
        temperature_image,
        None,
        alpha=0,
        beta=255,
        norm_type=cv.NORM_MINMAX,
        dtype=cv.CV_8U,
    )
    # Apply the jet color map.
    gradient_image = cv.applyColorMap(norm_image, cv.COLORMAP_JET)

    # Convert the image to temperatures and print min and max.
    # Print the min temperature.
    cv.putText(
        gradient_image,
        f"Min: {temperature_image.min():.2f} C",
        (10, image.height - 75),
        cv.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        2,
    )
    # Print the max temperature.
    cv.putText(
        gradient_image,
        f"Max: {temperature_image.max():.2f} C",
        (10, image.height - 50),
        cv.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        2,
    )
    # Print the inspected max temperature.
    if inspected_max:
        cv.putText(
            gradient_image,
            f"Inspected Max: {inspected_max:.2f} C",
            (10, image.height - 25),
            cv.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            2,
        )

    return gradient_image


def show_numpy_image(image: np.ndarray, title: str) -> None:
    """
    Show the numpy image in a new window.
    :param image: Image to show
    :param title: Title of the window.
    :return: None
    """
    # Show the image and wait for user interaction.
    cv.imshow(title, image)
    logging.info("Showing image. Press any key to continue.")
    cv.waitKey(0)
    cv.destroyAllWindows()


def show_image(image: api.Image, title: str) -> None:
    """
    Show an image.
    :param image: Image.
    :param title: Title of the window.
    :return: None
    """
    np_image = convert_image_to_numpy(image)
    show_numpy_image(np_image, title)


def show_thermal_image(
    thermal_image: api.ThermalImage,
    title: str,
    inspected_max: Optional[float] = None,
) -> None:
    """
    Show a thermal image with annotated min and max temperature.
    :param thermal_image: Thermal image.
    :param title: Title of the window.
    :param inspected_max: Max temperature detected by the onboard inspection.
    :return: None
    """
    temperature_image = convert_thermal_image_to_numpy(thermal_image)
    gradient_image = convert_thermal_image_to_opencv_with_legend(thermal_image, temperature_image, inspected_max)
    show_numpy_image(gradient_image, title)

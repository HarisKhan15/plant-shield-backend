from .CNN import CNN
from .image_detection import *

__all__ = ['CNN']

cnn_functions = [name for name in dir() if callable(eval(name)) and not name.startswith("__")]
__all__.extend(cnn_functions)

image_detection_functions = [name for name in dir() if callable(eval(name)) and not name.startswith("__")]
__all__.extend(image_detection_functions)
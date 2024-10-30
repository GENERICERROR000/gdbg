import os
import sys


class Resources:

    if hasattr(sys, '_MEIPASS'):
        path = os.path.join(
            getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "resources"
        )
    else:
        path = os.path.join(
            os.path.abspath("."), "resources"
        )

    @classmethod
    def get(cls, file):
        return os.path.join(cls.path, file)

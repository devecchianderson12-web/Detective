# Semántica de Python 2 que el código original da por sentada.
import numpy


def div(a, b):
    # "/" de Python 2: entero / entero = división entera (floor); si hay un float, división real
    if isinstance(a, (int, numpy.integer)) and isinstance(b, (int, numpy.integer)):
        return a // b
    if isinstance(a, numpy.ndarray) and a.dtype.kind in 'iub' and isinstance(b, (int, numpy.integer)):
        return a // b
    return a / b

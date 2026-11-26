

def __load():
    import imp, os, sys
    try:
        dirname = os.path.dirname(__loader__.archive)
    except NameError:
        dirname = sys.prefix

    path = os.path.join(dirname, 'game.stages.racer.pyd')
    mod = imp.load_dynamic(__name__, path)
    return


__load()
del __load

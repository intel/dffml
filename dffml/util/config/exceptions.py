# TODO modify config_get to raise an error if NoDefaultValue would be the return
# value of config_get
class NoDefaultValue:
    pass


class ParameterNotInDocString(Exception):
    """
    Raised when a numpy class has a parameter in its ``__init__`` which was not
    present in it's docstring. Therefore we have no typing information for it.
    """

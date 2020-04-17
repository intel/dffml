class CannotRemoveContainer(Exception):
    """
    Raised when `docker rm -f CONTAINER` fails to
    stop and remove the container
    """
class CannotRemoveContainer(Exception):
    """
    Raised when `docker rm -f CONTAINER` fails to
    stop and remove the container
    """


class UsageNotFound(Exception):
    """
    Raised when docker file does not have `docker run`
    command in comments
    """

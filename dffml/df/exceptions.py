class DefinitionNotFoundInDataFlow(Exception):
    pass


class OperationAlreadyPresent(Exception):
    pass


class ContextNotPresent(Exception):
    pass


class DefinitionNotInContext(Exception):
    pass


class NotOpImp(Exception):
    pass


class InputValidationError(Exception):
    pass


class ValidatorMissing(Exception):
    pass


class MultipleAncestorsFoundError(NotImplementedError):
    pass

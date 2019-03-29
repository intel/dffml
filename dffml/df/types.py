import uuid
import itertools
from enum import Enum
from typing import NamedTuple, Union, List, Dict, Optional, Any, Iterator

from ..util.entrypoint import Entrypoint

class Definition(NamedTuple):
    '''
    List[type] is how to specify a list
    '''
    name: str
    primitive: str
    lock: bool = False

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)

    def export(self):
        exported = dict(self._asdict())
        del exported['name']
        if not self.lock:
            del exported['lock']
        return exported

class Stage(Enum):
    PROCESSING = 'processing'
    CLEANUP = 'cleanup'
    OUTPUT = 'output'

class Operation(NamedTuple, Entrypoint):
    name: str
    inputs: Dict[str, Definition]
    outputs: Dict[str, Definition]
    conditions: List[Definition]
    stage: Stage = Stage.PROCESSING
    expand: Union[bool, List[str]] = False

    ENTRYPOINT = 'dffml.operation'

    def export(self):
        exported = dict(self._asdict())
        del exported['name']
        for to_string in ['conditions']:
            exported[to_string] = list(map(lambda definition: definition.name,
                                           exported[to_string]))
        for to_string in ['inputs', 'outputs']:
            exported[to_string] = dict(map(lambda key_def: \
                                           (key_def[0], key_def[1].name),
                                           exported[to_string].items()))
        if not self.conditions:
            del exported['conditions']
        if not self.stage:
            del exported['stage']
        if not self.expand:
            del exported['expand']
        return exported

class Output(NamedTuple):
    name: str
    select: List[Definition]
    fill: Any
    single: bool = False
    ismap: bool = False

class Input(object):
    '''
    All inputs have a unique id. Without it they can't be tracked for locking
    purposes.
    '''

    def __init__(self,
                 value: Any,
                 definition: Definition,
                 parents: List['Input'],
                 *,
                 uid: Optional[str] = ''):
        self.value = value
        self.definition = definition
        self.parents = parents
        self.uid = uid
        if not self.uid:
            self.uid = str(uuid.uuid4())
        # Must explictly set parents to False to get an empty list of parents
        if parents == False:
            self.parents = []

    def get_parents(self) -> Iterator['Input']:
        return itertools.chain(*[[item] + list(item.get_parents()) \
                                 for item in self.parents])

    def __repr__(self):
        return '%s: %s' % (self.definition.name, self.value)

    def __str__(self):
        return repr(self)

class Parameter(NamedTuple):
    key: str
    value: Any
    origin: Input
    definition: Definition

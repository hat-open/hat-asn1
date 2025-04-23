from collections.abc import Collection
import abc
import enum
import pathlib
import typing

from hat import json
from hat import util


# type ########################################################################

class ClassType(enum.Enum):
    UNIVERSAL = 0
    APPLICATION = 1
    CONTEXT_SPECIFIC = 2
    PRIVATE = 3


class TypeProperty(typing.NamedTuple):
    name: str | None
    type: 'Type'
    optional: bool


class TypeRef(typing.NamedTuple):
    module: str
    name: str


class BooleanType(typing.NamedTuple):
    pass


class IntegerType(typing.NamedTuple):
    pass


class BitStringType(typing.NamedTuple):
    pass


class OctetStringType(typing.NamedTuple):
    pass


class NullType(typing.NamedTuple):
    pass


class ObjectIdentifierType(typing.NamedTuple):
    pass


class StringType(enum.Enum):
    ObjectDescriptor = 7
    UTF8String = 12
    NumericString = 18
    PrintableString = 19
    T61String = 20
    VideotexString = 21
    IA5String = 22
    UTCTime = 23
    GeneralizedTime = 24
    GraphicString = 25
    VisibleString = 26
    GeneralString = 27
    UniversalString = 28
    CHARACTER_STRING = 29
    BMPString = 30


class ExternalType(typing.NamedTuple):
    pass


class RealType(typing.NamedTuple):
    pass


class EnumeratedType(typing.NamedTuple):
    pass


class EmbeddedPDVType(typing.NamedTuple):
    pass


class ChoiceType(typing.NamedTuple):
    choices: typing.Dict[str, 'Type']


class SetType(typing.NamedTuple):
    elements: Collection[TypeProperty]


class SetOfType(typing.NamedTuple):
    element_type: 'Type'


class SequenceType(typing.NamedTuple):
    elements: Collection[TypeProperty]


class SequenceOfType(typing.NamedTuple):
    element_type: 'Type'


class EntityType(typing.NamedTuple):
    pass


class UnsupportedType(typing.NamedTuple):
    pass


class PrefixedType(typing.NamedTuple):
    type: 'Type'
    class_type: ClassType
    tag_number: int
    implicit: bool


Type: typing.TypeAlias = (TypeRef |
                          BooleanType |
                          IntegerType |
                          BitStringType |
                          OctetStringType |
                          NullType |
                          ObjectIdentifierType |
                          StringType |
                          ExternalType |
                          RealType |
                          EnumeratedType |
                          EmbeddedPDVType |
                          ChoiceType |
                          SetType |
                          SetOfType |
                          SequenceType |
                          SequenceOfType |
                          EntityType |
                          UnsupportedType |
                          PrefixedType)


# value #######################################################################

Boolean: typing.TypeAlias = bool

Integer: typing.TypeAlias = int

BitString: typing.TypeAlias = Collection[bool]

OctetString: typing.TypeAlias = util.Bytes

Null: typing.TypeAlias = None

ObjectIdentifier: typing.TypeAlias = tuple[int, ...]

String: typing.TypeAlias = str

Real: typing.TypeAlias = float

Enumerated: typing.TypeAlias = int

Choice: typing.TypeAlias = typing.Tuple[str, 'Value']

Set: typing.TypeAlias = typing.Dict[str, 'Value']

SetOf: typing.TypeAlias = Collection['Value']

Sequence: typing.TypeAlias = typing.Dict[str, 'Value']

SequenceOf: typing.TypeAlias = Collection['Value']


class Entity(abc.ABC):
    """Encoding independent ASN.1 Entity"""


class External(typing.NamedTuple):
    """External data"""
    data: Entity | util.Bytes | Collection[bool]
    direct_ref: ObjectIdentifier | None
    indirect_ref: int | None


class EmbeddedPDV(typing.NamedTuple):
    """EmbeddedPDV"""
    syntax: (None |
             int |
             ObjectIdentifier |
             tuple[int, ObjectIdentifier] |
             tuple[ObjectIdentifier, ObjectIdentifier])
    data: util.Bytes


Value: typing.TypeAlias = (Boolean |
                           Integer |
                           BitString |
                           OctetString |
                           Null |
                           ObjectIdentifier |
                           String |
                           Real |
                           Enumerated |
                           Choice |
                           Set |
                           SetOf |
                           Sequence |
                           SequenceOf |
                           Entity |
                           External |
                           EmbeddedPDV)


# repository ##################################################################

Repository: typing.TypeAlias = dict[TypeRef, Type]


def create_repository(*args: pathlib.PurePath | str) -> Repository:
    """ASN.1 type definition repository.

    Repository can be initialized with multiple arguments, which can be
    instances of ``pathlib.PurePath`` or ``str``.

    If an argument is of type ``pathlib.PurePath``, and path points to file
    with a suffix '.asn', ASN.1 type definitions are decoded from the file.
    Otherwise, it is assumed that path points to a directory,
    which is recursively searched for ASN.1 definitions. All decoded types
    are added to the repository. Previously added type definitions with the
    same references are replaced.

    If an argument is of type ``str``, it represents ASN.1 type definitions.
    All decoded types are added to the repository. Previously added type
    definitions with the same references are replaced.

    """
    from hat.asn1 import parser

    repo = {}
    for arg in args:
        if isinstance(arg, pathlib.PurePath):
            paths = [arg] if arg.suffix == '.asn' else arg.rglob('*.asn')
            for path in paths:
                asn1_def = path.read_text(encoding='utf-8')
                ref_types = parser.parse(asn1_def)
                repo.update(ref_types)

        elif isinstance(arg, str):
            refs = parser.parse(arg)
            repo.update(refs)

        else:
            raise TypeError('invalid argument type')

    return repo


def repository_to_json(repo: Repository) -> json.Data:
    """Convert repository to JSON data"""
    return [[_type_to_json(k), _type_to_json(v)]
            for k, v in repo.items()]


def repository_from_json(data: json.Data) -> Repository:
    """Convert JSON data to repository"""
    return {_type_from_json(k): _type_from_json(v)
            for k, v in data}


# encoder #####################################################################

class Encoder(abc.ABC):
    """ASN1 Encoder"""

    @property
    @abc.abstractmethod
    def syntax_name(self) -> ObjectIdentifier:
        """Encoder syntax name"""

    def encode(self,
               t: Type,
               value: Value
               ) -> util.Bytes:
        """Encode value to data"""
        entity = self.encode_value(t, value)
        data = self.encode_entity(entity)
        return data

    def decode(self,
               t: Type,
               data: util.Bytes
               ) -> tuple[Value, util.Bytes]:
        """Decode value from data

        Returns value and remaining data.

        """
        entity, rest = self.decode_entity(data)
        value = self.decode_value(t, entity)
        return value, rest

    @abc.abstractmethod
    def encode_value(self,
                     t: Type,
                     value: Value
                     ) -> Entity:
        """Encode value to entity"""

    @abc.abstractmethod
    def decode_value(self,
                     t: Type,
                     entity: Entity
                     ) -> Value:
        """Decode value from entity"""

    @abc.abstractmethod
    def encode_entity(self,
                      entity: Entity
                      ) -> util.Bytes:
        """Encode entity to data"""

    @abc.abstractmethod
    def decode_entity(self,
                      data: util.Bytes
                      ) -> tuple[Entity, util.Bytes]:
        """Decode entity from data

        Returns entity and remaining data.

        """


# private #####################################################################

def _type_to_json(t):
    if isinstance(t, TypeRef):
        return ['TypeRef', t.module, t.name]

    if isinstance(t, BooleanType):
        return ['BooleanType']

    if isinstance(t, IntegerType):
        return ['IntegerType']

    if isinstance(t, BitStringType):
        return ['BitStringType']

    if isinstance(t, OctetStringType):
        return ['OctetStringType']

    if isinstance(t, ObjectIdentifierType):
        return ['ObjectIdentifierType']

    if isinstance(t, NullType):
        return ['NullType']

    if isinstance(t, StringType):
        return ['StringType', t.name]

    if isinstance(t, ExternalType):
        return ['ExternalType']

    if isinstance(t, RealType):
        return ['RealType']

    if isinstance(t, EnumeratedType):
        return ['EnumeratedType']

    if isinstance(t, EmbeddedPDVType):
        return ['EmbeddedPDVType']

    if isinstance(t, ChoiceType):
        return ['ChoiceType', [[k, _type_to_json(v)]
                               for k, v in t.choices.items()]]

    if isinstance(t, SetType):
        return ['SetType', [[i.name, _type_to_json(i.type), i.optional]
                            for i in t.elements]]

    if isinstance(t, SetOfType):
        return ['SetOfType', _type_to_json(t.element_type)]

    if isinstance(t, SequenceType):
        return ['SequenceType', [[i.name, _type_to_json(i.type), i.optional]
                                 for i in t.elements]]

    if isinstance(t, SequenceOfType):
        return ['SequenceOfType', _type_to_json(t.element_type)]

    if isinstance(t, EntityType):
        return ['EntityType']

    if isinstance(t, UnsupportedType):
        return ['UnsupportedType']

    if isinstance(t, PrefixedType):
        return ['PrefixedType', _type_to_json(t.type), t.class_type.name,
                t.tag_number, t.implicit]

    raise TypeError('invalid type definition')


def _type_from_json(data):
    if data[0] == 'TypeRef':
        return TypeRef(module=data[1],
                       name=data[2])

    if data[0] == 'BooleanType':
        return BooleanType()

    if data[0] == 'IntegerType':
        return IntegerType()

    if data[0] == 'BitStringType':
        return BitStringType()

    if data[0] == 'OctetStringType':
        return OctetStringType()

    if data[0] == 'NullType':
        return NullType()

    if data[0] == 'ObjectIdentifierType':
        return ObjectIdentifierType()

    if data[0] == 'StringType':
        return StringType[data[1]]

    if data[0] == 'ExternalType':
        return ExternalType()

    if data[0] == 'RealType':
        return RealType()

    if data[0] == 'EnumeratedType':
        return EnumeratedType()

    if data[0] == 'EmbeddedPDVType':
        return EmbeddedPDVType()

    if data[0] == 'ChoiceType':
        return ChoiceType({k: _type_from_json(v)
                           for k, v in data[1]})

    if data[0] == 'SetType':
        return SetType([TypeProperty(name=i[0],
                                     type=_type_from_json(i[1]),
                                     optional=i[2])
                        for i in data[1]])

    if data[0] == 'SetOfType':
        return SetOfType(_type_from_json(data[1]))

    if data[0] == 'SequenceType':
        return SequenceType([TypeProperty(name=i[0],
                                          type=_type_from_json(i[1]),
                                          optional=i[2])
                             for i in data[1]])

    if data[0] == 'SequenceOfType':
        return SequenceOfType(_type_from_json(data[1]))

    if data[0] == 'EntityType':
        return EntityType()

    if data[0] == 'UnsupportedType':
        return UnsupportedType()

    if data[0] == 'PrefixedType':
        return PrefixedType(type=_type_from_json(data[1]),
                            class_type=ClassType[data[2]],
                            tag_number=data[3],
                            implicit=data[4])

    raise ValueError('invalid data')

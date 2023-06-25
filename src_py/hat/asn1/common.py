import abc
import enum
import typing

from hat import json


Bytes = bytes | bytearray | memoryview


class ClassType(enum.Enum):
    UNIVERSAL = 0
    APPLICATION = 1
    CONTEXT_SPECIFIC = 2
    PRIVATE = 3


class TypeProperty(typing.NamedTuple):
    name: str
    type: 'Type'
    optional: bool = False


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
    choices: list[TypeProperty]


class SetType(typing.NamedTuple):
    elements: list[TypeProperty]


class SetOfType(typing.NamedTuple):
    type: 'Type'
    "elements type definition"


class SequenceType(typing.NamedTuple):
    elements: list[TypeProperty]


class SequenceOfType(typing.NamedTuple):
    type: 'Type'
    "elements type definition"


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
"""Type"""


Boolean: typing.TypeAlias = bool
"""Boolean"""


Integer: typing.TypeAlias = int
"""Integer"""


BitString: typing.TypeAlias = list[bool]
"""Bit string"""


OctetString: typing.TypeAlias = Bytes
"""Octet string"""


Null: typing.TypeAlias = None
"""Null"""


ObjectIdentifier: typing.TypeAlias = tuple[int, ...]
"""Object identifier"""


String: typing.TypeAlias = str
"""String"""


class External(typing.NamedTuple):
    data: typing.Union['Entity', Bytes, list[bool]]
    direct_ref: ObjectIdentifier | None
    indirect_ref: int | None


Real: typing.TypeAlias = float
"""Real"""


Enumerated: typing.TypeAlias = int
"""Enumerated"""


class EmbeddedPDV(typing.NamedTuple):
    """EmbeddedPDV

    If `abstract` is `ObjectIdentifier`, `transfer` must be defined

    """
    abstract: int | ObjectIdentifier | None
    transfer: ObjectIdentifier | None
    data: Bytes


Choice: typing.TypeAlias = typing.Tuple[str, 'Value']
"""Choice"""


Set: typing.TypeAlias = typing.Dict[str, 'Value']
"""Set"""


SetOf: typing.TypeAlias = typing.Iterable['Value']
"""Set of"""


Sequence: typing.TypeAlias = typing.Dict[str, 'Value']
"""Sequence"""


SequenceOf: typing.TypeAlias = typing.List['Value']
"""Sequence of"""


class Entity(abc.ABC):
    """Encoding independent ASN.1 Entity"""


Value: typing.TypeAlias = (Boolean |
                           Integer |
                           BitString |
                           OctetString |
                           Null |
                           ObjectIdentifier |
                           String |
                           External |
                           Real |
                           Enumerated |
                           EmbeddedPDV |
                           Choice |
                           Set |
                           SetOf |
                           Sequence |
                           SequenceOf |
                           Entity)
"""Value"""


def type_to_json(t: Type) -> json.Data:
    """Convert type definition to JSON data"""
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
        return ['ChoiceType', [[i.name, type_to_json(i.type)]
                               for i in t.choices]]

    if isinstance(t, SetType):
        return ['SetType', [[i.name, type_to_json(i.type), i.optional]
                            for i in t.elements]]

    if isinstance(t, SetOfType):
        return ['SetOfType', type_to_json(t.type)]

    if isinstance(t, SequenceType):
        return ['SequenceType', [[i.name, type_to_json(i.type), i.optional]
                                 for i in t.elements]]

    if isinstance(t, SequenceOfType):
        return ['SequenceOfType', type_to_json(t.type)]

    if isinstance(t, EntityType):
        return ['EntityType']

    if isinstance(t, UnsupportedType):
        return ['UnsupportedType']

    if isinstance(t, PrefixedType):
        return ['PrefixedType', type_to_json(t.type), t.class_type.name,
                t.tag_number, t.implicit]

    raise ValueError('invalid type definition')


def type_from_json(data: json.Data) -> Type:
    """Convert JSON data to type definition"""
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
        return ChoiceType([TypeProperty(name=i[0],
                                        type=type_from_json(i[1]))
                           for i in data[1]])

    if data[0] == 'SetType':
        return SetType([TypeProperty(name=i[0],
                                     type=type_from_json(i[1]),
                                     optional=i[2])
                        for i in data[1]])

    if data[0] == 'SetOfType':
        return SetOfType(type_from_json(data[1]))

    if data[0] == 'SequenceType':
        return SequenceType([TypeProperty(name=i[0],
                                          type=type_from_json(i[1]),
                                          optional=i[2])
                             for i in data[1]])

    if data[0] == 'SequenceOfType':
        return SequenceOfType(type_from_json(data[1]))

    if data[0] == 'EntityType':
        return EntityType()

    if data[0] == 'UnsupportedType':
        return UnsupportedType()

    if data[0] == 'PrefixedType':
        return PrefixedType(type=type_from_json(data[1]),
                            class_type=ClassType[data[2]],
                            tag_number=data[3],
                            implicit=data[4])

    raise ValueError('invalid data')

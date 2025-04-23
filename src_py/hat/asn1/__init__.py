"""Abstract Syntax Notation One

Value mapping
-------------

    +-----------------------+-------------------+
    | ASN.1 type            | Python type       |
    +=======================+===================+
    | Boolean               | bool              |
    +-----------------------+-------------------+
    | Integer               | int               |
    +-----------------------+-------------------+
    | BitString             | Collection[bool]  |
    +-----------------------+-------------------+
    | OctetString           | Bytes             |
    +-----------------------+-------------------+
    | Null                  | NoneType          |
    +-----------------------+-------------------+
    | ObjectIdentifier      | tuple[int, ...]   |
    +-----------------------+-------------------+
    | String                | str               |
    +-----------------------+-------------------+
    | Real                  | float             |
    +-----------------------+-------------------+
    | Enumerated            | int               |
    +-----------------------+-------------------+
    | Choice                | tuple[str, Value] |
    +-----------------------+-------------------+
    | Set                   | dict[str, Value]  |
    +-----------------------+-------------------+
    | SetOf                 | Collection[Value] |
    +-----------------------+-------------------+
    | Sequence              | dict[str, Value]  |
    +-----------------------+-------------------+
    | SequenceOf            | Collection[Value] |
    +-----------------------+-------------------+
    | ABSTRACT-SYNTAX.&Type | Entity            |
    +-----------------------+-------------------+
    | External              | External          |
    +-----------------------+-------------------+
    | EmbeddedPDV           | EmbeddedPDV       |
    +-----------------------+-------------------+

For Choice, Set and Sequence, `str` represents field name.

"""

from hat.asn1 import ber
from hat.asn1.common import (ClassType,
                             TypeProperty,
                             TypeRef,
                             BooleanType,
                             IntegerType,
                             BitStringType,
                             OctetStringType,
                             NullType,
                             ObjectIdentifierType,
                             StringType,
                             ExternalType,
                             RealType,
                             EnumeratedType,
                             EmbeddedPDVType,
                             ChoiceType,
                             SetType,
                             SetOfType,
                             SequenceType,
                             SequenceOfType,
                             EntityType,
                             UnsupportedType,
                             PrefixedType,
                             Type,
                             Boolean,
                             Integer,
                             BitString,
                             OctetString,
                             Null,
                             ObjectIdentifier,
                             String,
                             Real,
                             Enumerated,
                             Choice,
                             Set,
                             SetOf,
                             Sequence,
                             SequenceOf,
                             Entity,
                             External,
                             EmbeddedPDV,
                             Value,
                             Repository,
                             create_repository,
                             repository_to_json,
                             repository_from_json,
                             Encoder)
from hat.asn1.doc import generate_html_doc


__all__ = ['ber',
           'ClassType',
           'TypeProperty',
           'TypeRef',
           'BooleanType',
           'IntegerType',
           'BitStringType',
           'OctetStringType',
           'NullType',
           'ObjectIdentifierType',
           'StringType',
           'ExternalType',
           'RealType',
           'EnumeratedType',
           'EmbeddedPDVType',
           'ChoiceType',
           'SetType',
           'SetOfType',
           'SequenceType',
           'SequenceOfType',
           'EntityType',
           'UnsupportedType',
           'PrefixedType',
           'Type',
           'Boolean',
           'Integer',
           'BitString',
           'OctetString',
           'Null',
           'ObjectIdentifier',
           'String',
           'Real',
           'Enumerated',
           'Choice',
           'Set',
           'SetOf',
           'Sequence',
           'SequenceOf',
           'Entity',
           'External',
           'EmbeddedPDV',
           'Value',
           'Repository',
           'create_repository',
           'repository_to_json',
           'repository_from_json',
           'Encoder',
           'generate_html_doc']

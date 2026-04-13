`hat.asn1` - Python Abstract Syntax Notation One library
========================================================

This library provides implementation of
`ASN.1 <https://en.wikipedia.org/wiki/ASN.1>`_ schema parser and
`BER <https://en.wikipedia.org/wiki/X.690#BER_encoding>`_ encoder/decoder.
Additionally, HTML documentation of parsed ASN.1 schemas can be generated.


Python data mappings
--------------------

Mapping between ASN.1 data types and built in types:

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

According to previous mapping, this library defines following types::

    Value = (Boolean |
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

    Boolean = bool
    Integer = int
    BitString = Collection[bool]
    OctetString = Bytes
    Null = None
    ObjectIdentifier = tuple[int, ...]
    String = str
    Real = float
    Enumerated = int
    Choice = tuple[str, Value]
    Set = dict[str, Value]
    SetOf = Collection[Value]
    Sequence = dict[str, Value]
    SequenceOf = Collection[Value]

    class Entity(abc.ABC):
        """Encoding independent ASN.1 Entity"""

    class External(typing.NamedTuple):
        data: Entity | Bytes | Collection[bool]
        direct_ref: ObjectIdentifier | None
        indirect_ref: int | None

    class EmbeddedPDV(typing.NamedTuple):
        syntax: (None |
                 int |
                 ObjectIdentifier |
                 tuple[int, ObjectIdentifier] |
                 tuple[ObjectIdentifier, ObjectIdentifier])
        data: Data


Repository
----------

`hat.asn1.Repository` is collection of references to ASN.1 type definitions.
It can created by parsing ASN.1 schemas. ASN.1 data definitions are required
for encoding/decoding ASN.1 data. `hat.asn1.Repository` can be
represented as JSON data enabling efficient storage and reconstruction of ASN.1
type definitions without repetitive parsing of ASN.1 schemas.

::
    Repository = dict[TypeRef, Type]

    def create_repository(*args: pathlib.PurePath | str) -> Repository: ...

    def repository_to_json(repo: Repository) -> json.Data: ...

    def repository_from_json(data: json.Data) -> Repository: ...

def repository_from_json(data: json.Data) -> Repository:

Once instance of `hat.asn1.Repository` is created, HTML documentation
describing data structures can be generated with `generate_html_doc` method.


Encoder
-------

`hat.asn1.Encoder` provides interface for encoding/decoding ASN.1 data
based on ASN.1 data definitions (`hat.asn1.Repository`)::

    class Encoder:

        @property
        def syntax_name(self) -> ObjectIdentifier: ...

        def encode(self,
                   t: Type,
                   value: Value
                   ) -> util.Bytes: ...

        def decode(self,
                   t: Type,
                   data: util.Bytes
                   ) -> tuple[Value, util.Bytes]: ...

        def encode_value(self,
                         t: Type,
                         value: Value
                         ) -> Entity: ...

        def decode_value(self,
                         t: Type,
                         entity: Entity
                         ) -> Value: ...

        def encode_entity(self,
                          entity: Entity
                          ) -> util.Bytes: ...

        def decode_entity(self,
                          data: util.Bytes
                          ) -> tuple[Entity, util.Bytes]: ...


Example
-------

::

    repo = asn1.create_repository(r"""
        Example DEFINITIONS ::= BEGIN
            T ::= SEQUENCE OF CHOICE {
                a BOOLEAN,
                b INTEGER,
                c UTF8String
            }
        END
    """)

    encoder = asn1.ber.BerEncoder(repo)

    ref = asn1.TypeRef('Example', 'T')
    value = [('c', '123'), ('a', True), ('a', False), ('b', 123)]

    encoded = encoder.encode(ref, value)
    decoded, rest = encoder.decode(ref, encoded)

    assert value == decoded
    assert len(rest) == 0


API
---

API reference is available as part of generated documentation:

    * `Python hat.asn1 module <py_api/hat/asn1/index.html>`_

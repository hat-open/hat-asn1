from pathlib import Path

import pytest

from hat import asn1


def entity_equal(x, y):
    if isinstance(x, asn1.ber.Entity) and isinstance(y, asn1.ber.Entity):
        if x.class_type != y.class_type:
            return False

        if x.tag_number != y.tag_number:
            return False

        if (isinstance(x.content, asn1.ber.PrimitiveContent) and
                isinstance(y.content, asn1.ber.PrimitiveContent)):
            return x.content.value == y.content.value

        if (isinstance(x.content, asn1.ber.ConstructedContent) and
                isinstance(y.content, asn1.ber.ConstructedContent)):
            if len(x.content.elements) != len(y.content.elements):
                return False

            return all(entity_equal(a, b)
                       for a, b in zip(x.content.elements, y.content.elements))

        return False

    return False


def test_create_repository_file(tmpdir):
    directory = tmpdir.mkdir("schemas_asn1")
    file1 = directory.join("schema1.asn")
    file1.write("""
        Def1 DEFINITIONS ::= BEGIN
            T1 ::= BOOLEAN
        END
    """)
    file2 = directory.join("schema2.asn")
    file2.write("""
        Def2 DEFINITIONS ::= BEGIN
            T1 ::= BOOLEAN
        END
    """)

    repository = asn1.create_repository(Path(directory))

    assert repository == {asn1.TypeRef('Def1', 'T1'): asn1.BooleanType(),
                          asn1.TypeRef('Def2', 'T1'): asn1.BooleanType()}


def test_create_repository_str():
    base = """
        Base DEFINITIONS ::= BEGIN
            T1 ::= BOOLEAN
        END"""

    derived = """
        Derived DEFINITIONS ::= BEGIN
            T1 ::= SEQUENCE OF Base.T1
        END
        """

    repository = asn1.create_repository(base, derived)

    assert repository == {
        asn1.TypeRef('Base', 'T1'): asn1.BooleanType(),
        asn1.TypeRef('Derived', 'T1'): asn1.SequenceOfType(
            asn1.TypeRef('Base', 'T1'))}


@pytest.mark.parametrize('repo', [
    {},

    {asn1.TypeRef('M1', 'T1'): asn1.TypeRef('M2', 'T2')},

    {asn1.TypeRef('M', f'T{i}'): cls()
     for i, cls in enumerate([asn1.BooleanType,
                              asn1.IntegerType,
                              asn1.BitStringType,
                              asn1.OctetStringType,
                              asn1.NullType,
                              asn1.ObjectIdentifierType,
                              asn1.ExternalType,
                              asn1.RealType,
                              asn1.EnumeratedType,
                              asn1.EmbeddedPDVType,
                              asn1.EntityType,
                              asn1.UnsupportedType])},

    {asn1.TypeRef('M1', f'T{i}'): t
     for i, t in enumerate(asn1.StringType)},

    {asn1.TypeRef('M', 'T1'): asn1.ChoiceType({'a': asn1.BooleanType()}),
     asn1.TypeRef('M', 'T2'): asn1.SetType([
        asn1.TypeProperty('a', asn1.BooleanType(), False),
        asn1.TypeProperty(None, asn1.SetType([]), True)]),
     asn1.TypeRef('M', 'T3'): asn1.SetOfType(asn1.BooleanType()),
     asn1.TypeRef('M', 'T4'): asn1.SequenceType([
        asn1.TypeProperty('a', asn1.BooleanType(), False),
        asn1.TypeProperty(None, asn1.SequenceType([]), True)]),
     asn1.TypeRef('M', 'T5'): asn1.SequenceOfType(asn1.BooleanType())},

    {asn1.TypeRef('M', f'T{i}'): asn1.PrefixedType(type=asn1.BooleanType(),
                                                   class_type=ct,
                                                   tag_number=i,
                                                   implicit=bool(i % 2))
     for i, ct in enumerate(asn1.ClassType)}
])
def test_repository_to_from_json(repo):
    repo_json = asn1.repository_to_json(repo)
    result = asn1.repository_from_json(repo_json)

    assert result == repo


@pytest.mark.parametrize('asn1_def, repo', [
    ("""
        Abc DEFINITIONS ::= BEGIN
        END""",
     {}),

    ("""
        Abc DEFINITIONS ::= BEGIN
            T1 ::= BOOLEAN
        END""",
     {asn1.TypeRef('Abc', 'T1'): asn1.BooleanType()}),

    ("""
        Abc DEFINITIONS ::= BEGIN
            T1 ::= ENUMERATED {
                red         (0),
                green       (1),
                blue        (2)
            }
        END""",
     {asn1.TypeRef('Abc', 'T1'): asn1.EnumeratedType()}),

    ("""
        Abc DEFINITIONS ::= BEGIN
            T1 ::= SET {
                item1 [0]                      INTEGER OPTIONAL,
                item2 [1]                      UTF8String,
                item3 [APPLICATION 1] IMPLICIT UTF8String
            }
        END""",
     {asn1.TypeRef('Abc', 'T1'): asn1.SetType([
        asn1.TypeProperty(
            'item1',
            asn1.PrefixedType(type=asn1.IntegerType(),
                              class_type=asn1.ClassType.CONTEXT_SPECIFIC,
                              tag_number=0,
                              implicit=False),
            True),
        asn1.TypeProperty(
            'item2',
            asn1.PrefixedType(type=asn1.StringType.UTF8String,
                              class_type=asn1.ClassType.CONTEXT_SPECIFIC,
                              tag_number=1,
                              implicit=False),
            False),
        asn1.TypeProperty(
            'item3',
            asn1.PrefixedType(type=asn1.StringType.UTF8String,
                              class_type=asn1.ClassType.APPLICATION,
                              tag_number=1,
                              implicit=True),
            False)])})
])
def test_parse(asn1_def, repo):
    result = asn1.create_repository(asn1_def)
    assert result == repo


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('asn1_def', ["""
    Module DEFINITIONS ::= BEGIN
        T1 ::= BOOLEAN
        T2 ::= INTEGER
        T3 ::= BIT STRING
        T4 ::= OCTET STRING
        T5 ::= NULL
        T6 ::= OBJECT IDENTIFIER
        T7 ::= UTF8String
        T8 ::= ENUMERATED {
            red     (0),
            green   (1),
            blue    (2)
        }
        T9 ::= EMBEDDED PDV
    END
"""], ids=[''])
@pytest.mark.parametrize('name, value', [
    ('T1', True),
    ('T2', 10),
    ('T3', [True, True, False, True]),
    ('T4', b'0123'),
    ('T5', None),
    ('T6', (1, 5, 3)),
    ('T6', (1, 5, 3, 7, 9, 2)),
    ('T6', (1, 0)),
    ('T6', (2, 3, 1)),
    ('T6', (0, 0)),
    ('T7', 'Foo bar'),
    ('T8', 1),
    ('T9', asn1.EmbeddedPDV(None, b'0123')),
])
def test_serialization(encoder_cls, asn1_def, name, value):
    repo = asn1.create_repository(asn1_def)
    encoder = encoder_cls(repo)

    ref = asn1.TypeRef('Module', name)
    encoded_value = encoder.encode(ref, value)
    decoded_value, remainder = encoder.decode(ref, encoded_value)

    assert value == decoded_value
    assert len(remainder) == 0


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('asn1_def', ["""
    Module DEFINITIONS ::= BEGIN
        T1 ::= CHOICE {
            item1   INTEGER,
            item2   BIT STRING,
            item3   NULL
        }
        T2 ::= SET {
            item1   BOOLEAN,
            item2   INTEGER,
            item3   BIT STRING
        }
        T3 ::= SET OF INTEGER
        T4 ::= SEQUENCE {
            item1   OCTET STRING,
            item2   NULL,
            item3   OBJECT IDENTIFIER
        }
        T5 ::= SEQUENCE OF INTEGER
        T6 ::= SET {
            item1   [APPLICATION 0] IMPLICIT UTF8String,
            item2   [APPLICATION 1] IMPLICIT ENUMERATED {
                red     (0),
                green   (1),
                blue    (2)
            },
            item3   [APPLICATION 2] IMPLICIT EMBEDDED PDV
        }
        T7 ::= SET {
            item1   [0] BOOLEAN,
            item2   [1] EXTERNAL,
            item3   [2] INTEGER
        }

        T8 ::= SET {
            item1   T4,
            item2   T6 OPTIONAL
        }
    END
"""])
@pytest.mark.parametrize('name, value', [
    ('T1', ('item2', [True, False, True])),
    ('T2', {'item1': True, 'item2': 100, 'item3': [True, False, True]}),
    ('T3', [1, 2, 3, 4]),
    ('T4', {'item1': b'0123', 'item2': None, 'item3': (1, 2, 3)}),
    ('T5', [1, 2, 3, 4]),
    ('T6', {'item1': 'foo', 'item2': 0,
            'item3': asn1.EmbeddedPDV(None, b'0')}),
    ('T7', {'item1': True,
            'item2': asn1.External(b'0123', None, None),
            'item3': 12}),
    ('T8', {'item1': {'item1': b'0123', 'item2': None, 'item3': (1, 2, 3)},
            'item2': {'item1': 'foo', 'item2': 0,
                      'item3': asn1.EmbeddedPDV(None, b'0')}}),
    ('T8', {'item1': {'item1': b'0123', 'item2': None, 'item3': (1, 2, 3)}}),
])
def test_serialization_composite(encoder_cls, asn1_def, name, value):
    repo = asn1.create_repository(asn1_def)
    encoder = encoder_cls(repo)

    ref = asn1.TypeRef('Module', name)
    encoded_value = encoder.encode(ref, value)
    decoded_value, remainder = encoder.decode(ref, encoded_value)

    assert value == decoded_value
    assert len(remainder) == 0


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('sequence_size', [1, 20, 50])
def test_serialization_entity(encoder_cls, sequence_size):
    sequence_items = ', '.join([f'item{n} [APPLICATION {n}] OCTET STRING'
                                for n in range(sequence_size)])
    sequence_items = '{' + sequence_items + '}'
    definition = f"""
    Module DEFINITIONS ::= BEGIN
        T1 ::= ABSTRACT-SYNTAX.&Type
        T2 ::= SEQUENCE {sequence_items}
    END"""
    repo = asn1.create_repository(definition)
    encoder = encoder_cls(repo)

    ref_t1 = asn1.TypeRef('Module', 'T1')
    ref_t2 = asn1.TypeRef('Module', 'T2')

    value = {f'item{n}': b'0123' for n in range(sequence_size)}
    entity = encoder.encode_value(ref_t2, value)

    encoded = encoder.encode(ref_t1, entity)
    decoded_entity, rest = encoder.decode(ref_t1, encoded)
    assert entity_equal(decoded_entity, entity)
    assert len(rest) == 0

    decoded_value = encoder.decode_value(ref_t2, decoded_entity)
    assert decoded_value == value


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('data_type', ["entity", "bytes", "bitstring"])
@pytest.mark.parametrize('direct_ref', [None, (1, 5, 2, 3, 8)])
@pytest.mark.parametrize('indirect_ref', [None, 11])
def test_serialization_external(encoder_cls, data_type, direct_ref,
                                indirect_ref):
    repo = asn1.create_repository("""
        Module DEFINITIONS ::= BEGIN
            T1 ::= EXTERNAL
            T2 ::= BIT STRING
        END""")
    encoder = encoder_cls(repo)

    ref_t1 = asn1.TypeRef('Module', 'T1')
    ref_t2 = asn1.TypeRef('Module', 'T2')

    bits = [True, False, False, True]
    data = {
        'entity': encoder.encode_value(ref_t2, bits),
        'bytes': encoder.encode(ref_t2, bits),
        'bitstring': bits
    }[data_type]

    external = asn1.External(data=data,
                             direct_ref=direct_ref,
                             indirect_ref=indirect_ref)
    encoded = encoder.encode(ref_t1, external)
    decoded, rest = encoder.decode(ref_t1, encoded)
    assert decoded == external
    assert len(rest) == 0


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('syntax', [None,
                                    5,
                                    (1, 3, 8),
                                    (1, (1, 3, 9)),
                                    ((1, 3, 10), (1, 3, 11))])
def test_serialization_embedded_pdv(encoder_cls, syntax):
    repo = asn1.create_repository("""
        Module DEFINITIONS ::= BEGIN
            T1 ::= EMBEDDED PDV
            T2 ::= SEQUENCE OF INTEGER
        END""")
    encoder = encoder_cls(repo)

    ref_t1 = asn1.TypeRef('Module', 'T1')
    ref_t2 = asn1.TypeRef('Module', 'T2')

    data = encoder.encode(ref_t2, [1, 2, 3, 9, 8, 7])

    embedded_pdv = asn1.EmbeddedPDV(syntax=syntax,
                                    data=data)
    encoded = encoder.encode(ref_t1, embedded_pdv)
    decoded, rest = encoder.decode(ref_t1, encoded)
    assert decoded == embedded_pdv
    assert len(rest) == 0


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('asn1_def', ["""
    Module DEFINITIONS ::= BEGIN
        T1 ::= REAL
    END
"""])
@pytest.mark.parametrize('name, value', [
    ('T1', 10.5)
])
def test_serialization_not_supported(encoder_cls, asn1_def, name, value):
    repo = asn1.create_repository(asn1_def)
    encoder = encoder_cls(repo)

    ref = asn1.TypeRef('Module', name)

    with pytest.raises(NotImplementedError):
        encoder.encode(ref, value)


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
@pytest.mark.parametrize('asn1_def', ["""
    Module DEFINITIONS ::= BEGIN
        T1 ::= CHOICE {
            item1   INTEGER,
            item2   BOOLEAN,
            item3   BIT STRING
        }
        T2 ::= CHOICE {
            item1   INTEGER,
            item2   BOOLEAN
        }
        T3 ::= SET {
            item1   INTEGER,
            item2   BOOLEAN
        }
        T4 ::= SET {
            item1   INTEGER,
            item2   BOOLEAN,
            item3   BIT STRING
        }
        T5 ::= SEQUENCE {
            item1   INTEGER,
            item2   BOOLEAN
        }
        T6 ::= SEQUENCE {
            item1   INTEGER,
            item2   BOOLEAN,
            item3   BIT STRING
        }
        T7 ::= SEQUENCE {
            item1   INTEGER,
            item2   BOOLEAN,
            xyz     UTF8String
        }
        T8 ::= SEQUENCE {
            item1   INTEGER,
            item2   BOOLEAN,
            item3   BIT STRING
        }
    END
"""], ids=[""])
@pytest.mark.parametrize('value, serialize_name, deserialize_name', [
    (('item3', [True, False]), 'T1', 'T2'),
    ({'item1': 1, 'item2': True}, 'T3', 'T4'),
    ({'item1': 1, 'item2': True}, 'T5', 'T6'),
    ({'item1': 1, 'item2': True, 'xyz': 'abc'}, 'T7', 'T8'),
])
def test_invalid_serialization(encoder_cls, asn1_def, value, serialize_name,
                               deserialize_name):
    repo = asn1.create_repository(asn1_def)
    encoder = encoder_cls(repo)

    ref_serialize = asn1.TypeRef('Module', serialize_name)
    ref_deserialize = asn1.TypeRef('Module', deserialize_name)

    encoded_value = encoder.encode(ref_serialize, value)
    with pytest.raises(Exception):
        encoder.decode(ref_deserialize, encoded_value)


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
def test_constructed_as_octet_and_utf8_string(encoder_cls):
    repo = asn1.create_repository("""
        Module DEFINITIONS ::= BEGIN
            T1 ::= SEQUENCE OF OCTET STRING
            T2 ::= OCTET STRING
            T3 ::= UTF8String
        END""")
    encoder = encoder_cls(repo)

    ref_t1 = asn1.TypeRef('Module', 'T1')
    ref_t2 = asn1.TypeRef('Module', 'T2')
    ref_t3 = asn1.TypeRef('Module', 'T3')

    entity = encoder.encode_value(ref_t1, [b'foo', b'bar'])
    assert encoder.decode_value(ref_t2, entity) == b'foobar'
    assert encoder.decode_value(ref_t3, entity) == 'foobar'


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
def test_constructed_as_bit_string(encoder_cls):
    repo = asn1.create_repository("""
        Module DEFINITIONS ::= BEGIN
            T1 ::= SEQUENCE OF OCTET STRING
            T2 ::= BIT STRING
        END""")
    encoder = encoder_cls(repo)
    ref_t1 = asn1.TypeRef('Module', 'T1')
    ref_t2 = asn1.TypeRef('Module', 'T2')

    entity = encoder.encode_value(
        ref_t1, [bytes([0, 5]), bytes([0, 15])])
    assert list(encoder.decode_value(ref_t2, entity)) == (
        [False, False, False, False, False, True, False, True] +
        [False, False, False, False, True, True, True, True])


@pytest.mark.parametrize('encoder_cls', [asn1.ber.BerEncoder])
def test_components_of(encoder_cls):
    repo = asn1.create_repository("""
        Module DEFINITIONS ::= BEGIN
            T1 ::= SEQUENCE {
                ...,
                COMPONENTS OF [0] T2
            }
            T2 ::= SEQUENCE {
                a INTEGER
            }
        END""")
    encoder = encoder_cls(repo)

    ref_t1 = asn1.TypeRef('Module', 'T1')
    value = {'a': 123}

    encoded = encoder.encode(ref_t1, value)
    decoded, rest = encoder.decode(ref_t1, encoded)
    assert decoded == value
    assert len(rest) == 0


def test_example_docs():
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

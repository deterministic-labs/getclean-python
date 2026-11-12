# Part of the generated SDK of the getclean API; do not edit.

from getclean.core.query_encoder import encode_query


def test_query_encoding_deep_objects() -> None:
    assert encode_query({"hello world": "hello world"}) == [("hello world", "hello world")]
    assert encode_query({"hello_world": {"hello": "world"}}) == [("hello_world[hello]", "world")]
    assert encode_query({"hello_world": {"hello": {"world": "today"}, "test": "this"}, "hi": "there"}) == [
        ("hello_world[hello][world]", "today"),
        ("hello_world[test]", "this"),
        ("hi", "there"),
    ]


def test_query_encoding_deep_object_arrays() -> None:
    assert encode_query({"objects": [{"key": "hello", "value": "world"}, {"key": "foo", "value": "bar"}]}) == [
        ("objects[key]", "hello"),
        ("objects[value]", "world"),
        ("objects[key]", "foo"),
        ("objects[value]", "bar"),
    ]
    assert encode_query(
        {"users": [{"name": "string", "tags": ["string"]}, {"name": "string2", "tags": ["string2", "string3"]}]}
    ) == [
        ("users[name]", "string"),
        ("users[tags]", "string"),
        ("users[name]", "string2"),
        ("users[tags]", "string2"),
        ("users[tags]", "string3"),
    ]


def test_encode_query_with_none() -> None:
    encoded = encode_query(None)
    assert encoded is None


def test_an_empty_list_is_the_key_with_an_empty_value() -> None:
    # The wire form of an empty list on a query parameter: the key sent once with an empty value (`formats=`), never
    # dropped (the server's default would apply) and never refused by the client (the server's rule, not the client's).
    assert encode_query({"formats": []}) == [("formats", "")]
    assert encode_query({"filter": {"kinds": []}}) == [("filter[kinds]", "")]
    assert encode_query({"formats": ["markdown"]}) == [("formats", "markdown")]

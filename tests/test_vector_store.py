from app.storage.vector.vector_store import to_vector_literal


def test_vector_literal_format():
    assert to_vector_literal([0.1, 0.2, 0.3]) == "[0.1,0.2,0.3]"


def test_vector_literal_casts_to_float():
    assert to_vector_literal([1, 2]) == "[1.0,2.0]"


def test_vector_literal_empty():
    assert to_vector_literal([]) == "[]"

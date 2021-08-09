import pytest


def test_searches_responses_fielded_response_init():
    from snosearch.responses import FieldedResponse
    fr = FieldedResponse()
    assert isinstance(fr, FieldedResponse)


def test_searches_responses_fielded_response_validate_response_fields():
    from snosearch.responses import FieldedResponse
    from snosearch.fields import ResponseField
    rf = ResponseField()
    FieldedResponse(response_fields=[rf])
    class NewResponseField(ResponseField):
        def __init__(self):
            super().__init__()
    nrf = NewResponseField()
    FieldedResponse(response_fields=[rf, nrf])
    class OtherResponseField():
        pass
    orf = OtherResponseField()
    with pytest.raises(ValueError):
        FieldedResponse(response_fields=[rf, nrf, orf])


def test_searches_responses_fielded_response_ordered_response():
    from collections import OrderedDict
    from snosearch.responses import FieldedResponse
    fr = FieldedResponse()
    fr.response = {'b': 2, 'a': 1}
    ordered_dict = OrderedDict([('a', 1), ('b', 2)])
    for item1, item2 in zip(fr.ordered_response.items(), ordered_dict.items()):
        assert item1 == item2


def test_searches_responses_fielded_response_get_request(dummy_request):
    from snosearch.responses import FieldedResponse
    from snosearch.parsers import ParamsParser
    fr = FieldedResponse()
    assert fr.get_request() is None
    dummy_request.body = b'abc'
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    request = fr.get_request()
    assert request
    assert request.body == b'abc'


def test_searches_responses_fielded_response_get_or_create_response(dummy_request):
    from snosearch.responses import FieldedResponse
    from snosearch.parsers import ParamsParser
    from pyramid.response import Response
    fr = FieldedResponse()
    response = fr.get_or_create_response()
    assert isinstance(response, Response)
    dummy_request.response.body = b'abc'
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    response = fr.get_or_create_response()
    assert response.body == b'abc'


def test_searches_responses_fielded_response_is_request_from_embed(dummy_request):
    from snosearch.responses import FieldedResponse
    from snosearch.parsers import ParamsParser
    fr = FieldedResponse()
    assert not fr._is_request_from_embed()
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert not fr._is_request_from_embed()
    dummy_request.__parent__ = 'something'
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert fr._is_request_from_embed()


def test_searches_responses_fielded_response_is_response_with_generator(dummy_request):
    from snosearch.responses import FieldedResponse
    fr = FieldedResponse()
    assert not fr._is_response_with_generator()
    fr.response = {'a': [1, 2, 3]}
    assert not fr._is_response_with_generator()
    fr.response = {'a': (x for x in [1, 2, 3])}
    assert fr._is_response_with_generator()
    fr.response = {'a': (x for x in [1, 2, 3]), 'b': 1}
    assert fr._is_response_with_generator()


def test_searches_responses_fielded_response_should_stream_response(dummy_request):
    from snosearch.responses import FieldedResponse
    from snosearch.parsers import ParamsParser
    fr = FieldedResponse()
    assert not fr._should_stream_response()
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert not fr._should_stream_response()
    fr.response = {'a': (x for x in [1, 2, 3])}
    assert fr._should_stream_response()
    dummy_request.__parent__ = 'something'
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert not fr._should_stream_response()
    fr.response = {'a': (x for x in [1, 2, 3])}
    assert not fr._should_stream_response()


def test_searches_responses_fielded_response_response_factory(dummy_request):
    from snosearch.responses import FieldedResponse
    from snosearch.responses import InMemoryResponse
    from snosearch.responses import StreamedResponse
    from snosearch.parsers import ParamsParser
    fr = FieldedResponse()
    fr.response = {'a': 1}
    assert isinstance(fr._response_factory(), InMemoryResponse)
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert isinstance(fr._response_factory(), InMemoryResponse)
    fr.response = {'a': (x for x in [1, 2, 3])}
    assert isinstance(fr._response_factory(), StreamedResponse)
    dummy_request.__parent__ = 'something'
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert isinstance(fr._response_factory(), InMemoryResponse)
    fr.response = {'a': (x for x in [1, 2, 3])}
    assert isinstance(fr._response_factory(), InMemoryResponse)


def test_searches_responses_fielded_response_render(dummy_request):
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    from snosearch.parsers import ParamsParser
    from pyramid.response import Response
    fr = FieldedResponse()
    fr.response = {'a': 1}
    response = fr.render()
    assert isinstance(response, dict)
    fr.response = {'a': (x for x in [1, 2, 3])}
    response = fr.render()
    assert isinstance(response, Response)
    assert isinstance(response.app_iter, StreamedResponse)
    assert response.json == {'a': [1, 2, 3]}
    dummy_request.__parent__ = 'something'
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    fr.response = {'a': (x for x in [1, 2, 3])}
    response = fr.render()
    assert isinstance(response, dict)
    assert response == {'a': [1, 2, 3]}
    


def test_searches_responses_query_response_init():
    from snosearch.responses import QueryResponse
    qr = QueryResponse([], [])
    assert isinstance(qr, QueryResponse)


def test_searches_responses_basic_query_response_with_facets_init():
    from snosearch.responses import BasicQueryResponseWithFacets
    bqr = BasicQueryResponseWithFacets([], [])
    assert isinstance(bqr, BasicQueryResponseWithFacets)


def test_searches_responses_raw_query_response_with_aggs_init():
    from snosearch.responses import RawQueryResponseWithAggs
    rqr = RawQueryResponseWithAggs([], [])
    assert isinstance(rqr, RawQueryResponseWithAggs)


def test_searches_responses_basic_matrix_response_with_facets_init():
    from snosearch.responses import BasicMatrixResponseWithFacets
    from snosearch.mixins import AggsToFacetsMixin
    from snosearch.mixins import AggsToMatrixMixin
    bmr = BasicMatrixResponseWithFacets([], [])
    assert isinstance(bmr, BasicMatrixResponseWithFacets)
    assert isinstance(bmr, AggsToFacetsMixin)
    assert isinstance(bmr, AggsToMatrixMixin)


def test_searches_responses_audit_matrix_response_with_facets_init():
    from snosearch.responses import AuditMatrixResponseWithFacets
    from snosearch.mixins import AggsToFacetsMixin
    from snosearch.mixins import AuditAggsToMatrixMixin
    amr = AuditMatrixResponseWithFacets([], [])
    assert isinstance(amr, AuditMatrixResponseWithFacets)
    assert isinstance(amr, AggsToFacetsMixin)
    assert isinstance(amr, AuditAggsToMatrixMixin)


def test_searches_responses_streamed_response_init():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    assert isinstance(sr, StreamedResponse)


def test_searches_responses_streamed_response_characters():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    assert sr._start_dict() == '{'
    assert sr._end_dict() == '}'
    assert sr._start_list() == '['
    assert sr._end_list() == ']'
    assert sr._comma() == ','
    assert sr._colon() == ':'


def test_searches_responses_streamed_response_to_json_string():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    assert sr._to_json({'a': 1}) == '{"a": 1}'
    assert sr._to_json(
        {'a': 1, 'b': [1, 2, 3]}
    ) == '{"a": 1, "b": [1, 2, 3]}' or '{"b": [1, 2, 3], "a": 1}'


def test_searches_responses_streamed_response_to_json_string_from_generator():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    g = (x for x in [{'a': 1}])
    assert list(sr._to_json_from_generator(g)) == [
        '[',
        '{"a": 1}',
        ']'
    ]
    g = (x for x in [{'a': 1}, {'b': [1, 2, 3]}, {'x': {'y': {'a': 1}}}])
    assert list(sr._to_json_from_generator(g)) == [
        '[',
        '{"a": 1}',
        ',',
        '{"b": [1, 2, 3]}',
        ',',
        '{"x": {"y": {"a": 1}}}',
        ']'
    ]


def test_searches_responses_streamed_response_iter():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    fr.response = {}
    assert list(sr._iter()) == ['{', '}']
    fr.response = {'a': 1}
    assert list(sr._iter()) == ['{', '"a"', ':', '1', '}']
    fr.response = {'a': 1, 'b': (x for x in [1, 2, 3])}
    assert list(sr._iter()) == [
        '{',
        '"a"',
        ':',
        '1',
        ',',
        '"b"',
        ':',
        '[',
        '1',
        ',',
        '2',
        ',',
        '3',
        ']',
        '}'
    ]
    fr.response = {'a': 1, 'b': (x for x in [{'a': 0}, {'b': [1, 2, {'a': 1}]}, {'c': 3}])}
    assert list(sr._iter()) == [
        '{',
        '"a"',
        ':',
        '1',
        ',',
        '"b"',
        ':',
        '[',
        '{"a": 0}',
        ',',
        '{"b": [1, 2, {"a": 1}]}',
        ',',
        '{"c": 3}',
        ']',
        '}'
    ]


def test_searches_responses_streamed_response__iter__():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    fr.response = {}
    assert list(sr) == [b'{', b'}']
    fr.response = {'a': 1}
    assert list(sr) == [b'{', b'"a"', b':', b'1', b'}']
    fr.response = {'a': 1, 'b': (x for x in [1, 2, 3])}
    assert list(sr) == [
        b'{',
        b'"a"',
        b':',
        b'1',
        b',',
        b'"b"',
        b':',
        b'[',
        b'1',
        b',',
        b'2',
        b',',
        b'3',
        b']',
        b'}'
    ]
    fr.response = {'a': 1, 'b': (x for x in [{'a': 0}, {'b': [1, 2, {'a': 1}]}, {'c': 3}])}
    assert list(sr) == [
        b'{',
        b'"a"',
        b':',
        b'1',
        b',',
        b'"b"',
        b':',
        b'[',
        b'{"a": 0}',
        b',',
        b'{"b": [1, 2, {"a": 1}]}',
        b',',
        b'{"c": 3}',
        b']',
        b'}'
    ]


def test_searches_responses_streamed_response_make_streamed_response():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    fr.response = {'a': 1}
    response = sr._make_streamed_response()
    assert response.content_type == 'application/json'
    assert isinstance(response.app_iter, StreamedResponse)
    assert response.body == b'{"a":1}'


def test_searches_responses_streamed_response_render():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import StreamedResponse
    fr = FieldedResponse()
    sr = StreamedResponse(fr)
    fr.response = {'a': 1}
    response = sr.render()
    assert response.content_type == 'application/json'
    assert isinstance(response.app_iter, StreamedResponse)
    assert response.body == b'{"a":1}'


def test_searches_responses_in_memory_response_init():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import InMemoryResponse
    fr = FieldedResponse()
    im = InMemoryResponse(fr)
    assert isinstance(im, InMemoryResponse)


def test_searches_responses_in_memory_response_render():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import InMemoryResponse
    fr = FieldedResponse()
    im = InMemoryResponse(fr)
    fr.response = {'a': 1}
    response = im.render()
    assert isinstance(response, dict)
    assert response == {'a': 1}
    fr.response = {'a': 1, 'b': (x for x in [1, 2, 3])}
    response = im.render()
    assert response == {'a': 1, 'b': [1, 2, 3]}


def test_searches_responses_generator_memory_response_init():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import FieldedGeneratorResponse
    from snosearch.responses import GeneratorResponse
    fr = FieldedResponse()
    gr = GeneratorResponse(fr)
    assert isinstance(gr, GeneratorResponse)
    fgr = FieldedGeneratorResponse()
    gr = GeneratorResponse(fgr)
    assert isinstance(gr, GeneratorResponse)


def test_searches_responses_generator_response_render():
    from snosearch.responses import FieldedResponse
    from snosearch.responses import FieldedGeneratorResponse
    from snosearch.responses import GeneratorResponse
    from types import GeneratorType
    fr = FieldedResponse()
    gr = GeneratorResponse(fr)
    fr.response = {'a': 1}
    response = gr.render()
    assert isinstance(response, dict)
    assert response == {}
    fr.response = {'a': 1, 'b': (x for x in [1, 2, 3])}
    response = gr.render()
    assert 'a' not in response
    assert 'b' in response
    assert isinstance(response['b'], GeneratorType)
    fgr = FieldedGeneratorResponse()
    gr = GeneratorResponse(fgr)
    fgr.response = {'a': 1}
    response = gr.render()
    assert isinstance(response, dict)
    assert response == {}
    fgr.response = {'a': 1, 'b': (x for x in [1, 2, 3])}
    response = gr.render()
    assert 'a' not in response
    assert 'b' in response
    assert isinstance(response['b'], GeneratorType)


def test_searches_responses_fielded_generator_response_init():
    from snosearch.responses import FieldedGeneratorResponse
    fgr = FieldedGeneratorResponse()
    assert isinstance(fgr, FieldedGeneratorResponse)


def test_searches_responses_fielded_generator_response_response_factory(dummy_request):
    from snosearch.responses import FieldedGeneratorResponse
    from snosearch.responses import GeneratorResponse
    from snosearch.parsers import ParamsParser
    fgr = FieldedGeneratorResponse()
    fgr.response = {'a': 1}
    assert isinstance(fgr._response_factory(), GeneratorResponse)
    fgr = FieldedGeneratorResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert isinstance(fgr._response_factory(), GeneratorResponse)
    fgr.response = {'a': (x for x in [1, 2, 3])}
    assert isinstance(fgr._response_factory(), GeneratorResponse)
    dummy_request.__parent__ = 'something'
    fgr = FieldedGeneratorResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert isinstance(fgr._response_factory(), GeneratorResponse)
    fgr.response = {'a': (x for x in [1, 2, 3])}
    assert isinstance(fgr._response_factory(), GeneratorResponse)


def test_searches_responses_fielded_generator_response_render(dummy_request):
    from snosearch.responses import FieldedGeneratorResponse
    from snosearch.responses import GeneratorResponse
    from snosearch.parsers import ParamsParser
    from types import GeneratorType
    from pyramid.response import Response
    fgr = FieldedGeneratorResponse()
    fgr.response = {'a': 1}
    response = fgr.render()
    assert isinstance(response, dict)
    fgr.response = {'a': (x for x in [1, 2, 3])}
    response = fgr.render()
    assert isinstance(response, dict)
    assert 'a' in response
    assert isinstance(response['a'], GeneratorType)
    assert list(response['a']) == [1, 2, 3]
    dummy_request.__parent__ = 'something'
    fgr = FieldedGeneratorResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    fgr.response = {'a': (x for x in [1, 2, 3])}
    response = fgr.render()
    assert isinstance(response, dict)
    assert 'a' in response
    assert isinstance(response['a'], GeneratorType)
    assert list(response['a']) == [1, 2, 3]


def test_searches_responses_fielded_in_memory_response_init():
    from snosearch.responses import FieldedInMemoryResponse
    fimr = FieldedInMemoryResponse()
    assert isinstance(fimr, FieldedInMemoryResponse)


def test_searches_responses_fielded_in_memory_response_response_factory(dummy_request):
    from snosearch.responses import FieldedInMemoryResponse
    from snosearch.responses import InMemoryResponse
    from snosearch.parsers import ParamsParser
    fimr = FieldedInMemoryResponse()
    fimr.response = {'a': 1}
    assert isinstance(fimr._response_factory(), InMemoryResponse)
    fimr = FieldedInMemoryResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert isinstance(fimr._response_factory(), InMemoryResponse)
    fimr.response = {'a': (x for x in [1, 2, 3])}
    assert isinstance(fimr._response_factory(), InMemoryResponse)
    dummy_request.__parent__ = 'something'
    fimr = FieldedInMemoryResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    assert isinstance(fimr._response_factory(), InMemoryResponse)
    fimr.response = {'a': (x for x in [1, 2, 3])}
    assert isinstance(fimr._response_factory(), InMemoryResponse)


def test_searches_responses_fielded_in_memory_response_render(dummy_request):
    from snosearch.responses import FieldedInMemoryResponse
    from snosearch.responses import InMemoryResponse
    from snosearch.parsers import ParamsParser
    from pyramid.response import Response
    fimr = FieldedInMemoryResponse()
    fimr.response = {'a': 1}
    response = fimr.render()
    assert isinstance(response, dict)
    fimr.response = {'a': (x for x in [1, 2, 3])}
    response = fimr.render()
    assert isinstance(response, dict)
    assert 'a' in response
    assert isinstance(response['a'], list)
    assert response['a'] == [1, 2, 3]
    dummy_request.__parent__ = 'something'
    fimr = FieldedInMemoryResponse(
        _meta={
            'params_parser': ParamsParser(dummy_request)
        }
    )
    fimr.response = {'a': (x for x in [1, 2, 3])}
    response = fimr.render()
    assert isinstance(response, dict)
    assert 'a' in response
    assert isinstance(response['a'], list)
    assert response['a'] == [1, 2, 3]

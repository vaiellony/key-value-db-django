import json

OK_CODE = 200
BAD_REQUEST_CODE = 400
NOT_FOUND_CODE = 404
JSON_CONTENT_TYPES = ['application/json']


def validate_request_and_load_json(request):
    try:
        request.content = request.body.decode()
    except ValueError:
        request.content = ''

    is_valid = True
    accepts_json = True
    request.json = {}
    if not request.META.get('CONTENT_LENGTH'):
        is_valid = False
    accepted_types = request.META.get('HTTP_ACCEPT', [])
    if accepted_types:
        if not isinstance(accepted_types, list):
            accepted_types = [accepted_types]
        accepts_json = any([
            acc_type in accepted_types for acc_type in JSON_CONTENT_TYPES + ['*/*']
        ])

    if not hasattr(request, 'content_type'):
        request.content_type = request.META.get('CONTENT_TYPE', [])

    is_json_type = request.content_type and any(
        json_type in request.content_type for json_type in JSON_CONTENT_TYPES
    )

    if not accepts_json or not is_json_type:
        return False

    json_content = request.content
    try:
        request.json = json.loads(json_content)
        if request.json is None:
            request.json = {}
    except ValueError:
        request.json = {}

    return is_valid


def validate_json_request(request, expected_params):
    """

    :param django.core.handlers.wsgi.WSGIRequest request: incoming JSON request
    :param str | set | list | tuple expected_params: parameters expected to be present in the payload.
                                                        Can be a str for single param or
                                                        an iterable such as set, list, tuple for multiple params
    :returns: 2 elements tuple:
                 1. Validation passed: 1st element is True, 2nd element is the request's payload (from json to dict)
                 2. Validation failed: 1st element is False, 2nd element is the error payload (dict with `error` key)
    """
    is_valid = validate_request_and_load_json(request)
    if not is_valid:
        response_payload = {'error': 'Request should accept JSON and its body should be a JSON object. '
                                     '`Content-Length` header should also be specified'}
        return False, response_payload

    request_payload = request.json
    if not isinstance(expected_params, (set, list, tuple)):
        expected_params = [expected_params]
    if not all([param in request_payload for param in expected_params]):
        response_payload = {
            'error': 'Request is missing parameters. Expected: {}, Found: {}'.format(list(expected_params),
                                                                                     list(request_payload.keys()))
        }
        return False, response_payload

    return True, request_payload

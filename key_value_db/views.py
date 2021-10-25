import logging

from django.http import JsonResponse
from django.views.generic import View

from key_value_db.utils import OK_CODE, NOT_FOUND_CODE, BAD_REQUEST_CODE, validate_json_request

logger = logging.getLogger(__name__)
key_value_dict = {}


class GetView(View):
    def get(self, request):
        key = request.GET.get('key')
        if not key:
            resp = JsonResponse({
                'error': 'Missing parameter `key`'
            })
            resp.status_code = BAD_REQUEST_CODE
            return resp

        if key not in key_value_dict:
            resp = JsonResponse({
                'error': 'Key `{}` does not exist in the database'.format(key)
            })
            resp.status_code = NOT_FOUND_CODE
            return resp

        value = key_value_dict[key]
        resp = JsonResponse({
            'key': key,
            'value': value
        })
        resp.status_code = OK_CODE
        return resp


class SetView(View):
    def post(self, request):
        is_valid, payload = validate_json_request(request, {'key', 'value'})
        if not is_valid:
            resp = JsonResponse(payload)
            resp.status_code = BAD_REQUEST_CODE
            return resp
        key = payload['key']
        value = payload['value']
        if key in key_value_dict:
            # logging differently in case of overrides for tracking purposes
            logger.info('Overriding existing key {} --> {} with new value: {}'.format(key, key_value_dict[key], value))
        else:
            logger.info('Inserting new key-value pair: {} --> {}'.format(key, value))

        key_value_dict[key] = value
        resp = JsonResponse({
            'key': key,
            'value': value
        })
        resp.status_code = OK_CODE
        return resp


class DeleteView(View):
    def post(self, request):
        is_valid, payload = validate_json_request(request, 'key')
        if not is_valid:
            resp = JsonResponse(payload)
            resp.status_code = BAD_REQUEST_CODE
            return resp
        key = payload['key']
        if key in key_value_dict:
            value = key_value_dict.pop(key)
            logger.info('Deleted key-value pair: {} --> {}'.format(key, value))
            resp = JsonResponse({
                'key': key,
                'value': value
            })
        else:
            logger.info('Tried to delete non-existent key: {}'.format(key))
            resp = JsonResponse({
                'message': "'Key `{}` does not exist".format(key),
            })

        resp.status_code = OK_CODE
        return resp

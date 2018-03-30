import logging
from aiohttp.web import middleware, json_response


log = logging.getLogger(__name__)


@middleware
async def error_middleware(request, handler):
    """Логгируем и отправляем пользователю ошибки, произошедшие на стороне бэкенда"""
    try:
        response = await handler(request)
        return response
    except Exception as ex:
        log.exception(f'Server error:')
        return json_response(
            status=502,
            data={'error': str(ex)},
        )

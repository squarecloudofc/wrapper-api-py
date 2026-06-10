import inspect
import logging
import types
from typing import Any

from ..http import Endpoint, Response
from . import ListenerManager


class RequestListenerManager(ListenerManager):
    """CaptureListenerManager"""

    def __init__(self) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance variables that will be used by other methods
        in the class.


        :param self: Refer to the class instance
        :return: A dictionary of the capture listeners and request listeners
        """
        super().__init__()

    async def notify(
        self, endpoint: Endpoint, response: Response, extra_value: Any
    ) -> Any:
        """
        The on_request function is called when a request has been made to the
        endpoint.
        The response object contains all the information about the request

        :param self: Refer to the class instance
        :param endpoint: Endpoint: Get the endpoint that was called
        :param response: Response: Get the response from the endpoint
        :return: The result of the call function
        """

        if not (listener := self.get_listener(endpoint)):
            return None
        logger = logging.getLogger('squarecloud')
        kwargs: dict[str, Any] = {}
        call_params = listener.callback_params
        call_extra_param: inspect.Parameter | None = call_params.get('extra')
        annotation: Any | None = None

        if 'response' in call_params.keys():
            kwargs['response'] = response
        if 'extra' in call_params.keys():
            kwargs['extra'] = extra_value

        if call_extra_param:
            annotation = call_extra_param.annotation
        is_coro: bool = inspect.iscoroutinefunction(listener.callback)
        try:
            if is_coro:
                listener_result = await listener.callback(**kwargs)
            else:
                listener_result = listener.callback(**kwargs)
            logger.info(
                f'listener "{listener.callback.__name__}" was invoked.\n'
                f'Endpoint: {listener.endpoint}\n'
                f'RETURN: {listener_result}\n',
                extra={'type': 'listener'},
            )
            return listener_result
        except Exception as exc:
            logger.error(
                f'Failed to call listener "{listener.callback.__name__}.\n'
                f'Error: {exc.__repr__()}.\n',
                extra={'type': 'listener'},
            )
            if listener.config.force_raise:
                raise exc

import inspect
import logging
import types
from typing import Any, Union

from .. import data, errors
from ..http import Endpoint
from . import Listener, ListenerManager

ListenerDataTypes = Union[
    data.AppData,
    data.StatusData,
    data.LogsData,
    data.Snapshot,
]


class CaptureListenerManager(ListenerManager):
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

    def include_listener(self, listener: Listener) -> Listener:
        allowed_endpoints: tuple[Endpoint, Endpoint, Endpoint, Endpoint] = (
            Endpoint.logs(),
            Endpoint.app_status(),
            Endpoint.snapshot(),
            Endpoint.app_data(),
        )

        if listener.endpoint not in allowed_endpoints:
            raise errors.InvalidListener(
                message='the endpoint to capture must be '
                f'{allowed_endpoints}',
                listener=listener.callback,
            )
        if self.get_listener(listener.endpoint):
            raise errors.InvalidListener(
                message='Already exists an capture_listener for '
                f'{listener.endpoint}',
                listener=listener.callback,
            )
        self.listeners.update({listener.endpoint.name: listener})
        return listener

    async def notify(
        self,
        endpoint: Endpoint,
        before: ListenerDataTypes | None,
        after: ListenerDataTypes,
        extra_value: Any = None,
    ) -> Any:
        """
        The on_capture function is called when a capture event occurs.

        :param self: Refer to the class instance
        :param endpoint: Endpoint: Get the endpoint that is being called
        :param before:
        :param after:
        :param extra:
        :return: The result of the call function
        """

        if not (listener := self.get_listener(endpoint)):
            return None
        logger = logging.getLogger('squarecloud')
        kwargs: dict[str, Any] = {}
        call_params = listener.callback_params
        call_extra_param: inspect.Parameter | None = call_params.get('extra')
        if 'before' in call_params.keys():
            kwargs['before'] = before
        if 'after' in call_params.keys():
            kwargs['after'] = after
        if 'extra' in call_params.keys():
            kwargs['extra'] = extra_value
        info_msg: str = (
            f'ENDPOINT: {listener.endpoint}\n'
            f'APP-TAG: {listener.app.name}\n'
            f'APP-ID: {listener.app.id}'
        )
        if call_extra_param:
            info_msg += f'\nEXTRA: {extra_value}'
        is_coro: bool = inspect.iscoroutinefunction(listener.callback)
        try:
            if is_coro:
                listener_result = await listener.callback(**kwargs)
            else:
                listener_result = listener.callback(**kwargs)
            logger.info(
                f'listener "{listener.callback.__name__}" was invoked.\n'
                f'{info_msg}\n'
                f'RETURN: {listener_result}',
                extra={'type': 'listener'},
            )
            return listener_result
        except Exception as exc:
            logger.error(
                f'Failed to call listener "{listener.callback.__name__}.\n'
                f'Error: {exc.__repr__()}.\n'
                f'APP-TAG: {listener.app.name}\n'
                f'APP-ID: {listener.app.id}',
                extra={'type': 'listener'},
            )
            if listener.config.force_raise:
                raise exc

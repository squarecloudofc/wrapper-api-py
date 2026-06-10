"""This module is a wrapper for using the SquareCloud API"""

from __future__ import annotations

from functools import wraps
from io import BytesIO
from typing import Any, Callable, Literal, ParamSpec, TypeVar, cast

from typing_extensions import deprecated

from .app import Application
from .data import (
    AppData,
    Certificate,
    Database,
    DatabaseInfo,
    DeployData,
    DNSRecord,
    DomainAnalytics,
    FileInfo,
    LogsData,
    ResumedStatus,
    Snapshot,
    SnapshotInfo,
    StatusData,
    UploadData,
    UserData,
    Workspace,
)
from .errors import ApplicationNotFound, InvalidFile, SquareException
from .file import File
from .http import HTTPClient, Response
from .http.endpoints import Endpoint
from .listeners import Listener, ListenerConfig
from .listeners.request_listener import RequestListenerManager
from .logger import logger

P = ParamSpec("P")
R = TypeVar("R")


class Client(RequestListenerManager):
    """A client for interacting with the SquareCloud API."""

    def __init__(
        self,
        api_key: str,
        log_level: Literal[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ] = "INFO",
    ) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines all of its
        attributes.


        :param self: Refer to the class instance
        :param api_key: str: Your API key, get in:
         https://squarecloud.app/dashboard/me
        :param debug: bool: Set the logging level to debug
        :return: None
        """
        self.log_level = log_level
        self._api_key = api_key

        if not isinstance(self._api_key, str):
            raise TypeError("api_key must be str")

        self._http = HTTPClient(api_key=api_key)
        self.logger = logger
        logger.setLevel(log_level)
        super().__init__()

    @property
    def api_key(self) -> str:
        """
        Returns the api key for the client.

        :return: The api key
        :rtype: str
        """
        return self._api_key

    def on_request(self, endpoint: Endpoint, **kwargs) -> Callable:
        """
        The on_request function is a decorator that allows you to register a
        function as an endpoint listener.

        :param endpoint: Endpoint: Specify the endpoint that will be used to
            capture the request
        :return: A wrapper function
        """

        def wrapper(func: Callable) -> None:
            """
            The wrapper function is a decorator that wraps the function passed
            to it.
            It takes in a function, and returns another function. The wrapper
            will call
            the wrapped function with all of its arguments, and then do
            something extra
            with the result.

            :param func: Callable: Specify the type of the parameter
            :return: The function itself, if the endpoint is not already
                    registered
            :raises SquarecloudException: Raised if the endpoint is already
                    registered
            """
            for key, value in kwargs.items():
                if key not in ListenerConfig.__annotations__:
                    raise ValueError(
                        f'Invalid listener configuration: "{key}={value}"'
                    )
            config = ListenerConfig(**kwargs)
            listener = Listener(
                endpoint=endpoint, callback=func, client=self, config=config
            )
            self.include_listener(listener)

        return wrapper

    @staticmethod
    def _notify_listener(endpoint: Endpoint) -> Callable:
        """
        The _notify_listener function is a decorator that call a listener after
        the decorated coroutine is called

        :param endpoint: the endpoint for witch the listener will fetch
        :return: a callable
        """

        def wrapper(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            async def decorator(
                self: Client, *args: P.args, **kwargs: P.kwargs
            ) -> R:
                # result: Any
                response: Response
                result = await func(self, *args, **kwargs)
                response = self._http.last_response
                if kwargs.get("avoid_listener", False):
                    return result
                await self.notify(
                    endpoint=endpoint,
                    response=response,
                    extra_value=kwargs.get("extra"),
                )
                return result

            return decorator

        return wrapper

    @_notify_listener(Endpoint.user())
    async def user(self, **_kwargs) -> UserData:
        """
        This method is used to get your information.

        :param _kwargs: Keyword arguments
        :return: A UserData object
        :rtype: UserData

        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.fetch_user_info()
        payload: dict[str, Any] = response.response
        return UserData(**payload["user"])

    @_notify_listener(Endpoint.logs())
    async def get_logs(self, app_id: str, **_kwargs) -> LogsData:
        """
        The get_logs method is used to get logs for an application.

        :param app_id: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: A LogsData object
        :rtype: LogsData

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.fetch_logs(app_id)
        payload: dict[str, Any] | None = response.response
        if not payload:
            logs_data: LogsData = LogsData()
        else:
            logs_data: LogsData = LogsData(**payload)

        return logs_data

    
    @_notify_listener(Endpoint.app_status())
    async def app_status(self, app_id: str, **_kwargs) -> StatusData:
        """
        The app_status method is used to get the status of an application.

        :param app_id: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: A StatusData object
        :rtype: StatusData

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.fetch_app_status(app_id)
        payload: dict[str, Any] = response.response
        return StatusData(**payload)

    
    @_notify_listener(Endpoint.start())
    async def start_app(self, app_id: str, **_kwargs) -> Response:
        """
        The start_app method starts an application.

        :param app_id: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.start_application(app_id)

    
    @_notify_listener(Endpoint.stop())
    async def stop_app(self, app_id: str, **_kwargs) -> Response:
        """
        The stop_app method stops an application.

        :param app_id: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.stop_application(app_id)

    
    @_notify_listener(Endpoint.restart())
    async def restart_app(self, app_id: str, **_kwargs) -> Response:
        """
        The restart_app method is restarts an application.

        :param app_id: Specify the application id
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.restart_application(app_id)    
    
    @_notify_listener(Endpoint.snapshot())
    async def snapshot(self, app_id: str, **_kwargs) -> Snapshot:
        """
        The snapshot method is used to save a snapshot of an application.

        :param app_id: Specify the application id
        :param _kwargs: Keyword arguments
        :return: A Snapshot object
        :rtype: Snapshot

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.snapshot(app_id)
        payload: dict[str, Any] = response.response
        return Snapshot(**payload)

    
    async def restore_snapshot(self, application_type: Literal["app", "database"], app_id: str, snapshot_id:str, version_id:str, **_kwargs) -> Response:
        """
        The restore_snapshot method is used to restore a snapshot of an application.

        :param application_type: Specify the type of the application, it can be "app" or "database"
        :param app_id: Specify the application id
        :param snapshot_id: Specify the snapshot id
        :param version_id: Specify the snapshot version id

        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """

        if application_type not in ["app", "database"]:
            raise ValueError("application_type must be 'app' or 'database'")
        

        return await self._http.restore_snapshot(app_type=application_type, app_id=app_id, snapshot_id=snapshot_id, version_id=version_id)

    
    @_notify_listener(Endpoint.delete_app())
    async def delete_app(self, app_id: str, **_kwargs) -> Response:
        """
        The delete_app method deletes an application.

        :param app_id: The application id
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.delete_application(app_id)

    
    @_notify_listener(Endpoint.commit())
    async def commit(self, app_id: str, file: File, **_kwargs) -> Response:
        """
        The commit method is used to commit an application.

        :param app_id: Specify the application by id
        :param file: File: Specify the File object to be committed
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.commit(app_id, file)

    
    @_notify_listener(Endpoint.user())
    async def app(self, app_id: str, **_kwargs) -> Application:
        """
        The app method returns an Application object.

        :param app_id: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: An Application object
        :rtype: Application

        :raises ApplicationNotFound: Raised when is not found an application
                with the specified id
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.fetch_user_info()
        payload = response.response
        app_data = list(
            filter(
                lambda application: application["id"] == app_id,
                payload["applications"],
            )
        )
        if not app_data:
            raise ApplicationNotFound(app_id=app_id)
        app_data = app_data.pop()
        app_data = AppData(**app_data).to_dict()
        return Application(client=self, http=self._http, **app_data)

    # @_notify_listener(Endpoint.user())
    async def all_apps(self, **_kwargs) -> list[Application]:
        """
        The all_apps method returns a list of all applications that the user
        has access to.

        :param _kwargs: Keyword arguments
        :return: A list of Application objects
        :rtype: list[Application]

        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.fetch_user_info()
        payload = response.response
        apps_data: list = payload["applications"]
        apps: list[Application] = []
        for data in apps_data:
            data = AppData(**data).to_dict()
            apps.append(Application(client=self, http=self._http, **data))
        return apps

    
    @_notify_listener(Endpoint.upload())
    async def upload_app(self, file: File, **_kwargs) -> UploadData:
        """
        The upload_app method uploads an application to the server.

        :param file: Upload a file
        :param _kwargs: Keyword arguments
        :return: An UploadData object
        :rtype: UploadData

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        :raises FewMemory: Raised when user memory reached the maximum
                amount of memory
        :raises BadMemory: Raised when the memory in configuration file is
                invalid
        :raises MissingConfigFile: Raised when the .zip file is missing the
                config file (squarecloud.app/squarecloud.config)
        :raises MissingDependenciesFile: Raised when the .zip file is missing
                the dependencies file (requirements.txt, package.json, ...)
        :raises MissingMainFile: Raised when the .zip file is missing the main
                file (main.py, index.js, ...)
        :raises InvalidMain: Raised when the field MAIN in config file is
                invalid or when the main file is corrupted
        :raises InvalidDisplayName: Raised when the field DISPLAY_NAME
                in config file is invalid
        :raises MissingDisplayName: Raised when the DISPLAY_NAME field is
                missing in the config file
        :raises InvalidMemory: Raised when the MEMORY field is invalid
        :raises MissingMemory: Raised when the MEMORY field is missing in
                the config file
        :raises InvalidVersion: Raised when the VERSION field is invalid,
                the value accepted is "recommended" or "latest"
        :raises MissingVersion: Raised when the VERSION field is missing in
                the config file
        :raises InvalidAccessToken: Raised when a GitHub access token
                provided is invalid
        :raises InvalidDomain: Raised when a domain provided is invalid
        """
        if not isinstance(file, File):
            raise InvalidFile(f"you need provide an {File.__name__} object")

        if (file.filename is not None) and (
            file.filename.split(".")[-1] != "zip"
        ):
            raise InvalidFile("the file must be a .zip file")
        response: Response = await self._http.upload(file)
        payload: dict[str, Any] = response.response
        return UploadData(**payload)

    
    @_notify_listener(Endpoint.files_list())
    async def app_files_list(
        self, app_id: str, path: str, **_kwargs
    ) -> list[FileInfo]:
        """
        The app_files_list method returns a list of your application files.

        :param app_id: Specify the application by id
        :param path: Specify the path to the file
        :param _kwargs: Keyword arguments
        :return: A list of FileInfo objects
        :rtype: list[FileInfo]

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.fetch_app_files_list(
            app_id, path
        )
        if not response.response:
            return []
        return [
            FileInfo(**data, app_id=app_id, path=path + f"{data.get('name')}")
            for data in response.response
        ]

    
    @_notify_listener(Endpoint.files_read())
    async def read_app_file(
        self, app_id: str, path: str, **_kwargs
    ) -> BytesIO | None:
        """
        The read_app_file method reads a file from the specified path and
        returns a BytesIO representation.

        :param app_id: Specify the application by id
        :param path: str: Specify the path of the file to be read
        :param _kwargs: Keyword arguments
        :return: A BytesIO representation of the file
        :rtype: BytesIO | None

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.read_app_file(app_id, path)
        if response.response:
            return BytesIO(bytes(response.response.get("data")))
        return None

    
    @_notify_listener(Endpoint.files_create())
    async def create_app_file(
        self, app_id: str, file: File, path: str, **_kwargs
    ) -> Response:
        """
        The create_app_file method creates a new file in the specified
        directory.

        :param app_id: Specify the application by id
        :param file: Pass the file to be created
        :param path: Specify the directory to create the file in
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        if not isinstance(file, File):
            raise SquareException(
                "the file must be an string or a squarecloud.File object"
            )
        file_bytes = list(file.bytes.read())
        response: Response = await self._http.create_app_file(
            app_id, file_bytes, path=path
        )
        file.bytes.close()

        return response

    
    @_notify_listener(Endpoint.files_delete())
    async def delete_app_file(
        self, app_id: str, path: str, **_kwargs
    ) -> Response:
        """
        The delete_app_file method deletes a file in the specified directory.

        :param app_id: Specify the application by id
        :param path: Specify the directory where the file should be
        deleted
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.file_delete(app_id, path)

    
    @_notify_listener(Endpoint.last_deploys())
    async def last_deploys(
        self, app_id: str, **_kwargs
    ) -> list[list[DeployData]]:
        """
        The last_deploys method returns a list of DeployData objects.

        :param self: Represent the instance of a class
        :param app_id: str: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: A list of DeployData objects
        :rtype: list[list[DeployData]]

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.get_last_deploys(app_id)
        data = response.response
        return [[DeployData(**deploy) for deploy in _] for _ in data]

    
    @_notify_listener(Endpoint.github_integration())
    async def github_integration(
        self, app_id: str, access_token: str, **_kwargs
    ) -> str:
        """
        The github_integration method returns a GitHub Webhook url to integrate
        with your GitHub repository

        :param app_id: Specify the application by id
        :param access_token: your GitHub access token
        :param _kwargs: Keyword arguments
        :return: A GitHub Webhook url

        :raises InvalidAccessToken: Raised when a GitHub access token
                provided is invalid
        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.create_github_integration(
            app_id=app_id, github_access_token=access_token
        )
        data = response.response
        return data.get("webhook")

    
    @_notify_listener(Endpoint.custom_domain())
    async def set_custom_domain(
        self, app_id: str, custom_domain: str, **_kwargs
    ) -> Response:
        """
        The set_custom_domain method sets a custom domain to your website

        :param app_id: Specify the application by id
        :param custom_domain: Specify the custom domain to use for your website
        :param _kwargs: Keyword arguments
        :return: A Response object
        :rtype: Response

        :raises InvalidDomain: Raised when a domain provided is invalid
        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        return await self._http.update_custom_domain(
            app_id=app_id, custom_domain=custom_domain
        )

    
    @_notify_listener(Endpoint.domain_analytics())
    async def domain_analytics(
        self, app_id: str, **_kwargs
    ) -> DomainAnalytics:
        """
        The domain_analytics method return a DomainAnalytics object

        :param app_id: Specify the application by id
        :param _kwargs: Keyword arguments
        :return: A DomainAnalytics object
        :rtype: DomainAnalytics

        :raises NotFoundError: Raised when the request status code is 404
        :raises BadRequestError: Raised when the request status code is 400
        :raises AuthenticationFailure: Raised when the request status
                code is 401
        :raises TooManyRequestsError: Raised when the request status
                code is 429
        """
        response: Response = await self._http.domain_analytics(
            app_id=app_id,
        )
        return DomainAnalytics(**response.response)    
    
    @_notify_listener(Endpoint.all_snapshots())
    async def all_app_snapshots(
        self, app_id: str, **_kwargs
    ) -> list[SnapshotInfo]:
        """
        Retrieve all snapshots for a specific application.
        This method fetches a list of snapshots associated with the 
        given application ID and returns them as a list of `SnapshotInfo` objects.
        :param app_id: Specify the application by id.
        :type app_id: str
        :param _kwargs: Additional keyword arguments.
        :type _kwargs: dict
        :return: A list of `SnapshotInfo` objects representing the snapshots of 
                 the specified application.
        :rtype: list[SnapshotInfo]
        """
        response: Response = await self._http.get_all_app_snapshots(
            app_id=app_id
        )
        return [SnapshotInfo(**snapshot_data) for snapshot_data in response.response]

    @_notify_listener(Endpoint.all_apps_status())
    async def all_apps_status(self, **_kwargs) -> list[ResumedStatus]:
        """
        Retrieve the status of all applications.
        This method fetches the status of all applications
        and returns a list of `ResumedStatus` objects for applications
        that are currently running.
        :param _kwargs: Additional keyword arguments.
        :type _kwargs: dict
        :return: A list of `ResumedStatus` objects representing the status
                 of running applications.
        :rtype: list[ResumedStatus]
        """
        response: Response = await self._http.all_apps_status()
        all_status = []
        for status in response.response:
            if status["running"] is True:
                all_status.append(ResumedStatus(**status))
        return all_status

    
    @_notify_listener(Endpoint.move_file())
    async def move_app_file(
        self, app_id: str, origin: str, dest: str, **_kwargs
    ) -> Response:
        """
        Moves a file within an application from the origin path to the destination path.
        :param app_id: Specify the application by id.
        :type app_id: str
        :param origin: The current path of the file to be moved.
        :type origin: str
        :param dest: The target path where the file should be moved.
        :type dest: str
        :param _kwargs: Additional keyword arguments.
        :type _kwargs: dict
        :return: The response object containing the result of the move operation.
        :rtype: Response
        """
        response: Response = await self._http.move_app_file(
            app_id=app_id, origin=origin, dest=dest
        )
        return response

    
    @_notify_listener(Endpoint.dns_records())
    async def dns_records(self, app_id: str) -> list[DNSRecord]:
        """
        Retrieve DNS records for a specific application.
        :param app_id: Specify the application by id.
        :type app_id: str
        :return: A list of DNSRecord objects representing the DNS records of the application.
        :rtype: list[DNSRecord]
        """
        
        response: Response = await self._http.dns_records(app_id)
        return [DNSRecord(**data) for data in response.response]

    
    @_notify_listener(Endpoint.current_integration())
    async def current_app_integration(self, app_id: str) -> str | None:
        response: Response = await self._http.get_app_current_integration(
            app_id
        )
        return response.response["webhook"]

    async def get_app_envs(self, app_id: str) -> dict[str, str]:
        """
        Retrieve the environment variables of a specific application.
        :param app_id: Specify the application by id.
        :type app_id: str
        :return: A dictionary containing the environment variables as key-value pairs.
        :rtype: dict[str, str]
        """
        response: Response = await self._http.get_environment_variables(app_id)
        return response.response
    
    async def set_app_envs(self, app_id: str, envs: dict[str, str]) -> dict[str, str]:
        """
        Sets or edits environment variables for a specific application.
        This method sends a request to update the environment variables of the
        specified application with the provided key-value pairs.
        :param app_id: Specify the application by id.
        :type app_id: str
        :param envs: A dictionary containing the environment variables to set,
                     where the keys are variable names and the values are their
                     corresponding values.
        :type envs: dict[str, str]
        :return: A dictionary containing the updated environment with all variables.
        :rtype: dict[str, str]
        :raises HTTPException: If the HTTP request fails or returns an error response.
        """
        
        response: Response = await self._http.set_environment_variable(app_id, envs)
        return response.response
    
    async def delete_app_envs(self, app_id: str, keys: list[str]) -> dict[str, str]:
        """
        Deletes specified environment variables for a given application.
        :param app_id: Specify the application by id.
        :type app_id: str
        :param keys: A list of keys representing the environment variables to be deleted.
        :type keys: list[str]
        :return: A dictionary containing the remaining variables.
        :rtype: dict[str, str]
        """
        response: Response = await self._http.delete_environment_variable(app_id, keys)
        return response.response
    
    async def overwrite_app_envs(self, app_id: str, envs: dict[str, str]) -> dict[str, str]:
        """
        Overwrite the environment variables of a specific application.
        This method sets the dictionary provided as the new environment for the application.
        :param app_id: Specify the application by id.
        :type app_id: str
        :param envs: A dictionary containing the new environment variables to set
                     for the application. Keys and values must both be strings.
        :type envs: dict[str, str]
        :return: A dictionary containing the new environment after overwriting the
                 environment variables.
        :rtype: dict[str, str]
        """
        response: Response = await self._http.overwrite_environment_variables(app_id, envs)
        return response.response
    
    async def clear_app_envs(self, app_id: str) -> dict[str, str]:
        """
        Clears all environment variables for the specified application.
        This method overwrites the application's environment variables with an empty dictionary,
        effectively removing all existing environment variables.
        
        :param app_id: Specify the application by id.
        :type app_id: str
        :return: A dictionary containing the response from the server.
        :rtype: dict[str, str]
        """
        response: Response = await self._http.overwrite_environment_variables(app_id, {})
        return response.response
    
    @_notify_listener(Endpoint.create_database())
    async def create_database(
            self,
            name: str,
            memory: int,
            type: Literal["redis", "mongo", "mysql", "postgres"],
            *,
            version: str | None = None,
        ) -> Database:
        """
        Create a new database.

        :param name: Name of the database to be created.
        :param memory: Memory in MB allocated to the database.
        :param type: Database type ("redis", "mongo", "mysql", "postgres").
        :param version: Database version.
        :return: Database instance representing the created database.
        """
        versions = {
            "redis": "7.4.5",
            "mongo": "8.0.11",
            "postgres": "17.6",
            "mysql": "9.5",
        }
        version = version if version else versions.get(type)

        response: Response = await self._http.create_database(name=name, memory=memory, type=type, version=version)

        response.response.update({"certificate": Certificate(response.response['certificate'])})

        return Database(**response.response)
    
    @_notify_listener(Endpoint.get_database_info())
    async def get_database_info(self, database_id: str) -> DatabaseInfo:
        """
        Retrieve information about a specific database.

        :param database_id: ID of the database to retrieve information for.
        :return: DatabaseInfo instance containing details about the specified database.
        """
        response: Response = await self._http.get_database_information(database_id)
        return DatabaseInfo(**response.response)

    @_notify_listener(Endpoint.start_database())
    async def start_database(self, database_id: str) -> Response:
        """
        Start a specific database.

        :param database_id: ID of the database to be started.
        :return: Response object containing the result of the start operation.
        """
        return await self._http.start_database(database_id)

    @_notify_listener(Endpoint.stop_database())
    async def stop_database(self, database_id: str) -> Response:
        """
        Stop a specific database.

        :param database_id: ID of the database to be stopped.
        :return: Response object containing the result of the stop operation.
        """
        return await self._http.stop_database(database_id)

    @_notify_listener(Endpoint.edit_database())
    async def edit_database(self, database_id: str, name: str | None = None, memory: int | None = None) -> Response:
        """
        Edit the configuration of a specific database.

        :param database_id: ID of the database to be edited.
        :param name: New name for the database (optional).
        :param memory: New memory allocation in MB for the database (optional).
        :return: Response object containing the result of the edit operation.
        """
        return await self._http.edit_database(database_id, name=name, memory=memory)

    @_notify_listener(Endpoint.delete_database())
    async def delete_database(self, database_id: str) -> Response:
        """
        Delete a specific database.

        :param database_id: ID of the database to be deleted.
        :return: Response object containing the result of the delete operation.
        """
        return await self._http.delete_database(database_id)
    
    @_notify_listener(Endpoint.all_databases_status())
    async def all_databases_status(self) -> list[ResumedStatus]:
        """
        Retrieve the status of all databases.
        This method fetches the status of all databases
        and returns a list of `ResumedStatus` objects
        """

        response = await self._http.all_databases_status()
        return [ResumedStatus(**status) for status in response.response]

    @_notify_listener(Endpoint.database_status())
    async def get_database_status(self, database_id: str) -> StatusData:
        """
        Obtains the status of a specific database and returns a StatusData object.

        :param database_id: ID of the database
        :return: A StatusData object containing the status of the specified database.   
        """

        response = await self._http.get_database_status(database_id)
        return StatusData(**response.response)

    @_notify_listener(Endpoint.get_database_certificate())
    async def get_database_certificate(self, database_id: str) -> Certificate:
        """
        Retrieve the database TLS certificate.

        :param database_id: Database identifier.
        :return: Certificate instance.
        """

        response: Response = await self._http.get_database_certificate(database_id)

        return Certificate(response.response['certificate'])

    @_notify_listener(Endpoint.reset_database_credentials())
    async def reset_database_password(self, database_id: str) -> str:
        """
        Reset database password credentials.

        :param database_id: Database identifier.
        :return: Newly generated password.
        """

        response: Response = await self._http.reset_database_credentials(database_id, "password")

        return response.response["password"]
    
    @_notify_listener(Endpoint.reset_database_credentials())
    async def reset_database_certificate(self, database_id: str) -> Response:
        """
        Regenerate the database certificate.

        :param database_id: Database identifier.
        :return: API response.
        """
        response: Response = await self._http.reset_database_credentials(database_id, "certificate")
        return response

    async def create_workspace(self, name: str) -> Workspace:
        """Create a new workspace.

        :param name: Name of the workspace to create.
        :type name: str
        :return: Workspace object containing the created workspace data.
        :rtype: Workspace
        """
        create_workspace: Response = await self._http.create_workspace(name)
        get_workspace: Response = await self._http.fetch_workspace(create_workspace.response["id"])
        return Workspace(**get_workspace.response)

    async def get_workspace(self, workspace_id: str) -> Workspace:
        """Retrieve a workspace by its identifier.

        :param workspace_id: ID of the workspace to fetch.
        :type workspace_id: str
        :return: Workspace object containing workspace details.
        :rtype: Workspace
        """
        get_workspace: Response = await self._http.fetch_workspace(workspace_id)
        get_workspace.response["applications"] = list(
            map(lambda app: app | {"id": f'{app["id"]}-{get_workspace.response["id"]}'}, get_workspace.response["applications"])
        )
        return Workspace(**get_workspace.response)

    async def delete_workspace(self, workspace_id: str) -> Response:
        """Delete a workspace by its identifier.

        :param workspace_id: ID of the workspace to delete.
        :type workspace_id: str
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.delete_workspace(workspace_id)

    async def leave_workspace(self, workspace_id: str) -> Response:
        """Leave a workspace.

        :param workspace_id: ID of the workspace to leave.
        :type workspace_id: str
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.leave_workspace(workspace_id)

    async def all_workspaces(self) -> list[Workspace]:
        """Retrieve all workspaces available to the current user.

        :return: List of Workspace objects representing all accessible workspaces.
        :rtype: list[Workspace]
        """
        response: Response = await self._http.fetch_all_workspaces()
        for workspace in response.response:
            workspace["applications"] = list(
                map(lambda app: app | {"id": f'{app["id"]}-{workspace["id"]}'}, workspace["applications"])
            )
        return [Workspace(**workspace) for workspace in response.response]

    async def add_member_to_workspace(
        self, workspace_id: str, invite_code: str, permissions: Literal["admin", "maintain", "manager", "view"]
        ) -> Response:
        """Add a member to a workspace using an invite code.

        :param workspace_id: ID of the workspace.
        :type workspace_id: str
        :param invite_code: Invite code used to join the workspace.
        :type invite_code: str
        :param permissions: Permission level for the added member.
        :type permissions: Literal["admin", "maintain", "manager", "view"]
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.add_member_to_workspace(workspace_id, invite_code, permissions)

    async def remove_member_from_workspace(self, workspace_id: str, user_id: str) -> Response:
        """Remove a member from a workspace.

        :param workspace_id: ID of the workspace.
        :type workspace_id: str
        :param user_id: ID of the member to remove.
        :type user_id: str
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.remove_member_from_workspace(workspace_id, user_id)

    async def add_app_to_workspace(self, workspace_id: str, app_id: str) -> Response:
        """Add an application to a workspace.

        :param workspace_id: ID of the workspace.
        :type workspace_id: str
        :param app_id: ID of the application to add.
        :type app_id: str
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.add_app_to_workspace(workspace_id, app_id)

    async def remove_app_from_workspace(self, workspace_id: str, app_id: str) -> Response:
        """Remove an application from a workspace.

        :param workspace_id: ID of the workspace.
        :type workspace_id: str
        :param app_id: ID of the application to remove.
        :type app_id: str
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.remove_app_from_workspace(workspace_id, app_id)

    async def modify_member_permissions(
        self, workspace_id: str, user_id: str, permissions: Literal["admin", "maintain", "manager", "view"]
    ) -> Response:
        """Change a workspace member's permissions.

        :param workspace_id: ID of the workspace.
        :type workspace_id: str
        :param user_id: ID of the member whose permissions will be changed.
        :type user_id: str
        :param permissions: New permission level for the member.
        :type permissions: Literal["admin", "maintain", "manager", "view"]
        :return: Response object returned by the API.
        :rtype: Response
        """
        return await self._http.change_workspace_member_permission(workspace_id, user_id, permissions)

    async def get_invite_code(self) -> str:
        """Retrieve the workspace invite code for the current user.

        :return: Invite code string.
        :rtype: str
        """
        response: Response = await self._http.get_workspace_member_code()
        return cast(str, response.response.get("code", ""))
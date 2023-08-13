import io
from io import BytesIO

import click
from click import Context
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import squarecloud
from squarecloud import Client
from squarecloud.cli import run_async
from squarecloud.cli.app import app_group
from squarecloud.data import FileInfo
from squarecloud.http import Response


@app_group.command(name='file-list')
@click.argument(
    'path',
    default='/',
    required=True,
)
@click.pass_context
@run_async
async def file_list(ctx: Context, path: str):
    client: Client = ctx.obj['client']
    app_id = ctx.obj['app_id']
    with Console().status('loading'):
        files_info: list[FileInfo] = await client.app_files_list(app_id, path)
        table = Table(title='Status', header_style='purple')

        file_info_list = [
            attr for attr in dir(files_info[0]) if not attr.startswith('__')
        ]

        for f in file_info_list:
            table.add_column(f.capitalize())

        for file in files_info:
            table.add_row(
                *[str(getattr(file, attr)) for attr in file_info_list],
                style='green',
            )
    print(table)


@app_group.command(name='file-read')
@click.argument(
    'path',
    default='/',
    required=True,
)
@click.pass_context
@run_async
async def read_file(ctx: Context, path: str):
    client: Client = ctx.obj['client']
    app_id = ctx.obj['app_id']
    with Console().status('loading'):
        bytesio: BytesIO = await client.read_app_file(app_id, path)

        content = bytesio.read().decode('utf-8')
    if not content:
        panel = Panel(
            rf'the path {path} has no content',
            title='No Content',
            title_align='left',
            border_style='purple',
            style='red',
        )
        print(panel)
        return

    panel = Panel(
        content,
        title=path.split('/')[-1],
        title_align='left',
        border_style='purple',
        style='green',
    )

    print(panel)


@app_group.command(name='file-delete')
@click.argument(
    'path',
    default='/',
    required=True,
)
@click.pass_context
@run_async
async def file_delete(ctx: Context, path: str):
    client: Client = ctx.obj['client']
    app_id = ctx.obj['app_id']
    with Console().status('loading'):
        response: Response = await client.delete_app_file(app_id, path)

    match response.status:
        case 'success':
            panel = Panel(
                f"Successfully deleted file in: '{path}'",
                title='Success',
                title_align='left',
                border_style='purple',
                style='green',
            )
        case 'error':
            panel = Panel(
                f"'{path}' don't exists",
                title='File Not Found',
                title_align='left',
                border_style='purple',
                style='red',
            )
        case _:
            panel = Panel(
                f'Error on deleting file\n{response}',
                title='Error',
                title_align='left',
                border_style='red',
                style='red',
            )

    print(panel)


@app_group.command(name='file-create')
@click.argument(
    'file',
    type=click.File('rb'),
)
@click.option(
    '--path',
    default='/',
    type=click.STRING,
    required=True,
)
@click.pass_context
@run_async
async def file_create(ctx: Context, file: io.BufferedReader, path: str):
    client: Client = ctx.obj['client']
    app_id = ctx.obj['app_id']
    full_path = path + file.name
    if path != '/':
        full_path = f'/{path}/{file.name}'
    with Console().status('loading'):
        response: Response = await client.create_app_file(
            app_id,
            squarecloud.File(file),
            full_path,
        )

    match response.status:
        case 'success':
            panel = Panel(
                f"Successfully created file in: '{full_path}'",
                title='Success',
                title_align='left',
                border_style='purple',
                style='green',
            )
        case 'error':
            panel = Panel(
                f"'/{path}' don't exists",
                title='Directory Not Found',
                title_align='left',
                border_style='purple',
                style='red',
            )
        case _:
            panel = Panel(
                f"Error on creating file in '/{path}'\n{response}",
                title='Error',
                title_align='left',
                border_style='red',
                style='red',
            )
    print(panel)

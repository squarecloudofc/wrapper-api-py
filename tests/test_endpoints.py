"""Offline tests for the v4.1.0 endpoint additions (no API key needed)."""

import pytest

from squarecloud.http.endpoints import Endpoint, Router

BASE = Router.BASE_V2

NEW_ENDPOINTS = {
    'USER_SNAPSHOTS': ('GET', '/users/snapshots'),
    'SERVICE_STATUS': ('GET', '/service/status'),
    'ALL_DOMAINS': ('GET', '/apps/domains'),
    'LOAD_BALANCERS': ('GET', '/apps/load-balancers'),
    'APP_METRICS': ('GET', '/apps/{app_id}/metrics'),
    'REALTIME': ('GET', '/apps/{app_id}/realtime'),
    'GITHUB_APP_LINK': ('POST', '/apps/{app_id}/deploy/github-app'),
    'GITHUB_APP_UNLINK': ('DELETE', '/apps/{app_id}/deploy/github-app'),
    'NETWORK_ERRORS': ('GET', '/apps/{app_id}/network/errors'),
    'NETWORK_LOGS': ('GET', '/apps/{app_id}/network/logs'),
    'NETWORK_PERFORMANCE': ('GET', '/apps/{app_id}/network/performance'),
    'PURGE_CACHE': ('POST', '/apps/{app_id}/network/purge_cache'),
    'DATABASE_METRICS': ('GET', '/databases/{database_id}/metrics'),
    'ALL_DATABASE_SNAPSHOTS': ('GET', '/databases/{database_id}/snapshots'),
    'DATABASE_SNAPSHOT': ('POST', '/databases/{database_id}/snapshots'),
}


@pytest.mark.parametrize('name', NEW_ENDPOINTS)
def test_new_endpoint_definition(name: str):
    method, path = NEW_ENDPOINTS[name]
    endpoint = Endpoint(name)
    assert endpoint.method == method
    assert endpoint.path == path


def test_new_endpoint_classmethods():
    assert Endpoint.user_snapshots() == Endpoint('USER_SNAPSHOTS')
    assert Endpoint.service_status() == Endpoint('SERVICE_STATUS')
    assert Endpoint.all_domains() == Endpoint('ALL_DOMAINS')
    assert Endpoint.load_balancers() == Endpoint('LOAD_BALANCERS')
    assert Endpoint.app_metrics() == Endpoint('APP_METRICS')
    assert Endpoint.realtime() == Endpoint('REALTIME')
    assert Endpoint.github_app_link() == Endpoint('GITHUB_APP_LINK')
    assert Endpoint.github_app_unlink() == Endpoint('GITHUB_APP_UNLINK')
    assert Endpoint.network_errors() == Endpoint('NETWORK_ERRORS')
    assert Endpoint.network_logs() == Endpoint('NETWORK_LOGS')
    assert Endpoint.network_performance() == Endpoint('NETWORK_PERFORMANCE')
    assert Endpoint.purge_cache() == Endpoint('PURGE_CACHE')
    assert Endpoint.database_metrics() == Endpoint('DATABASE_METRICS')
    assert Endpoint.all_database_snapshots() == Endpoint(
        'ALL_DATABASE_SNAPSHOTS'
    )
    assert Endpoint.database_snapshot() == Endpoint('DATABASE_SNAPSHOT')


def test_router_builds_new_urls():
    route = Router(Endpoint.app_metrics(), app_id='abc')
    assert route.url == f'{BASE}/apps/abc/metrics'

    route = Router(Endpoint.database_snapshot(), database_id='db1')
    assert route.url == f'{BASE}/databases/db1/snapshots'

    route = Router(Endpoint.github_app_link(), app_id='abc')
    assert route.url == f'{BASE}/apps/abc/deploy/github-app'

    route = Router(Endpoint.service_status())
    assert route.url == f'{BASE}/service/status'

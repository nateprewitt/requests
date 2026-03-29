import requests.adapters


def test_request_url_trims_leading_path_separators():
    """See also https://github.com/psf/requests/issues/6643."""
    a = requests.adapters.HTTPAdapter()
    p = requests.Request(method="GET", url="http://127.0.0.1:10000//v:h").prepare()
    assert "/v:h" == a.request_url(p, {})


def test_proxy_manager_eviction():
    """Proxy manager cache should not grow beyond pool_connections."""
    a = requests.adapters.HTTPAdapter(pool_connections=2)
    proxies = [f"http://proxy{n}:8080" for n in range(3)]
    for proxy in proxies:
        a.proxy_manager_for(proxy)

    assert len(a.proxy_manager) == 2
    assert proxies[0] not in a.proxy_manager


def test_proxy_manager_lru():
    a = requests.adapters.HTTPAdapter(pool_connections=2)
    proxies = [f"http://proxy{n}:8080" for n in range(3)]
    a.proxy_manager_for(proxies[0])
    a.proxy_manager_for(proxies[1])

    # Access initial proxy again to bring it to "latest"
    a.proxy_manager_for(proxies[0])
    a.proxy_manager_for(proxies[2])

    assert proxies[0] in a.proxy_manager
    assert proxies[1] not in a.proxy_manager

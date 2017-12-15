import aiohttp

from nccostorage import create_app


if __name__ == '__main__':
    options = {
        'host': '127.0.0.1',
        'port': 8080
    }

    aiohttp.web.run_app(create_app(()), **options)

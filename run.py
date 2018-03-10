import aiohttp

from nccostorage import create_app


def read_config():
    server_config = {
        'host': '0.0.0.0',
        'port': 8080
    }
    return {
        'server': server_config,
        'loop': None,
    }


if __name__ == '__main__':
    config = read_config()
    app = create_app(config)

    aiohttp.web.run_app(app,
                        host=config['server']['host'],
                        port=config['server']['port'])

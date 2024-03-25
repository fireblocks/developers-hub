from fastapi import Request


async def parse_body(request: Request):
    """Parse raw body sent by the Co-Signer"""
    raw_body = await request.body()
    return raw_body.decode("ascii")


def load_plugin_list(plugins_str):
    res = []
    plugin_names: list[str] = plugins_str.split(",")
    for plugin_name in plugin_names:
        res.append(plugin_name.strip())

    return res


# python-mirth-client

[![PyPI Release](https://img.shields.io/pypi/v/mirth-client)](https://pypi.org/project/mirth-client/)
[![Documentation Status](https://readthedocs.org/projects/python-mirth-client/badge/?version=latest)](https://python-mirth-client.readthedocs.io/en/latest/?badge=latest)

A basic async Python interface for Mirth Connect

## Installation

`pip install mirth-client`

## Usage example

Assuming running within IPython or as part of an async application with an event-loop set up.

```python
from mirth_client import MirthAPI
from pprint import pprint

async with MirthAPI("https://mirth.domain.com/api") as api:
    await api.login("****", "****")

    # Check out list of channels
    for channel in await api.get_channels():
        metadata = await channel.get()
        print(f"ID: {metadata.id}")
        print(f"Name: {metadata.name}")
        print("")

    # Get stats for a channel
    s = await channels["3cdefad2-bf10-49ee-81c9-8ac6fd2fed67"].get_statistics()
    pprint(s)

    # Check channel for failed messages
    e = await channels["3cdefad2-bf10-49ee-81c9-8ac6fd2fed67"].get_messages(status="error")
    pprint(e)

    # Get 10 most recent events
    e = await api.get_events(10)
    pprint(e)
```

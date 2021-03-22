# python-mirth-client

A basic async Python interface for Mirth Connect

## Usage example

Assuming running within IPython or as part of an async application with an event-loop set up.

```python
from mirth_client import MirthAPI
from pprint import pprint

async with MirthAPI("https://mirth.ukrdc.nhs.uk/api") as api:
    await api.login("****", "****")

    # Check out list of channels
    for channel in await api.get_channels():
        print(f"ID: {channel.id}")
        print(f"Name: {channel.name}")
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

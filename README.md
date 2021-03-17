# python-mirth-client
Basic Python interface for Mirth Connect

## Very early development. Not currently for deployment.

## Usage example
```python
from mirth_client import MirthAPI
from pprint import pprint

api = MirthAPI("https://mirth.ukrdc.nhs.uk/api")
api.login("****", "****")

# Check out list of channels
for channel in api.get_channels():
    print(f"ID: {channel.id}")
    print(f"Name: {channel.name}")
    print("")
    
# Get stats for a channel
s = channels["3cdefad2-bf10-49ee-81c9-8ac6fd2fed67"].get_statistics()
pprint(s)

# Check channel for failed messages
e = channels["3cdefad2-bf10-49ee-81c9-8ac6fd2fed67"].get_messages(status="error")
pprint(e)

# Get 10 most recent events
e = api.get_events(10)
pprint(e)
```

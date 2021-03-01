from collections import namedtuple

# percentage cloud cover at each layer
Clouds = namedtuple("CloudCoverage", ["high", "medium", "low"])

# longitude is positive for west coordinates for this application
Location = namedtuple("Location", ["latitude", "longitude", "timezone"])



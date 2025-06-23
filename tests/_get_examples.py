import sys
import httpx
from pathlib import Path


if len(sys.argv) < 2:
    print("Please provide a Mirth API base URL")
    sys.exit(1)

BASE = sys.argv[1]

# Fetch OpenAPI spec
openapi = httpx.get(
    BASE + "openapi.json", verify=False, headers={"X-Requested-With": "HTTPX"}
).json()

API_VER = openapi["info"]["version"]

# Create output folders

OUTPUT_DIR = Path(__file__).parent.joinpath("examples").joinpath(API_VER)
RESPONSES_DIR = OUTPUT_DIR.joinpath("responses")
REQUESTS_DIR = OUTPUT_DIR.joinpath("requests")

RESPONSES_DIR.mkdir(exist_ok=True, parents=True)
REQUESTS_DIR.mkdir(exist_ok=True, parents=True)

# Get example documents

paths = openapi.get("paths")

for path in paths.values():
    for method in path.keys():
        # Response examples
        response_examples_xml = (
            path.get(method)
            .get("responses", {})
            .get("default", {})
            .get("content", {})
            .get("application/xml", {})
            .get("examples")
        )
        if response_examples_xml:
            for example in response_examples_xml.keys():
                href = response_examples_xml.get(example).get("$ref")
                if href:
                    example_container = httpx.get(
                        BASE + href, verify=False, headers={"X-Requested-With": "HTTPX"}
                    ).json()
                    example_xml = example_container.get("value")
                    with open(
                        RESPONSES_DIR.joinpath(method + "-" + example + ".xml"), "w"
                    ) as f:
                        f.write(example_xml)

        # Request examples
        request_examples_xml = (
            path.get(method)
            .get("requestBody", {})
            .get("content", {})
            .get("application/xml", {})
            .get("examples")
        )
        if request_examples_xml:
            for example in request_examples_xml.keys():
                href = request_examples_xml.get(example).get("$ref")
                if href:
                    example_container = httpx.get(
                        BASE + href, verify=False, headers={"X-Requested-With": "HTTPX"}
                    ).json()
                    example_xml = example_container.get("value")
                    with open(
                        REQUESTS_DIR.joinpath(method + "-" + example + ".xml"), "w"
                    ) as f:
                        f.write(example_xml)

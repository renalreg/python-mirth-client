from pathlib import Path
from uuid import UUID
from mirth_client.models import ChannelMessageModel, MirthDatetime

CHANNEL_MESSAGE_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-message.xml")
    .read_text()
)

CHANNEL_MESSAGE_RESPONSE_ERROR = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-message.error.xml")
    .read_text()
)


def test_xml_to_obj():
    response = ChannelMessageModel.parse_raw(CHANNEL_MESSAGE_RESPONSE)
    assert response == {
        "message_id": 1,
        "server_id": UUID("4975776f-deb5-4ac6-ba3c-60b27198983d"),
        "channel_id": UUID("702dd3c4-4079-4933-8ab2-2a6d5c27e503"),
        "processed": True,
        "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
        "connector_messages": {
            1: {
                "chain_id": 0,
                "order_id": 0,
                "server_id": UUID("681d4d66-f685-4206-b9a9-703a1ea1b1ea"),
                "channel_id": "3781e5ae-f1b3-452b-af60-9b5f08df7279",
                "status": "SENT",
                "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
                "channel_name": "Channel 1",
                "connector_name": None,
                "message_id": "1",
                "error_code": 0,
                "send_attempts": 0,
                "raw": None,
                "encoded": None,
                "sent": None,
                "response": None,
                "meta_data_id": 0,
                "meta_data_map": {},
            }
        },
    }


def test_xml_to_obj_message_with_error():
    response = ChannelMessageModel.parse_raw(CHANNEL_MESSAGE_RESPONSE_ERROR)
    assert response == {
        "message_id": 1,
        "server_id": UUID("176fbc8a-2718-4d78-beee-7530ec068ee9"),
        "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
        "processed": True,
        "received_date": MirthDatetime(2022, 2, 1, 10, 7, 47, 490000),
        "connector_messages": {
            0: {
                "chain_id": 0,
                "order_id": 0,
                "server_id": UUID("176fbc8a-2718-4d78-beee-7530ec068ee9"),
                "channel_id": "0288e3d8-e7f6-49de-91a3-53223c807893",
                "status": "TRANSFORMED",
                "received_date": MirthDatetime(2022, 2, 1, 10, 7, 47, 490000),
                "channel_name": "Outbound Error Channel",
                "connector_name": "Source",
                "message_id": "1",
                "error_code": 0,
                "send_attempts": 1,
                "raw": {
                    "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
                    "content": '<?xml version="1.0" encoding="UTF-8" ?>\n<root>\n  <shelf>\n    <air>count</air>\n    <outside>\n      <effort>coffee</effort>\n      <distant>-386193605.22669554</distant>\n    </outside>\n  </shelf>\n  <try>rate</try>\n</root>',
                    "content_type": "RAW",
                    "data_type": "XML",
                    "encrypted": False,
                    "message_id": "1",
                    "message_data_id": None,
                },
                "encoded": {
                    "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
                    "content": '<?xml version="1.0" encoding="UTF-8" ?>\n<root>\n  <shelf>\n    <air>count</air>\n    <outside>\n      <effort>coffee</effort>\n      <distant>-386193605.22669554</distant>\n    </outside>\n  </shelf>\n  <try>rate</try>\n</root>',
                    "content_type": "ENCODED",
                    "data_type": "XML",
                    "encrypted": False,
                    "message_id": "1",
                    "message_data_id": None,
                },
                "sent": None,
                "response": None,
                "meta_data_id": 0,
                "meta_data_map": {},
            },
            1: {
                "chain_id": 1,
                "order_id": 1,
                "server_id": UUID("176fbc8a-2718-4d78-beee-7530ec068ee9"),
                "channel_id": "0288e3d8-e7f6-49de-91a3-53223c807893",
                "status": "ERROR",
                "received_date": MirthDatetime(2022, 2, 1, 10, 7, 47, 501000),
                "channel_name": "Outbound Error Channel",
                "connector_name": "Error Generator",
                "message_id": "1",
                "error_code": 1,
                "send_attempts": 1,
                "raw": {
                    "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
                    "content": '<?xml version="1.0" encoding="UTF-8" ?>\n<root>\n  <shelf>\n    <air>count</air>\n    <outside>\n      <effort>coffee</effort>\n      <distant>-386193605.22669554</distant>\n    </outside>\n  </shelf>\n  <try>rate</try>\n</root>',
                    "content_type": "RAW",
                    "data_type": "XML",
                    "encrypted": False,
                    "message_id": "1",
                    "message_data_id": None,
                },
                "encoded": {
                    "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
                    "content": '<?xml version="1.0" encoding="UTF-8" ?>\n<root>\n  <shelf>\n    <air>count</air>\n    <outside>\n      <effort>coffee</effort>\n      <distant>-386193605.22669554</distant>\n    </outside>\n  </shelf>\n  <try>rate</try>\n</root>',
                    "content_type": "ENCODED",
                    "data_type": "XML",
                    "encrypted": False,
                    "message_id": "1",
                    "message_data_id": None,
                },
                "sent": {
                    "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
                    "content": '<com.mirth.connect.connectors.js.JavaScriptDispatcherProperties version="3.12.0">\n  <pluginProperties/>\n  <destinationConnectorProperties version="3.12.0">\n    <queueEnabled>false</queueEnabled>\n    <sendFirst>false</sendFirst>\n    <retryIntervalMillis>10000</retryIntervalMillis>\n    <regenerateTemplate>false</regenerateTemplate>\n    <retryCount>0</retryCount>\n    <rotate>false</rotate>\n    <includeFilterTransformer>false</includeFilterTransformer>\n    <threadCount>1</threadCount>\n    <threadAssignmentVariable></threadAssignmentVariable>\n    <validateResponse>false</validateResponse>\n    <resourceIds class="linked-hash-map">\n      <entry>\n        <string>Default Resource</string>\n        <string>[Default Resource]</string>\n      </entry>\n    </resourceIds>\n    <queueBufferSize>1000</queueBufferSize>\n    <reattachAttachments>true</reattachAttachments>\n  </destinationConnectorProperties>\n  <script>throw Error(&quot;Test Error&quot;);</script>\n</com.mirth.connect.connectors.js.JavaScriptDispatcherProperties>',
                    "content_type": "SENT",
                    "data_type": None,
                    "encrypted": False,
                    "message_id": "1",
                    "message_data_id": None,
                },
                "response": {
                    "channel_id": UUID("0288e3d8-e7f6-49de-91a3-53223c807893"),
                    "content": "<response>\n  <status>ERROR</status>\n  <message></message>\n  <error>JavaScript Writer error\nERROR MESSAGE: Error evaluating JavaScript Writer\ncom.mirth.connect.server.MirthJavascriptTransformerException: \nCHANNEL:\tOutbound Error Channel\nCONNECTOR:\tError Generator\nSCRIPT SOURCE:\tJavaScript Writer\nSOURCE CODE:\t\n94:         }\n95:         eval(&apos;importPackage(&apos; + Packages.java.lang.Class.forName(className).getPackage().getName() + &apos;)&apos;);\n96:     }\n97: }\n98: function doScript() {\n99: throw Error(&quot;Test Error&quot;); \n100: }\nLINE NUMBER:\t99\nDETAILS:\tError: Test Error\n\tat d9de4386-893e-474c-95bc-9947dab1904c:99 (doScript)\n\tat d9de4386-893e-474c-95bc-9947dab1904c:101\n\tat com.mirth.connect.connectors.js.JavaScriptDispatcher$JavaScriptDispatcherTask.doCall(JavaScriptDispatcher.java:265)\n\tat com.mirth.connect.connectors.js.JavaScriptDispatcher$JavaScriptDispatcherTask.doCall(JavaScriptDispatcher.java:190)\n\tat com.mirth.connect.server.util.javascript.JavaScriptTask.call(JavaScriptTask.java:113)\n\tat java.base/java.util.concurrent.FutureTask.run(Unknown Source)\n\tat java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(Unknown Source)\n\tat java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(Unknown Source)\n\tat java.base/java.lang.Thread.run(Unknown Source)\n</error>\n  <statusMessage>Error evaluating JavaScript Writer [JavaScriptException: Error: Test Error (d9de4386-893e-474c-95bc-9947dab1904c#99)]</statusMessage>\n</response>",
                    "content_type": "RESPONSE",
                    "data_type": "XML",
                    "encrypted": False,
                    "message_id": "1",
                    "message_data_id": None,
                },
                "meta_data_id": 1,
                "meta_data_map": {},
            },
        },
    }

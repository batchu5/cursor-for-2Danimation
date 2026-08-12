from datetime import datetime
import json

# Your raw video group data
data = [
    [
        {
            "prompt": "Subhan Allah",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752757047/rgvrjkilp5axd6ouxd7a.mp4",
            "conversationId": "307c7468-0632-4acf-a0fd-0af04070632a",
            "timestamp": "2025-07-17T12:57:00.352000"
        },
        {
            "prompt": "Nice to meet you",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752757035/wnzrqg8hhu8iwkzomdqu.mp4",
            "conversationId": "307c7468-0632-4acf-a0fd-0af04070632a",
            "timestamp": "2025-07-17T12:56:48.437000"
        },
        {
            "prompt": "Add",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752757024/k5fyyecxxap50euu0iuw.mp4",
            "conversationId": "307c7468-0632-4acf-a0fd-0af04070632a",
            "timestamp": "2025-07-17T12:56:35.320000"
        }
    ],
    [
        {
            "prompt": "Damn sure",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752757124/mswyl5goj031cjtckh5k.mp4",
            "conversationId": "06681ecb-ab23-4d56-92d4-ae47d4b0cd64",
            "timestamp": "2025-07-17T12:58:15.567000"
        },
        {
            "prompt": "namasthe madam",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752757112/sdijypd40g4imqhmabwt.mp4",
            "conversationId": "06681ecb-ab23-4d56-92d4-ae47d4b0cd64",
            "timestamp": "2025-07-17T12:58:04.915000"
        }
    ],
    [
        {
            "prompt": "Hii da",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752804367/x91a8mzgpqeggmae8kro.mp4",
            "conversationId": "",
            "timestamp": "2025-07-18T02:05:39.705000"
        },
        {
            "prompt": "Hii",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752804356/h9yxtft1xrgwr6d2rlyt.mp4",
            "conversationId": "",
            "timestamp": "2025-07-18T02:05:26.452000"
        },
        {
            "prompt": "adlknsa",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752777257/phtfxxm433bb5yo8hylb.mp4",
            "conversationId": "",
            "timestamp": "2025-07-17T18:33:50.568000"
        },
        {
            "prompt": "adlkn",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752777178/n39mdohq45orsxmf4cji.mp4",
            "conversationId": "",
            "timestamp": "2025-07-17T18:32:26.701000"
        }
    ],
    [
        {
            "prompt": "Namasthe",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752804788/aplrryeeztqbf4xjhzbh.mp4",
            "conversationId": "8995ddbf-7731-4979-8270-4ae87b672160",
            "timestamp": "2025-07-18T02:12:41.002000"
        },
        {
            "prompt": "Hii",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752804776/nw5zcejcx3qwc9or7hpq.mp4",
            "conversationId": "8995ddbf-7731-4979-8270-4ae87b672160",
            "timestamp": "2025-07-18T02:12:27.902000"
        }
    ],
    [
        {
            "prompt": "is a bitch",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752804872/dcvpbbwqwj3kvq8puyuh.mp4",
            "conversationId": "740bb59f-b7b4-4217-87d2-4da4d65765f0",
            "timestamp": "2025-07-18T02:14:05.150000"
        },
        {
            "prompt": "uday",
            "url": "https://res.cloudinary.com/dxmkpoe7j/video/upload/v1752804860/wtf3wjfsnocg7boxp798.mp4",
            "conversationId": "740bb59f-b7b4-4217-87d2-4da4d65765f0",
            "timestamp": "2025-07-18T02:13:52.883000"
        }
    ]
]

# Step 1: Sort inner groups (videos inside each group) by timestamp ASCENDING (oldest first)
for group in data:
    group.sort(key=lambda video: datetime.fromisoformat(video['timestamp']))

# Step 2: Sort outer groups by the most recent timestamp in each group DESCENDING (most recent group first)
data.sort(
    key=lambda group: max(datetime.fromisoformat(video['timestamp']) for video in group),
    reverse=True
)

# Step 3: Print the final result
print(json.dumps(data, indent=2))

cat > train.json <<EOF
{
    "data":[
        {
            "sentence": "I went to London and Berlin.",
            "entities":[
                {
                    "start":10,
                    "end": 16,
                    "tag": "LOC"
                },
                {
                    "start":21,
                    "end": 27,
                    "tag": "LOC"
                }
                ]
        },
        {
            "sentence":"Who is Donald Trump?",
            "entities":[
                {
                    "start":7,
                    "end": 19,
                    "tag": "PERSON"
                }
            ]
        }

    ]
}
EOF
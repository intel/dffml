cat >> train.json << EOF
{
    "data":[
       {
          "title":"University_of_Notre_Dame",
          "paragraphs":[
             {
                "context":"Architecturally, the school has a Catholic character. Atop the Main Building's gold dome is a golden statue of the Virgin Mary. Immediately in front of the Main Building and facing it, is a copper statue of Christ with arms upraised with the legend \"Venite Ad Me Omnes\". Next to the Main Building is the Basilica of the Sacred Heart. Immediately behind the basilica is the Grotto, a Marian place of prayer and reflection. It is a replica of the grotto at Lourdes, France where the Virgin Mary reputedly appeared to Saint Bernadette Soubirous in 1858. At the end of the main drive (and in a direct line that connects through 3 statues and the Gold Dome), is a simple, modern stone statue of Mary.",
                "qas":[
                   {
                      "answers":[
                         {
                            "answer_start":515,
                            "text":"Saint Bernadette Soubirous"
                         }
                      ],
                      "question":"To whom did the Virgin Mary allegedly appear in 1858 in Lourdes France?",
                      "id":"5733be284776f41900661182"
                   },
                   {
                      "answers":[
                         {
                            "answer_start":188,
                            "text":"a copper statue of Christ"
                         }
                      ],
                      "question":"What is in front of the Notre Dame Main Building?",
                      "id":"5733be284776f4190066117f"
                   },
                   {
                      "answers":[
                         {
                            "answer_start":279,
                            "text":"the Main Building"
                         }
                      ],
                      "question":"The Basilica of the Sacred heart at Notre Dame is beside to which structure?",
                      "id":"5733be284776f41900661180"
                   },
                   {
                      "answers":[
                         {
                            "answer_start":381,
                            "text":"a Marian place of prayer and reflection"
                         }
                      ],
                      "question":"What is the Grotto at Notre Dame?",
                      "id":"5733be284776f41900661181"
                   },
                   {
                      "answers":[
                         {
                            "answer_start":92,
                            "text":"a golden statue of the Virgin Mary"
                         }
                      ],
                      "question":"What sits on top of the Main Building at Notre Dame?",
                      "id":"5733be284776f4190066117e"
                   }
                ]
             }
          ]
       }
    ]
 }
EOF
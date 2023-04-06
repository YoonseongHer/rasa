# chatbot engine

## RUN
    python3 myown_chatbot.py
    
## requirements
    python==3.6.13
    greenlet==1.1.2
    spacy==3.3.0
    rasa-nlu==0.13.2
    rasa_core==0.11.1
    scipy==1.5.2
    konlpy==0.6.0
    py-hanspell==1.1
    sklearn-crfsuite==0.3.6
    
## structure
```
├── feature
│   ├── Answer.py                   // ANSWER JSON DATA creater
│   ├── AnswerClassification.py     
│   ├── Chatbot.py                  // CHATBOT DATA, CHAT DATA parser
│   ├── Model.py                    // train, predict AI model
│   ├── TextPreprocessing.py        // TEXT preprocessing module
│   └── Tohtml.py                   // for test
│
├── bots
│   └── chatbot
│       ├── metadata.json
│       ├── model  
│       └── response
│
├── config.yml
└── myown_chatbot.py
```

## API

#### /webhooks/rasa/button
* `POST` : get a response

#### /webhooks/rasa/deploy
* `POST` : create a chatbot

#### /webhooks/rasa/delete/{chatbot_id}
* `DELETE` : delete chatbot
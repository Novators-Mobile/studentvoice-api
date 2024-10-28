import googleapiclient.errors
from apiclient import discovery
from google.oauth2 import service_account
from threading import Lock


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]


class GoogleFormsWorker(metaclass=SingletonMeta):
    SCOPES = ['https://www.googleapis.com/auth/forms.body', 'https://www.googleapis.com/auth/drive']

    def __init__(self):
        creds = service_account.Credentials.from_service_account_file("polls/polls-creds.json", scopes=self.SCOPES)
        self.service = discovery.build(
            "forms",
            "v1",
            credentials=creds
        )

    def create_form(self):
        new_form_request = {
            "info": {
                "title": "Оценка пары",
            }
        }
        options = [
            {
                "value": "1"
            },
            {
                "value": "2"
            },
            {
                "value": "3"
            },
            {
                "value": "4"
            },
            {
                "value": "5"
            }
        ]
        form_items = [
            {
                "title": "Насколько информативным было содержание пары?",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": 1,  # RADIO type
                            "options": options,
                            "shuffle": False
                        }
                    }
                },
            },
            {
                "title": "Насколько понятно и доступно преподаватель донёс информацию?",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": 1,  # RADIO type
                            "options": options,
                            "shuffle": False
                        }
                    }
                },
            },
            {
                "title": "Как бы вы оценили взаимодействие преподавателя со студентами (дискусии, ответы на "
                         "возникавшие вопросы, интерактивы и т.д.)?",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": 1,  # RADIO type
                            "options": options,
                            "shuffle": False
                        }
                    }
                },
            },
            {
                "title": "Как сильно вас заинтересовал материал занятия?",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": 1,  # RADIO type
                            "options": options,
                            "shuffle": False
                        }
                    }
                },
            },
            {
                "title": "Как бы вы оценили подачу материала (насколько уверенным и подробным чувствовал себя "
                         "преподаватель?",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": 1,  # RADIO type
                            "options": options,
                            "shuffle": False
                        }
                    }
                },
            },
            {
                "title": "Опишите подробнее позитивные впечатления от занятия и чем они были вызваны",
                "questionItem": {
                    "question": {
                        "required": False,
                        "textQuestion": {
                            "paragraph": False
                        }
                    }
                }
            },
            {
                "title": "Опишите подробнее негативные впечатления от занятия и чем они были вызваны",
                "questionItem": {
                    "question": {
                        "required": False,
                        "textQuestion": {
                            "paragraph": False
                        }
                    }
                }
            }
        ]
        create_request = {
            "requests": [{"createItem": {"item": x, "location": {"index": y}}} for y, x in enumerate(form_items)]
        }
        try:
            form = self.service.forms().create(body=new_form_request).execute()
            self.service.forms().batchUpdate(formId=form["formId"], body=create_request).execute()
            return form["formId"], form["responderUri"]
        except googleapiclient.errors.Error:
            return None, None

    def delete_form(self, form_id: str):
        pass


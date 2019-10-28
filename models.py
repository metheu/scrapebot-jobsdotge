from peewee import *

db = SqliteDatabase("vacancy.db")


def create_tables():
    with db:
        db.create_tables([Vacancy])


class BaseModel(Model):
    class Meta:
        database = db


class Vacancy(BaseModel):
    vac_id = AutoField(unique=True)
    vacancy_title = CharField()
    rating = IntegerField()
    vacancy_list_id = IntegerField(unique=True)
    notification_sent = DateTimeField(null=True)




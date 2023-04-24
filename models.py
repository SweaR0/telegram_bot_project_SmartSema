from peewee import *

db = SqliteDatabase('statistics.db')  # база данных


class Userinf(Model):
    id = TextField()
    chat_id = TextField()
    first_name = TextField()
    last_name = TextField()
    username = TextField()
    wikipedia = IntegerField()
    calculator = IntegerField()
    currency_converter = IntegerField()
    black_white_photo = IntegerField()
    game = IntegerField()
    random_number = IntegerField()
    random_word = IntegerField()
    game_dice = IntegerField()
    basketball = IntegerField()
    football = IntegerField()
    bowling = IntegerField()
    darts = IntegerField()
    slot_machine = IntegerField()

    class Meta:
        database = db
        order_by = 'id'
        db_table = 'user_inf'
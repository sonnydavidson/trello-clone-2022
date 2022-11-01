from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config ['JSON_SORT_KEYS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pyscopg2://trello_dev:password123@127.0.0.1:5432/trello'

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

class User(db.model):
    __talename__ = 'users'
    id = db.column(db.integer, primary_key=True)
    name = db.column(db.string)
    email = db.column(db.string, nullable=False, unique=True)
    password = db.column(db.string, ullable=False)
    is_admin = db.column(db.boolean, default = False)

class UserSchema(ma.schema):
    class Meta:
        fields = ('id', 'name', 'email', 'is_admin')


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.date)
    status = db.Column(db.String)
    priority = db.Column(db.String)

class CardSchema(ma.Schema):
    class Meta:
        feilds = ('id', 'title', 'description', 'status', 'priority', 'date')
        ordered = True


# Define custom CLI terminal comman 
@app.cli.command('create')
def create_db():
    db.create_all()
    print('Tables created successfully')

@app.cli.command('drop')
def drop_db():
    db.drop.all()
    print('tables dropped')

@app.cli.command('seed')
def seed_db():
    users = [
        User(
            email="admin@spam.com",
            password=bcrypt.generate_password_hash("eggs").decode("utf-8")
            is_admin=True
        ),
        User(
            name="Sonny Davidson",
            email="someone@spam.com",
            password =bcrypt.generate_password_hash("12345").decode("utf-8")
        )
    ]

    cards = [
        Card(
            title = 'start the project',
            description = 'stage 1 - Creating the database',
            status = 'to do',
            priority ='high',
            data = date.today()
        ),
        Card(
            title = 'SQLALchemy',
            description = 'stage 2 -   ',
            status = 'ongoing',
            priority ='high ',
            data = date.today()
        ),
        Card(
            title = 'ORM Queries',
            description = 'stage 3 - implement several queries ',
            status = 'ongoing',
            priority ='medium',
            data = date.today()
        ),
        Card(
            title = 'Marshmello',
            description = 'stage 4 a implement marshmellow to jsonfiy models',
            status = 'ongoing',
            priority ='medium',
            data = date.today()
        )
    ]

    db.session.add_all(cards)
    db.session.add.all(users)
    db.session.commit()
    print('table seeded')


@app.route('/cards/')
def all_cards():
    # cards = Card.query.all() 
    # print(cards[0].__dict__)
    # stmt = db.select(Card).where(Card.status == 'To Do ')
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt).all()
    return CardSchema(many=True).dump(cards)

@app.cli.command('first_card')
def first_card():
    stmt = db.select(Card).limit(1)
    card = db.session.scalar(stmt)
    print(card.__dict__)


@app.cli.command('count_ongoing')
def count_ongoing():
    stmt = db.select(db.func.count()).select_from(Card).filter_by(status='Ongoing')
    cards = db.session.scalar(stmt)
    print(cards)


 

@app.route('/')
def index():
    return "hello world!"

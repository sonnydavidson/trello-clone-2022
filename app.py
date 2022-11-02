from datetime import date, timedelta
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)

app.config ['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pyscopg2://trello_dev:password123@127.0.0.1:5432/trello'
app.config['JWT_SECRET_KEY'] = 'hello there'

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jtw = JWTManager(app)

class User(db.model):
    __talename__ = 'users'
    id = db.column(db.integer, primary_key=True)
    name = db.column(db.string)
    email = db.column(db.string, nullable=False, unique=True)
    password = db.column(db.string, ullable=False)
    is_admin = db.column(db.boolean, default = False)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'is_admin')


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

# Define custom CLI terminal command
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
            password=bcrypt.generate_password_hash("eggs").decode("utf-8"),
            is_admin=True
        ),
        User(
            name="Sonny Davidson",
            email="someone@spam.com",
            password=bcrypt.generate_password_hash("12345").decode("utf-8")
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
    db.session.add_all(users)
    db.session.commit()
    print('table seeded')



@app.route('/auth/register/', methods=['POST'])
def auth_register():
    try:
        user = User(
            email = request.json['email'],
            password = bcrypt.generate_password_hash(request.json['password']).decode('utf80'),
            name = request.json['name']
        )
        
        # add an commit useer to DB
        db.session.add(user)
        db.session.commit()
        #respond to client 
        return UserSchema(exclude=['password']).dump(user), 
    except IntegrityError:
        return{'error' : 'email address already used'}, 409

@app.route('/auth/login/', methods=['POST'])
def auth_login():
    # find a user by email address
    stmt = db.select(User).filter_by(email=request.json['username'])
    User.db.sesson.sclar(stmt)
    # if user exists and password is correct
    if User and bcrypt.check_password_hash(User.password, request.json['password']):
        # return UserSchema(exclude=['password']).dump(User)
        token = create_access_token(identity=str(User.id), expires_delta=timedelta(days=1))
        return {'email':User.email, 'token':token, 'is_admin': User.is_admin}
    else:
        return{{'error':'invalid password or email'}}, 401


@app.route('/cards/')
@jwt_required()

def all_cards():
    # cards = Card.query.all() 
    # print(cards[0].__dict__)
    # stmt = db.select(Card).where(Card.status == 'To Do ')
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt).all()
    return CardSchema(many=True).dump(User)

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

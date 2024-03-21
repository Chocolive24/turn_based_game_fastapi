import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from peewee import *

app = FastAPI()
database_name = os.environ.get("POSTGRES_DB", "my_data_base")
user_name = os.environ.get("POSTGRES_USER", "olivier")
password = os.environ.get("POSTGRES_PASSWORD", "1234")
host = os.environ.get("POSTGRES_HOST", "localhost")

psql_db = PostgresqlDatabase(database_name, user=user_name,
                             password=password, host=host)


class PsqlModel(Model):
    class Meta:
        database = psql_db


class PlayerModel(PsqlModel):
    name = CharField()


class GameModel(PsqlModel):
    name = CharField()


with psql_db:  # connect
    psql_db.create_tables([PlayerModel, GameModel])
# close.


class Player(BaseModel):
    name: str


class Game(BaseModel):
    name: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/players")
async def get_players():
    players = list(PlayerModel.select().dicts())
    return players


@app.get("/games")
async def get_games():
    games = list(GameModel.select().dicts())
    return games


@app.post("/players")
async def create_player(player: Player):
    new_player = PlayerModel.create(name=player.name)
    return {"message": f"successfully created player : {new_player.name}"}


@app.post("/games")
async def create_game(game: Game):
    new_game = GameModel.create(name=game.name)
    print("post a new game : ", game)
    return {"message": f"successfully created a new game : {new_game.name}"}


@app.middleware("http")
async def db_connection_handler(request: Request, call_next):
    psql_db.connect()
    response = await call_next(request)
    psql_db.close()
    return response



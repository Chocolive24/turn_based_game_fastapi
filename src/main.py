import os
from fastapi import FastAPI, Request, HTTPException
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
    name = CharField(primary_key=True)
    elo = IntegerField()


class GameModel(PsqlModel):
    name = CharField()


with psql_db:  # connect
    psql_db.create_tables([PlayerModel, GameModel])
# close.


class Player(BaseModel):
    name: str = PrimaryKeyField()
    elo: int


class EloGain(BaseModel):
    gain: int


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
    players = list(PlayerModel.select(PlayerModel.name, PlayerModel.elo).dicts())
    return players


@app.get("/player/{name}")
async def get_player(name: str):
    player = list(PlayerModel.select(PlayerModel.name, PlayerModel.elo).where(PlayerModel.name == name).dicts())
    if not player:
        raise HTTPException(status_code=404, detail=f"No player named : {name}")
    return player


@app.get("/player/{name}/elo")
async def get_player(name: str):
    player = list(PlayerModel.select(PlayerModel.elo).where(PlayerModel.name == name).dicts())
    if not player:
        raise HTTPException(status_code=404, detail=f"No player named : {name}")
    return player


@app.get("/games")
async def get_games():
    games = list(GameModel.select().dicts())
    return games


@app.post("/player")
async def create_player(player: Player):
    # Check if the player already exists
    try:
        existing_player = PlayerModel.get(PlayerModel.name == player.name)
        # If player already exists, return a message indicating the same
        return {"message": f"Player {existing_player.name} already exists."}
    except PlayerModel.DoesNotExist:
        # If player doesn't exist, create a new one
        new_player = PlayerModel.create(name=player.name, elo=player.elo)
        return {"message": f"Successfully created player: {new_player.name}"}


@app.post("/games")
async def create_game(game: Game):
    new_game = GameModel.create(name=game.name)
    print("post a new game : ", game)
    return {"message": f"successfully created a new game : {new_game.name}"}


@app.post("/player/{name}")
async def update_player_elo(name: str, elo_gain: EloGain):
    try:
        player = PlayerModel.get(PlayerModel.name == name)
        player.elo += elo_gain.gain
        player.save()
        return {"message": f"ELO for player {name} updated successfully"}
    except PlayerModel.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"No player named: {name}")


@app.middleware("http")
async def db_connection_handler(request: Request, call_next):
    psql_db.connect()
    response = await call_next(request)
    psql_db.close()
    return response



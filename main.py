from fastapi import Depends, FastAPI, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import pandas as pd
from io import StringIO
import json
from fastapi.responses import StreamingResponse


Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    player_id = Column(String, unique=True, nullable=False)


class Level(Base):
    __tablename__ = 'levels'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    order = Column(Integer, default=0)


class Prize(Base):
    __tablename__ = 'prizes'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)


class PlayerLevel(Base):
    __tablename__ = 'player_levels'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    level_id = Column(Integer, ForeignKey('levels.id'), nullable=False)
    completed = Column(Date, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    score = Column(Integer, default=0)


class LevelPrize(Base):
    __tablename__ = 'level_prizes'
    id = Column(Integer, primary_key=True)
    level_id = Column(Integer, ForeignKey('levels.id'), nullable=False)
    prize_id = Column(Integer, ForeignKey('prizes.id'), nullable=False)
    received = Column(Date, default=datetime.utcnow)


app = FastAPI()

engine = create_engine('sqlite:///game_prize.db')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/assign_prize/")
async def assign_prize(request: Request, db: Session = Depends(get_db)):
    try:
        request_json = await request.json()
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=405, detail="Ошибка в чтении JSON.")

    # print(request_json)
    player_id = request_json.get("player_id")
    level_id = request_json.get("level_id")
    prize_id = request_json.get("prize_id")

    if not player_id or not level_id or not prize_id:
        raise HTTPException(status_code=405, detail="Параметры указаны не верно.")

    player = db.query(Player).filter_by(id=player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Игрок не найден.")

    level = db.query(Level).filter_by(id=level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Уровень не найден.")

    prize = db.query(Prize).filter_by(id=prize_id).first()
    if not prize:
        raise HTTPException(status_code=404, detail="Приз не найден.")

    player_level = db.query(PlayerLevel).filter_by(player_id=player_id, level_id=level_id).first()
    if not player_level:
        raise HTTPException(status_code=404, detail="PlayerLevel не найден.")
    elif not player_level.is_completed:
        raise HTTPException(status_code=400, detail="Игрок не завершил уровень.")

    level_prize = LevelPrize(level_id=level_id, prize_id=prize_id)
    db.add(level_prize)
    db.commit()
    return {"message": f"Приз '{prize_id}' получен за уровень '{level_id}'."}


@app.get("/export_csv/")
async def export_csv(db: Session = Depends(get_db)):
    query = db.query(Player.id.label("player_id"), Level.title.label("level_title"), PlayerLevel.is_completed,
                     Prize.title.label("prize_title")) \
        .join(PlayerLevel, Player.id == PlayerLevel.player_id) \
        .join(Level, PlayerLevel.level_id == Level.id) \
        .outerjoin(LevelPrize, Level.id == LevelPrize.level_id) \
        .outerjoin(Prize, LevelPrize.prize_id == Prize.id)

    df = pd.read_sql(query.statement, db.bind)
    csv_data = StringIO()
    df.to_csv(csv_data, index=False)
    csv_data.seek(0)

    return StreamingResponse(csv_data, media_type="text/csv",
                             headers={"Content-Disposition": "attachment;filename=data.csv"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.35", port=8000)

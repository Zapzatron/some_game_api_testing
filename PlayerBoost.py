from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_login = Column(DateTime, default=datetime.utcnow)
    points = Column(Integer, default=0)
    boosts = relationship('PlayerBoost', back_populates='player')

    def __repr__(self):
        return f"<Player(username='{self.username}', first_login='{self.first_login}', points='{self.points}')>"

    @classmethod
    def get_by_name(cls, session, username, need_to_raise=True):
        player = session.query(cls).filter_by(username=username).first()

        if isinstance(player, cls):
            return player
        else:
            if need_to_raise:
                raise Exception(f"Игрок '{username}' не найден.")
            else:
                return None

    @classmethod
    def add_new(cls, session, username):
        if not cls.get_by_name(session, username, need_to_raise=False):
            new_player = cls(username=username)
            session.add(new_player)
            session.commit()
        else:
            raise Exception(f"Игрок '{username}' уже существует.")

    def get_info(self):
        return self.first_login, self.id, self.username, self.boosts


class Boost(Base):
    __tablename__ = 'boosts'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # в секундах
    players = relationship('PlayerBoost', back_populates='boost')

    def __repr__(self):
        return f"<Boost(name='{self.name}', description='{self.description}', duration='{self.duration}')>"

    @classmethod
    def get_by_name(cls, session, boost_name, need_to_raise=True):
        boost = session.query(cls).filter_by(name=boost_name).first()

        if isinstance(boost, cls):
            return boost
        else:
            if need_to_raise:
                raise Exception(f"Буст '{boost_name}' не найден.")
            else:
                return None

    @classmethod
    def add_new(cls, session, boost_name, boost_description, boost_duration):
        if not cls.get_by_name(session, boost_name, need_to_raise=False):
            new_boost = Boost(name=boost_name, description=boost_description, duration=boost_duration)
            session.add(new_boost)
            session.commit()
        else:
            raise Exception(f"Буст '{boost_name}' уже существует.")


class PlayerBoost(Base):
    __tablename__ = 'player_boosts'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    boost_id = Column(Integer, ForeignKey('boosts.id'), nullable=False)
    acquired_at = Column(DateTime, default=datetime.utcnow)

    player = relationship('Player', back_populates='boosts')
    boost = relationship('Boost', back_populates='players')

    def __repr__(self):
        return f"<PlayerBoost(player_id='{self.player_id}', boost_id='{self.boost_id}', acquired_at='{self.acquired_at}')>"

    @classmethod
    def add_boost_to_player(cls, session, player_id, boost_id):
        player_boost = PlayerBoost(player_id=player_id, boost_id=boost_id)
        session.add(player_boost)
        session.commit()


if __name__ == "__main__":
    # Используется sqlite, но можно переделать на PostgreSQL
    engine = create_engine('sqlite:///game.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Player
    player_name = "player1"

    Player.add_new(session, player_name)

    cur_player = Player.get_by_name(session, player_name)

    print(cur_player)

    player_first_login, player_id, player_username, player_boosts = cur_player.get_info()

    print(player_first_login, player_id, player_username, player_boosts)

    # Boost
    boost_name = "Speed Boost"
    boost_description = "Increases speed by 50%"
    boost_duration = 3600

    Boost.add_new(session, boost_name, boost_description, boost_duration)

    cur_boost = Boost.get_by_name(session, boost_name)

    # Добавление Boost к Player
    PlayerBoost.add_boost_to_player(session, cur_player.id, cur_boost.id)

    print(cur_player.boosts)

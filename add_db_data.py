from sqlalchemy.orm import Session
from main import engine, Player, Level, Prize, PlayerLevel

session = Session(bind=engine)

new_player = Player(player_id="test_player")
session.add(new_player)
session.commit()

new_level = Level(title="test_level")
session.add(new_level)
session.commit()

new_prize = Prize(title="test_prize")
session.add(new_prize)
session.commit()

player_level = PlayerLevel(player_id=new_player.id, level_id=new_level.id, is_completed=True, score=100)
session.add(player_level)
session.commit()

session.close()

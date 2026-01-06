from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class GameGenre(Base):
    __tablename__ = 'game_genres'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

class CharacterArchetype(Base):
    __tablename__ = 'character_archetypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    genre_id = Column(Integer, ForeignKey('game_genres.id'))
    genre = relationship('GameGenre', backref='archetypes')

class SkillTree(Base):
    __tablename__ = 'skill_trees'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    archetype_id = Column(Integer, ForeignKey('character_archetypes.id'))
    archetype = relationship('CharacterArchetype', backref='skill_trees')
    description = Column(Text)

class StatSystem(Base):
    __tablename__ = 'stat_systems'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    archetype_id = Column(Integer, ForeignKey('character_archetypes.id'))
    archetype = relationship('CharacterArchetype', backref='stat_systems')

class DesignerProfile(Base):
    __tablename__ = 'designer_profiles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    experience_years = Column(Integer)
    favorite_genre_id = Column(Integer, ForeignKey('game_genres.id'))
    favorite_genre = relationship('GameGenre')
    bio = Column(Text)

class InterviewQuestion(Base):
    __tablename__ = 'interview_questions'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    category = Column(String(100))
    difficulty = Column(String(50))
    archetype_id = Column(Integer, ForeignKey('character_archetypes.id'), nullable=True)
    archetype = relationship('CharacterArchetype')

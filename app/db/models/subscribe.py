from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import Session

from app.db.models import Base
from app.schemas import MediaType


class Subscribe(Base):
    """
    订阅表
    """
    id = Column(Integer, Sequence('id'), primary_key=True, index=True)
    # 标题
    name = Column(String, nullable=False, index=True)
    # 年份
    year = Column(String)
    # 类型
    type = Column(String)
    # 搜索关键字
    keyword = Column(String)
    tmdbid = Column(Integer, index=True)
    imdbid = Column(String)
    tvdbid = Column(Integer)
    doubanid = Column(String, index=True)
    # 季号
    season = Column(Integer)
    # 海报
    poster = Column(String)
    # 背景图
    backdrop = Column(String)
    # 评分
    vote = Column(Integer)
    # 简介
    description = Column(String)
    # 过滤规则
    filter = Column(String)
    # 包含
    include = Column(String)
    # 排除
    exclude = Column(String)
    # 总集数
    total_episode = Column(Integer)
    # 开始集数
    start_episode = Column(Integer)
    # 缺失集数
    lack_episode = Column(Integer)
    # 附加信息
    note = Column(String)
    # 状态：N-新建， R-订阅中
    state = Column(String, nullable=False, index=True, default='N')
    # 最后更新时间
    last_update = Column(String)
    # 订阅用户
    username = Column(String)

    @staticmethod
    def exists(db: Session, tmdbid: int, season: int = None):
        if season:
            return db.query(Subscribe).filter(Subscribe.tmdbid == tmdbid,
                                              Subscribe.season == season).first()
        return db.query(Subscribe).filter(Subscribe.tmdbid == tmdbid).first()

    @staticmethod
    def get_by_state(db: Session, state: str):
        return db.query(Subscribe).filter(Subscribe.state == state).all()

    @staticmethod
    def get_by_tmdbid(db: Session, tmdbid: int, season: int = None):
        if season:
            return db.query(Subscribe).filter(Subscribe.tmdbid == tmdbid,
                                              Subscribe.season == season).all()
        return db.query(Subscribe).filter(Subscribe.tmdbid == tmdbid).all()

    @staticmethod
    def get_by_title(db: Session, title: str):
        return db.query(Subscribe).filter(Subscribe.name == title).first()

    @staticmethod
    def get_by_doubanid(db: Session, doubanid: str):
        return db.query(Subscribe).filter(Subscribe.doubanid == doubanid).first()

    def delete_by_tmdbid(self, db: Session, tmdbid: int, season: int):
        subscrbies = self.get_by_tmdbid(db, tmdbid, season)
        for subscrbie in subscrbies:
            subscrbie.delete(db, subscrbie.id)
        return True

    def delete_by_doubanid(self, db: Session, doubanid: str):
        subscribe = self.get_by_doubanid(db, doubanid)
        if subscribe:
            subscribe.delete(db, subscribe.id)
        return True

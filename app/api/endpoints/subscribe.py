from typing import List, Any, Optional

from fastapi import APIRouter, Request, BackgroundTasks, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app import schemas
from app.chain.subscribe import SubscribeChain
from app.core.config import settings
from app.core.security import verify_token
from app.db import get_db
from app.db.models.subscribe import Subscribe
from app.db.models.user import User
from app.db.userauth import get_current_active_user
from app.schemas.types import MediaType

router = APIRouter()


def start_subscribe_add(title: str, year: str,
                        mtype: MediaType, tmdbid: int, season: int, username: str):
    """
    启动订阅任务
    """
    SubscribeChain().add(title=title, year=year,
                         mtype=mtype, tmdbid=tmdbid, season=season, username=username)


def start_subscribe_search(sid: Optional[int], state: Optional[str]):
    """
    启动订阅搜索任务
    """
    SubscribeChain().search(sid=sid, state=state, manual=True)


@router.get("/", summary="所有订阅", response_model=List[schemas.Subscribe])
def read_subscribes(
        db: Session = Depends(get_db),
        _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    查询所有订阅
    """
    return Subscribe.list(db)


@router.post("/", summary="新增订阅", response_model=schemas.Response)
def create_subscribe(
        *,
        subscribe_in: schemas.Subscribe,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    新增订阅
    """
    # 类型转换
    if subscribe_in.type:
        mtype = MediaType(subscribe_in.type)
    else:
        mtype = None
    # 标题转换
    if subscribe_in.name:
        title = subscribe_in.name
    else:
        title = None
    sid, message = SubscribeChain().add(mtype=mtype,
                                        title=title,
                                        year=subscribe_in.year,
                                        tmdbid=subscribe_in.tmdbid,
                                        season=subscribe_in.season,
                                        doubanid=subscribe_in.doubanid,
                                        username=current_user.name,
                                        exist_ok=True)
    return schemas.Response(success=True if sid else False, message=message, data={
        "id": sid
    })


@router.put("/", summary="更新订阅", response_model=schemas.Response)
def update_subscribe(
        *,
        subscribe_in: schemas.Subscribe,
        db: Session = Depends(get_db),
        _: schemas.TokenPayload = Depends(verify_token)
) -> Any:
    """
    更新订阅信息
    """
    subscribe = Subscribe.get(db, subscribe_in.id)
    if not subscribe:
        return schemas.Response(success=False, message="订阅不存在")
    subscribe.update(db, subscribe_in.dict())
    return schemas.Response(success=True)


@router.get("/media/{mediaid}", summary="查询订阅", response_model=schemas.Subscribe)
def subscribe_mediaid(
        mediaid: str,
        season: int = None,
        db: Session = Depends(get_db),
        _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    根据TMDBID或豆瓣ID查询订阅 tmdb:/douban:
    """
    if mediaid.startswith("tmdb:"):
        result = Subscribe.exists(db, int(mediaid[5:]), season)
    elif mediaid.startswith("douban:"):
        result = Subscribe.get_by_doubanid(db, mediaid[7:])
    else:
        result = None

    return result if result else Subscribe()


@router.get("/{subscribe_id}", summary="订阅详情", response_model=schemas.Subscribe)
def read_subscribe(
        subscribe_id: int,
        db: Session = Depends(get_db),
        _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    根据订阅编号查询订阅信息
    """
    return Subscribe.get(db, subscribe_id)


@router.delete("/media/{mediaid}", summary="删除订阅", response_model=schemas.Response)
def delete_subscribe_by_mediaid(
        mediaid: str,
        season: int = None,
        db: Session = Depends(get_db),
        _: schemas.TokenPayload = Depends(verify_token)
) -> Any:
    """
    根据TMDBID或豆瓣ID删除订阅 tmdb:/douban:
    """
    if mediaid.startswith("tmdb:"):
        Subscribe().delete_by_tmdbid(db, int(mediaid[5:]), season)
    elif mediaid.startswith("douban:"):
        Subscribe().delete_by_doubanid(db, mediaid[7:])

    return schemas.Response(success=True)


@router.delete("/{subscribe_id}", summary="删除订阅", response_model=schemas.Response)
def delete_subscribe(
        subscribe_id: int,
        db: Session = Depends(get_db),
        _: schemas.TokenPayload = Depends(verify_token)
) -> Any:
    """
    删除订阅信息
    """
    Subscribe.delete(db, subscribe_id)
    return schemas.Response(success=True)


@router.post("/seerr", summary="OverSeerr/JellySeerr通知订阅", response_model=schemas.Response)
def seerr_subscribe(request: Request, background_tasks: BackgroundTasks,
                    authorization: str = Header(None)) -> Any:
    """
    Jellyseerr/Overseerr订阅
    """
    if not authorization or authorization != settings.API_TOKEN:
        raise HTTPException(
            status_code=400,
            detail="授权失败",
        )
    req_json = request.json()
    if not req_json:
        raise HTTPException(
            status_code=500,
            detail="报文内容为空",
        )
    notification_type = req_json.get("notification_type")
    if notification_type not in ["MEDIA_APPROVED", "MEDIA_AUTO_APPROVED"]:
        return schemas.Response(success=False, message="不支持的通知类型")
    subject = req_json.get("subject")
    media_type = MediaType.MOVIE if req_json.get("media", {}).get("media_type") == "movie" else MediaType.TV
    tmdbId = req_json.get("media", {}).get("tmdbId")
    if not media_type or not tmdbId or not subject:
        return schemas.Response(success=False, message="请求参数不正确")
    user_name = req_json.get("request", {}).get("requestedBy_username")
    # 添加订阅
    if media_type == MediaType.MOVIE:
        background_tasks.add_task(start_subscribe_add,
                                  mtype=media_type,
                                  tmdbid=tmdbId,
                                  title=subject,
                                  year="",
                                  season=0,
                                  username=user_name)
    else:
        seasons = []
        for extra in req_json.get("extra", []):
            if extra.get("name") == "Requested Seasons":
                seasons = [int(str(sea).strip()) for sea in extra.get("value").split(", ") if str(sea).isdigit()]
                break
        for season in seasons:
            background_tasks.add_task(start_subscribe_add,
                                      mtype=media_type,
                                      tmdbid=tmdbId,
                                      title=subject,
                                      year="",
                                      season=season,
                                      username=user_name)

    return schemas.Response(success=True)


@router.get("/refresh", summary="刷新订阅", response_model=schemas.Response)
def refresh_subscribes(
        _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    刷新所有订阅
    """
    SubscribeChain().refresh()
    return schemas.Response(success=True)


@router.get("/search/{subscribe_id}", summary="搜索订阅", response_model=schemas.Response)
def search_subscribe(
        subscribe_id: int,
        background_tasks: BackgroundTasks,
        _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    搜索所有订阅
    """
    background_tasks.add_task(start_subscribe_search, sid=subscribe_id, state=None)
    return schemas.Response(success=True)


@router.get("/search", summary="搜索所有订阅", response_model=schemas.Response)
def search_subscribes(
        background_tasks: BackgroundTasks,
        _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    搜索所有订阅
    """
    background_tasks.add_task(start_subscribe_search, sid=None, state='R')
    return schemas.Response(success=True)

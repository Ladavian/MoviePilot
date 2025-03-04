from pathlib import Path
from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.chain.transfer import TransferChain
from app.core.security import verify_token
from app.db import get_db
from app.db.models.downloadhistory import DownloadHistory
from app.db.models.transferhistory import TransferHistory

router = APIRouter()


@router.get("/download", summary="查询下载历史记录", response_model=List[schemas.DownloadHistory])
def download_history(page: int = 1,
                     count: int = 30,
                     db: Session = Depends(get_db),
                     _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    查询下载历史记录
    """
    return DownloadHistory.list_by_page(db, page, count)


@router.delete("/download", summary="删除下载历史记录", response_model=schemas.Response)
def delete_download_history(history_in: schemas.DownloadHistory,
                            db: Session = Depends(get_db),
                            _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    删除下载历史记录
    """
    DownloadHistory.delete(db, history_in.id)
    return schemas.Response(success=True)


@router.get("/transfer", summary="查询转移历史记录", response_model=List[schemas.TransferHistory])
def transfer_history(title: str = None,
                     page: int = 1,
                     count: int = 30,
                     db: Session = Depends(get_db),
                     _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    查询转移历史记录
    """
    if title:
        return TransferHistory.list_by_title(db, title, page, count)
    else:
        return TransferHistory.list_by_page(db, page, count)


@router.delete("/transfer", summary="删除转移历史记录", response_model=schemas.Response)
def delete_transfer_history(history_in: schemas.TransferHistory,
                            delete_file: bool = False,
                            db: Session = Depends(get_db),
                            _: schemas.TokenPayload = Depends(verify_token)) -> Any:
    """
    删除转移历史记录
    """
    # 触发删除事件
    if delete_file:
        history = TransferHistory.get(db, history_in.id)
        if not history:
            return schemas.Response(success=False, msg="记录不存在")
        # 册除文件
        TransferChain().delete_files(Path(history.dest))
    # 删除记录
    TransferHistory.delete(db, history_in.id)
    return schemas.Response(success=True)

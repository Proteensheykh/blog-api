from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

from .. import models, schemas, utils, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostOut])
def read_posts(
    db: Session = Depends(get_db), 
    current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
    ):
    """
    GET /posts/

    Retrieve a list of posts with optional filtering and pagination.

    Query Parameters:
    - limit (int, optional): Maximum number of posts to return. Default: 10
    - skip (int, optional): Number of posts to skip for pagination. Default: 0
    - search (str, optional): Search string to filter posts by title. Default: ""
    - start_date (datetime, optional): Start date for filtering posts. Format: YYYY-MM-DD
    - end_date (datetime, optional): End date for filtering posts. Format: YYYY-MM-DD

    Returns:
    - 200 OK: A list of posts with their like counts
    - 401 Unauthorized: If the user is not authenticated

    Notes:
    - Requires user authentication
    - Includes the number of likes for each post
    - Date filtering is inclusive of start_date and end_date
    """
    start_date = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_date = datetime.combine(end_date, datetime.max.time()) if end_date else None

    query = db.query(models.Post, func.count(models.Like.post_id).label('likes')).join(
        models.Like, models.Like.post_id == models.Post.id, isouter=True
    ).group_by(models.Post.id)

    if start_date:
        query = query.filter(models.Post.created_at >= start_date)
    if end_date:
        query = query.filter(models.Post.created_at <= end_date)

    results = query.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostOut)
def read_post(id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Like.post_id).label('likes')).join(
        models.Like, models.Like.post_id == models.Post.id, isouter=True
    ).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found.")
        
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found.")
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action.")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(
    id: int, 
    post: schemas.PostCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_update = post_query.first() # Get the post to update

    if post_to_update == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found.")

    if post_to_update.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action.")

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()

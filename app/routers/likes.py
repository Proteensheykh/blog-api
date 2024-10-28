from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from .. import schemas, models, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_like(
    like: schemas.Like,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):

    post = db.query(models.Post).filter(models.Post.id == like.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {like.post_id} does not exist")

    # Query for an existing like
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == like.post_id,
        models.Like.user_id == current_user.id
    ).first()

    if like.dir == 1:
        if existing_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already liked post {like.post_id}")
        
        # Create new like
        new_like = models.Like(post_id=like.post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return {"message": "Successfully added like"}
    else:
        if not existing_like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Like does not exist")
        
        # Remove the like
        db.delete(existing_like)
        db.commit()
        return {"message": "Successfully deleted like"}

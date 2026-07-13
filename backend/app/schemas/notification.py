from pydantic import BaseModel


class NotificationCreate(BaseModel):

    title: str

    message: str

    notification_type: str
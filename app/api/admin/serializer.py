from pydantic import BaseModel, EmailStr


class AdminChangeEmailSerializer(BaseModel):
    new_email: EmailStr

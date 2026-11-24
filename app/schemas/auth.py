from pydantic import BaseModel, ConfigDict, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()

        if "@" not in value or value.count("@") != 1:
            raise ValueError("Invalid email format")

        local, domain = value.split("@")

        if not local or "." not in domain or domain.startswith("."):
            raise ValueError("Invalid email format")

        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    manager_id: int | None
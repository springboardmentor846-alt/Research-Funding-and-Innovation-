from fastapi import HTTPException

def role_required(allowed_roles: list):
    def checker(current_user):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access Denied"
            )
        return current_user

    return checker
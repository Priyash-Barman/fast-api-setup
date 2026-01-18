from fastapi import HTTPException, status
from fast_app.defaults.common_enums import UserRole
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.user.models.user_model import User
from fast_app.utils.jwt_utils import verify_access_token
from fast_app.utils.logger import logger

async def check_access(token: str, roles: tuple[UserRole, ...], resource: Resource | None = None, action: Action | None = None) -> User:
    try:
        # get payload from token
        payload = verify_access_token(token)
        user_id = payload.get('sub')
        
        # get user details by id
        user = await User.get(user_id)
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token or user")
        
        if not roles or not len(roles):
            return user
        
        if user.role == UserRole.SUPER_ADMIN and UserRole.ADMIN in roles:
            return user
        
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        if user.role==UserRole.ADMIN:
            
            # if resource name not added to the route
            if not resource:
                return user
            
            # if admin has permission to access the resource
            elif resource in user.permissions:

                # check if admin has permission to perform the particular action to the for the resource
                actions=user.permissions.get(resource) or []
                
                # if route action not mentioned, return true
                # if action exist in the the resource permission array return true
                # if admin can perform any("*") action return true
                if not action or action in actions or '*' in actions:
                    return user
                else:
                    raise HTTPException(status.HTTP_403_FORBIDDEN, f"You don't have permission to {action} the resource")
                
            else:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "You don't have permission to access this resource")
        
        return user
    except Exception as e:
        logger.exception(e.with_traceback)
        raise e
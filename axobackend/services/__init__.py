from axobackend.repositories import UsersRepository,CredentialsRepository
import axobackend.models as ModelX
import axobackend.dto as DtoX
from bson import ObjectId
from option import Result,Ok,Err

class UsersService(object):
    def __init__(self, 
        user_repository:UsersRepository,
        credentials_repository: CredentialsRepository
    ):
        self.user_repository        = user_repository
        self.credentials_repository = credentials_repository
    
    # Fatima - Implementar
    async def login():
        pass
    
    async def create(self,create_user_dto:DtoX.CreateUserDTO)->Result[str,Exception]:
        try:
            
            query = {
                "$or":[
                    {"username":create_user_dto.user.username},
                    {"email":create_user_dto.user.email}
                ]
            }

            found_user_result = await self.user_repository.find_one(
                query= query
            )
            if found_user_result.is_err:
                return found_user_result
            
            found_user = found_user_result.unwrap()

            if found_user:
                return Err(Exception("User already exists."))
            
            user = ModelX.UserModel(
                color         = "",
                disabled      = False,
                email         = create_user_dto.user.email,
                first_name    = create_user_dto.user.first_name,
                last_name     = create_user_dto.user.last_name,
                profile_photo = create_user_dto.user.profile_photo,
                username      = create_user_dto.user.username
            )

            create_user_result = await self.user_repository.create(user=user)
            
            if create_user_result.is_err:
                return create_user_result
            
            user_id = create_user_result.unwrap()
            
            credentials = ModelX.CredentialsModel(
                user_id  = user_id,
                password = create_user_dto.credentials.password,
                pin      = create_user_dto.credentials.pin,
                token    = create_user_dto.credentials.token,
            )

            result = await self.credentials_repository.create(
                credentials=credentials,
            )

            if result.is_err:
                return result
            return Ok(user_id)
       
        except Exception as e:
            return Err(e)
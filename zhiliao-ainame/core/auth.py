"""
JWT 身份认证处理模块

本模块提供了 JWT（JSON Web Token）的编码、解码和验证功能。
使用单例模式确保整个应用只有一个认证处理器实例。

依赖包：pyjwt (pip install pyjwt==2.10.1)
"""

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
from enum import Enum
import settings
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from threading import Lock


class SingletonMeta(type):
    """
    线程安全的单例模式元类
    
    确保在整个应用生命周期中，每个类只有一个实例。
    使用线程锁保证多线程环境下的安全性。
    
    Attributes:
        _instances (dict): 存储已创建的实例
        _lock (Lock): 线程锁，用于同步访问
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        创建或返回类的单例实例
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            类的单例实例
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class TokenTypeEnum(Enum):
    """
    JWT 令牌类型枚举
    
    定义两种令牌类型：
    - ACCESS_TOKEN: 访问令牌，用于 API 请求认证
    - REFRESH_TOKEN: 刷新令牌，用于刷新访问令牌
    """
    ACCESS_TOKEN = 1  # 访问令牌
    REFRESH_TOKEN = 2  # 刷新令牌


class AuthHandler(metaclass=SingletonMeta):
    """
    JWT 认证处理器
    
    提供 JWT 令牌的编码、解码和验证功能。
    使用单例模式确保整个应用只有一个实例。
    
    Attributes:
        security (HTTPBearer): FastAPI 的 HTTP Bearer 认证方案
        secret (str): JWT 签名密钥
    """
    
    # HTTP Bearer 认证方案
    # 请求头格式：Authorization: Bearer {token}
    security = HTTPBearer()
    
    # JWT 签名密钥（从配置中读取）
    secret = settings.JWT_SECRET_KEY

    def _encode_token(self, user_id: int, type: TokenTypeEnum) -> str:
        """
        编码 JWT 令牌（私有方法）
        
        根据用户 ID 和令牌类型生成 JWT 令牌。
        
        Args:
            user_id (int): 用户 ID，作为令牌的 iss (issuer) 声明
            type (TokenTypeEnum): 令牌类型，作为令牌的 sub (subject) 声明
            
        Returns:
            str: 编码后的 JWT 令牌字符串
            
        Note:
            - 使用 HS256 算法签名
            - 令牌包含过期时间（exp）
            - ACCESS_TOKEN 有效期为15天
            - REFRESH_TOKEN 有效期为30天
        """
        # 构建 JWT 载荷
        payload = dict(
            iss=user_id,           # issuer: 用户 ID
            sub=str(type.value)    # subject: 令牌类型
        )
        to_encode = payload.copy()
        
        # 根据令牌类型设置过期时间
        if type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES
        else:
            exp = datetime.now() + settings.JWT_REFRESH_TOKEN_EXPIRES
        
        # 添加过期时间到载荷
        to_encode.update({"exp": int(exp.timestamp())})
        
        # 使用密钥编码令牌
        return jwt.encode(to_encode, self.secret, algorithm='HS256')

    def encode_login_token(self, user_id: int) -> dict:
        """
        编码登录令牌对
        
        生成访问令牌和刷新令牌的组合，用于用户登录。
        
        Args:
            user_id (int): 用户 ID
            
        Returns:
            dict: 包含访问令牌和刷新令牌的字典：
                - access_token: 访问令牌（15天有效）
                - refresh_token: 刷新令牌（30天有效）
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        
        login_token = dict(
            access_token=f"{access_token}",
            refresh_token=f"{refresh_token}"
        )
        return login_token

    def encode_update_token(self, user_id: int) -> dict:
        """
        编码更新令牌
        
        生成新的访问令牌，用于刷新令牌时使用。
        
        Args:
            user_id (int): 用户 ID
            
        Returns:
            dict: 包含访问令牌的字典：
                - access_token: 新的访问令牌（15天有效）
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        
        update_token = dict(
            access_token=f"{access_token}"
        )
        return update_token

    def decode_access_token(self, token: str) -> int:
        """
        解码访问令牌
        
        验证并解码访问令牌，返回用户 ID。
        如果令牌无效或过期，抛出 HTTP 403 错误。
        
        Args:
            token (str): JWT 访问令牌字符串
            
        Returns:
            int: 用户 ID
            
        Raises:
            HTTPException:
                - 403: 令牌类型错误、已过期或无效
                
        Note:
            ACCESS TOKEN 不可用时统一返回 403 错误（Forbidden）
        """
        try:
            # 解码并验证令牌
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            
            # 验证令牌类型
            if payload['sub'] != str(TokenTypeEnum.ACCESS_TOKEN.value):
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, 
                    detail='Token类型错误！'
                )
            
            # 返回用户 ID
            return payload['iss']
            
        except jwt.ExpiredSignatureError:
            # 令牌已过期
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail='Access Token已过期！'
            )
        except jwt.InvalidTokenError as e:
            # 令牌无效（签名错误、格式错误等）
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail='Access Token不可用！'
            )

    def decode_refresh_token(self, token: str) -> int:
        """
        解码刷新令牌
        
        验证并解码刷新令牌，返回用户 ID。
        如果令牌无效或过期，抛出 HTTP 401 错误。
        
        Args:
            token (str): JWT 刷新令牌字符串
            
        Returns:
            int: 用户 ID
            
        Raises:
            HTTPException:
                - 401: 令牌类型错误、已过期或无效
                
        Note:
            REFRESH TOKEN 不可用时统一返回 401 错误（Unauthorized）
        """
        try:
            # 解码并验证令牌
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            
            # 验证令牌类型
            if payload['sub'] != str(TokenTypeEnum.REFRESH_TOKEN.value):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, 
                    detail='Token类型错误！'
                )
            
            # 返回用户 ID
            return payload['iss']
            
        except jwt.ExpiredSignatureError:
            # 令牌已过期
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, 
                detail='Refresh Token已过期！'
            )
        except jwt.InvalidTokenError as e:
            # 令牌无效（签名错误、格式错误等）
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, 
                detail='Refresh Token不可用！'
            )

    def auth_access_dependency(
        self, 
        auth: HTTPAuthorizationCredentials = Security(security)
    ) -> int:
        """
        访问令牌依赖注入函数
        
        用于 FastAPI 路由的依赖注入，自动从请求头中提取并验证访问令牌。
        
        Args:
            auth (HTTPAuthorizationCredentials): 从请求头中提取的认证信息
            
        Returns:
            int: 用户 ID
            
        Raises:
            HTTPException: 当令牌无效或过期时抛出异常
            
        Example:
            @router.get("/protected")
            async def protected_route(user_id: int = Depends(auth_handler.auth_access_dependency)):
                # user_id 是已验证的用户 ID
                pass
        """
        return self.decode_access_token(auth.credentials)

    def auth_refresh_dependency(
        self, 
        auth: HTTPAuthorizationCredentials = Security(security)
    ) -> int:
        """
        刷新令牌依赖注入函数
        
        用于 FastAPI 路由的依赖注入，自动从请求头中提取并验证刷新令牌。
        
        Args:
            auth (HTTPAuthorizationCredentials): 从请求头中提取的认证信息
            
        Returns:
            int: 用户 ID
            
        Raises:
            HTTPException: 当令牌无效或过期时抛出异常
        """
        return self.decode_refresh_token(auth.credentials)
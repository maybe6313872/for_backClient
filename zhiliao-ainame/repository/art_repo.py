"""
文章数据仓库模块

本模块提供了文章的数据访问层（Repository Pattern）。
封装了所有与文章相关的数据库操作。

使用异步 SQLAlchemy 进行数据库操作，确保高性能和并发安全。
"""

from models import AsyncSession
from models.art import Art
from sqlalchemy import delete, update, select


class ArtRepository:
    """
    文章数据仓库类
    
    提供文章相关的数据库操作方法。
    所有方法都是异步的，使用 SQLAlchemy 异步会话。
    
    Attributes:
        session (AsyncSession): SQLAlchemy 异步数据库会话
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化文章仓库
        
        Args:
            session (AsyncSession): 数据库会话实例
        """
        self.session = session

    async def create(
        self,
        username: str,
        sex: str,
        artcontent: str,
        thumbnail: bytes
    ) -> Art:
        """
        创建文章记录
        
        在数据库中保存文章信息。
        
        Args:
            username (str): 用户名
            sex (str): 性别
            artcontent (str): 文章内容
            thumbnail (bytes): 文章缩略图二进制数据
                
        Returns:
            Art: 创建的文章对象
            
        Note:
            - 需要在外部调用 commit() 才能持久化到数据库
        """
        # 创建文章对象
        art = Art(
            username=username,
            sex=sex,
            artcontent=artcontent,
            thumbnail=thumbnail
        )
        # 添加到会话中
        self.session.add(art)
        # 注意：不需要 flush()，因为 commit() 会自动执行 flush，所以这句是多余的，已问过cursor了，不过要自增ID的话，还是留着
        await self.session.flush()
        return art
    async def delete_by_ids(self, id_arr: list[int]) -> int:
        """
        批量删除文章记录
        
        根据ID数组批量删除文章。
        
        Args:
            id_arr (list[int]): 要删除的文章ID数组
                
        Returns:
            int: 实际删除的记录数
            
        Note:
            - 需要在外部调用 commit() 才能持久化到数据库
        """
        
        if not id_arr:
            return 0
        
        # ========== 方式1：使用 delete() 语句（当前实现，推荐）==========
        # 优点：
        #   - 一条SQL语句完成批量删除，性能高
        #   - 内存占用低，不需要加载对象到内存
        #   - 适合大批量删除操作
        # 缺点：
        #   - 不会触发ORM的事件钩子（如 before_delete, after_delete）
        #   - 不会触发级联删除（如果有外键关联）
        stmt = delete(Art).where(Art.id.in_(id_arr))
        result = await self.session.execute(stmt)
        # 先查询出所有要删除的对象
        # arts = await self.session.scalars(select(Art).where(Art.id.in_(id_arr)))
        # count = 0
        # for art in arts:
        #     await self.session.delete(art)
        #     count += 1
        # 返回删除的记录数
        return result.rowcount
    
    async def change_by_id(self, id: int, sex: str) -> int:
        """
        修改文章记录
        
        根据ID修改文章记录。
        """
        # stmt = update(Art).where(Art.id == id).values(sex=sex)
        # result = await self.session.execute(stmt)

        # # 使用 session 的 ORM 方式实现修改
        # # 1. 先查询出要修改的对象
        stmt = select(Art).where(Art.id == id)
        art = await self.session.scalar(stmt)
        
        # 2. 如果对象存在，修改其属性
        if art:
            art.sex = sex
        return art.id
    async def query_by_sex(self, page: int, size: int, sex: str) -> list[Art]:
        """
        查询文章记录
        
        根据性别分页查询文章记录。
        
        Args:
            page (int): 页码（从1开始）
            size (int): 每页数量
            sex (str): 性别筛选条件
                
        Returns:
            list[Art]: 文章对象列表
        """
        # 计算偏移量
        offset = (page - 1) * size
        
        # 构建查询语句：根据性别筛选，按创建时间倒序排列，分页查询
        stmt = (
            select(Art)
            .where(Art.sex == sex)
            .order_by(Art.created_time.desc())  # 按创建时间倒序
            .offset(offset)
            .limit(size)
        )
        
        # 执行查询并获取结果
        result = await self.session.scalars(stmt)
        arts = result.all()
        
        return arts
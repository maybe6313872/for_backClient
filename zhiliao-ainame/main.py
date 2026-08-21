"""
FastAPI 应用主入口文件

本模块定义了 FastAPI 应用实例，注册所有路由，并提供一些基础 API 端点。
"""

from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi import Depends
from dependencies import get_mail
from aiosmtplib import SMTPResponseException
from routers.auth_router import router as auth_router
from routers.name_router import router as name_router
from routers.art import router as art_router
from routers.artFile import router as art_file_router
from routers.redisTest import router as region_router
from routers.school import (
    school_router,
    teacher_router,
    student_router,
    course_router,
    student_course_router
)
from routers.order import (company_router, product_router, order_router)

# 创建 FastAPI 应用实例
# 配置应用的基本信息，包括标题、描述、版本和文档路径
app = FastAPI(
    title="知了AI起名 API",
    description="一个基于AI的起名服务API，提供用户注册、登录和智能起名功能",
    version="1.0.0",
    docs_url="/docs",          # Swagger UI 文档路径
    redoc_url="/redoc",        # ReDoc 文档路径
    openapi_url="/openapi.json"  # OpenAPI JSON 规范路径
)

# 注册路由模块
# 将认证相关的路由注册到应用中
app.include_router(auth_router)
# 将起名相关的路由注册到应用中
app.include_router(name_router)
# 将文章相关的路由注册到应用中
app.include_router(art_router)
# 将文章文件相关的路由注册到应用中
app.include_router(art_file_router)
# 将省市区相关的路由注册到应用中
app.include_router(region_router)
# 将学校相关的路由注册到应用中
app.include_router(school_router)
# 将班主任相关的路由注册到应用中
app.include_router(teacher_router)
# 将学生相关的路由注册到应用中
app.include_router(student_router)
# 将课程相关的路由注册到应用中
app.include_router(course_router)
# 将学生课程关联相关的路由注册到应用中
app.include_router(student_course_router)
# 将公司相关的路由注册到应用中
app.include_router(company_router)
# 将产品相关的路由注册到应用中
app.include_router(product_router)
# 将订单相关的路由注册到应用中
app.include_router(order_router)


@app.get("/")
async def root():
    """
    根路径端点
    
    用于测试 API 服务是否正常运行。
    
    Returns:
        dict: 包含欢迎消息的字典
    """
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    """
    问候接口
    
    根据传入的名字参数返回个性化的问候消息。
    
    Args:
        name (str): 要问候的名字
        
    Returns:
        dict: 包含问候消息的字典
    """
    return {"message": f"Hello {name}"}


@app.get("/mail/test")
async def mail_test(
    email: str,
    mail: FastMail = Depends(get_mail),
):
    """
    邮件测试接口
    
    用于测试邮件发送功能是否正常工作。
    注意：此接口仅用于开发测试，生产环境应移除或限制访问。
    
    Args:
        email (str): 接收测试邮件的邮箱地址
        mail (FastMail): 通过依赖注入获取的邮件服务实例
        
    Returns:
        dict: 包含邮件发送结果的字典
        
    Raises:
        SMTPResponseException: 当邮件发送失败时（QQ邮箱的特殊情况除外）
    """
    # 创建邮件消息对象
    message = MessageSchema(
        subject="hello",
        recipients=[email],
        body=f"hello {email}",
        subtype=MessageType.plain,  # 纯文本格式
    )
    try:
        # 发送邮件
        await mail.send_message(message)
    except SMTPResponseException as e:
        # QQ 邮箱在 SMTP 关闭阶段会返回非标准响应，但邮件已成功发送
        # 这里特殊处理，避免误报错误
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
    return {"message": "邮件发送成功！"}
"""
文章文件相关路由模块

本模块提供了文章相关的文件操作 API 端点。
"""

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from models import AsyncSession
from dependencies import get_session
from repository.art_repo import ArtRepository
from schemas.art import ArtQueryIn, ArtOut, ArtQueryOut
from schemas import ResponseOut
from core.excel import create_excel_file, encode_filename_for_download, parse_excel, find_column_indices
import base64
from datetime import datetime
from typing import Optional


# 创建文章文件相关的路由组
router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/queryArtExcel", summary="导出文章Excel", description="查询文章并导出为Excel文件")
async def query_art_excel(
    data: ArtQueryIn,
    session: AsyncSession = Depends(get_session),
):
    """
    查询文章并导出为Excel文件接口

    查询文章记录，将结果导出为Excel文件（blob格式）。
    
    Args:
        data (ArtQueryIn): 查询参数，包含：
            - page: 页码
            - size: 每页数量
            - sex: 性别筛选条件
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        StreamingResponse: Excel文件的二进制流响应
    """
    art_repo = ArtRepository(session=session)
    artList = await art_repo.query_by_sex(data.page, data.size, data.sex)

    # 将 ORM 对象转换为 ArtOut
    result = []
    for item in artList:
        result.append(ArtOut.model_validate(item, from_attributes=True))
    
    # 准备表头和数据
    headers = ["ID", "用户名", "性别", "文章内容"]
    data_rows = []
    for art in result:
        data_rows.append([
            art.id,
            art.username,
            art.sex,
            art.artcontent,
        ])
    
    # 生成 Excel 文件
    excel_buffer = create_excel_file(
        headers=headers,
        data_rows=data_rows,
        sheet_title="文章列表",
        column_widths={
            'A': 10,  # ID
            'B': 20,  # 用户名
            'C': 10,  # 性别
            'D': 50,  # 文章内容
        },
        header_style={
            'font_color': 'FFFFFF',
            'fill_color': '366092',
            'bold': True,
            'alignment': 'center'
        }
    )
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"文章列表_{timestamp}.xlsx"
    ascii_filename = f"article_list_{timestamp}.xlsx"
    
    # 对文件名进行 URL 编码
    encoded_filename = encode_filename_for_download(filename)
    
    # 返回Excel文件的二进制流
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            # 使用 RFC 5987 格式支持中文文件名
            # filename: ASCII 兼容的后备文件名（旧版浏览器）
            # filename*: UTF-8 编码的文件名（现代浏览器优先使用）
            "Content-Disposition": f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"
        }
    )

@router.post("/insertArtByExcel", response_model=ResponseOut, summary="批量导入文章", description="从Excel文件批量导入文章数据")
async def insert_artbyexcel(
    username: Optional[str] = Form(None, description="用户名（当前用户，可选）"),
    file: UploadFile = File(..., description="Excel文件，包含：用户名、性别、文章内容、缩略图(base64，可选)"),
    session: AsyncSession = Depends(get_session),
):
    """
    从Excel文件批量导入文章数据接口
    
    从上传的Excel文件中读取文章数据并批量插入到数据库。
    Excel文件格式要求：
    - 第一行为表头：用户名、性别、文章内容、缩略图（可选）
    - 从第二行开始为数据行
    - 缩略图列如果存在，应为base64编码的字符串；如果为空，则使用空字节
    
    Args:
        username (str): 用户名（当前用户，可用于后续业务逻辑）
        file (UploadFile): Excel文件（.xlsx格式）
        session (AsyncSession): 数据库会话（通过依赖注入获取）
        
    Returns:
        ResponseOut: 操作结果
            - result: "success" 表示成功，"failure" 表示失败
            
    Raises:
        HTTPException: 当文件格式错误或数据验证失败时
    """
    try:
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="文件格式错误，仅支持 .xlsx 或 .xls 格式")
        
        # 读取上传的文件内容
        file_content = await file.read()
        
        # 解析 Excel 文件（只解析，不验证）
        try:
            headers, data_rows = parse_excel(file_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # 检查是否有数据行
        if not data_rows:
            raise HTTPException(status_code=400, detail="Excel文件为空或没有数据行")
        
        # 查找列索引
        column_names = {
            'username': ['用户名', 'username', '用户'],
            'sex': ['性别', 'sex'],
            'artcontent': ['文章内容', 'artcontent', '内容', 'content'],
            'thumbnail': ['缩略图', 'thumbnail', '图片', 'image']
        }
        column_indices = find_column_indices(headers, column_names)
        
        # 验证必需的列是否存在
        if column_indices.get('username') is None:
            raise HTTPException(status_code=400, detail="Excel文件中缺少'用户名'列")
        if column_indices.get('sex') is None:
            raise HTTPException(status_code=400, detail="Excel文件中缺少'性别'列")
        if column_indices.get('artcontent') is None:
            raise HTTPException(status_code=400, detail="Excel文件中缺少'文章内容'列")
        
        # 创建仓库实例
        art_repo = ArtRepository(session=session)
        
        # 统计信息
        success_count = 0
        error_count = 0
        errors = []
        
        # 处理每一行数据
        for row_data in data_rows:
            row_num = row_data['row_num']
            cells = row_data['cells']
            
            try:
                # 提取各列的值
                username_val = cells.get(column_indices['username'])
                sex_val = cells.get(column_indices['sex'])
                artcontent_val = cells.get(column_indices['artcontent'])
                thumbnail_str = cells.get(column_indices.get('thumbnail')) if column_indices.get('thumbnail') else None
                
                # 验证必需字段
                if not username_val or not sex_val or not artcontent_val:
                    error_count += 1
                    errors.append(f"第{row_num}行：缺少必需字段（用户名、性别、文章内容）")
                    continue
                
                # 转换为字符串（处理数字类型）
                username = str(username_val).strip()
                sex = str(sex_val).strip()
                artcontent = str(artcontent_val).strip()
                
                # 验证字段长度
                if len(username) > 100:
                    error_count += 1
                    errors.append(f"第{row_num}行：用户名长度超过100字符")
                    continue
                if len(sex) > 10:
                    error_count += 1
                    errors.append(f"第{row_num}行：性别长度超过10字符")
                    continue
                if len(artcontent) > 5000:
                    error_count += 1
                    errors.append(f"第{row_num}行：文章内容长度超过5000字符")
                    continue
                
                # 处理缩略图 base64 解码
                thumbnail_bytes = b''
                if thumbnail_str:
                    try:
                        thumbnail_str = str(thumbnail_str).strip()
                        if thumbnail_str:
                            thumbnail_bytes = base64.b64decode(thumbnail_str)
                    except Exception:
                        errors.append(f"第{row_num}行：缩略图base64解码失败，将使用空缩略图")
                        thumbnail_bytes = b''
                
                # 创建文章记录
                await art_repo.create(
                    username=username,
                    sex=sex,
                    artcontent=artcontent,
                    thumbnail=thumbnail_bytes
                )
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"第{row_num}行处理失败: {str(e)}")
                continue
        
        # 提交事务（只要有成功的记录就提交）
        if success_count > 0:
            await session.commit()
        else:
            # 如果没有成功记录，回滚事务
            await session.rollback()
        
        # 返回结果
        if success_count == 0:
            # 全部失败
            error_message = f"批量导入失败，共{error_count}条错误。"
            if errors:
                error_message += f" 前5条错误：{'; '.join(errors[:5])}"
            raise HTTPException(status_code=400, detail=error_message)
        elif error_count > 0:
            # 部分成功（有成功也有失败）
            # 注意：这里返回 success，因为至少有一部分数据导入成功
            # 如果需要更详细的反馈，可以考虑修改 ResponseOut 模型添加更多字段
            return ResponseOut(result="success")
        else:
            # 全部成功
            return ResponseOut(result="success")
            
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 回滚事务
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"批量导入文章时发生错误: {str(e)}")

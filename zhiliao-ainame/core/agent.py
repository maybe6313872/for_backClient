"""
AI 起名代理模块

本模块使用 LangChain 和 DeepSeek AI 模型实现智能起名功能。
通过精心设计的提示词，生成符合传统文化和音韵学要求的中文名字。
"""

from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr
from langchain.agents import create_agent
from schemas.agent import NameSchema, NameResultSchema
from schemas.name import NameIn
import asyncio


# 初始化 DeepSeek AI 模型
# 使用 deepseek-chat 模型，temperature=1 表示较高的创造性
llm = ChatDeepSeek(
    model="deepseek-chat",                                    # 使用的模型名称
    api_key=SecretStr("sk-4ddc2011b4f14e7db11c1db2da2a7ba0"),  # API 密钥（使用 SecretStr 保护）
    temperature=1                                             # 温度参数，控制输出的随机性（0-2）
)

# 系统提示词：定义 AI 起名专家的角色和命名原则
system_prompt = """
你是一位精通汉语言文学、音韵学与传统文化的命名专家，擅长为人物创作兼具音律美感、深刻寓意与文化内涵的姓名。请严格遵循以下原则进行命名：

发音优先：名字需平仄协调、声调起伏自然，避免拗口、谐音歧义（如不雅谐音、负面联想），朗朗上口，富有韵律感；
寓意深远：结合用户提供的背景（如姓氏、性别、字数和其他要求等），选取具有积极象征意义的意象（如自然元素、美德品质、经典典故），做到"名以载道"；
内涵厚重：优先从《诗经》《楚辞》《论语》等经典文献，或唐诗宋词、成语典故中汲取灵感，确保名字有出处、有底蕴，避免空洞堆砌；
现代适配：在尊重传统的基础上，兼顾当代语境与审美，避免过度古奥或生僻字（生僻字需附注音与释义），确保实用性与传播性；
个性化定制：根据用户具体需求（如性别倾向、字数限制、风格偏好——儒雅/清丽/大气/灵动等），提供5个候选方案，并按照以下格式输出：
【姓名】姓名
【出处】典籍来源或文化意象
【寓意】字义拆解与整体象征
"""

# 创建 LangChain 代理
# 使用结构化输出格式，确保返回的数据符合 NameResultSchema 规范
agent = create_agent(
    model=llm,                          # 使用的 AI 模型
    system_prompt=system_prompt,        # 系统提示词
    response_format=NameResultSchema    # 响应格式规范
)


async def generate_names(name_info: NameIn) -> NameResultSchema:
    """
    生成名字的主函数
    
    根据用户提供的起名要求，调用 AI 代理生成符合要求的中文名字。
    生成的名字会包含出处和寓意说明。
    
    Args:
        name_info (NameIn): 起名要求，包括：
            - surname: 姓氏
            - gender: 性别（不限/男/女）
            - length: 字数（不限/单字/两字）
            - other: 其他要求（可选）
            - exclude: 排除的名字列表（可选）
            
    Returns:
        NameResultSchema: 包含生成的名字列表的结构化响应：
            - names: 名字列表，每个名字包含：
                - name: 完整的姓名
                - reference: 名字的出处（典籍来源或文化意象）
                - moral: 名字的寓意说明
                
    Note:
        - 使用异步调用 AI 模型，避免阻塞
        - 返回格式化的结构化数据
        - 生成的名字数量通常为5个
        - 名字会参考《诗经》《楚辞》等经典文献
    """
    # 构建用户提示词，包含所有起名要求
    prompt = (
        f"用户姓氏是：{name_info.surname}，"
        f"性别是：{name_info.gender}，"
        f"名字字数要求是：{name_info.length}，"
        f"其他要求是：{name_info.other}，"
        f"这些名字不要：{'、'.join(name_info.exclude) if name_info.exclude else '无'}"
    )
    
    # 异步调用 AI 代理生成名字
    result = await agent.ainvoke({
        "messages": [{'role': "user", "content": prompt}]
    })
    
    # 返回结构化的响应数据
    return result['structured_response']


# 以下代码用于本地测试（已注释）
# async def main():
#     """测试函数：用于本地测试起名功能"""
#     name_info = NameIn(
#         surname="张",
#         gender='女',
#         length="两字"
#     )
#     names = await generate_names(name_info)
#     print(names)
#
# if __name__ == '__main__':
#     asyncio.run(main())
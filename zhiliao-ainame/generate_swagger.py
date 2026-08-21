"""
生成 Swagger/OpenAPI 文档文件
运行此脚本将生成 openapi.json 和 openapi.yaml 文件
"""
import json
import yaml
from main import app


def generate_swagger():
    """生成 Swagger/OpenAPI 文档"""
    # 获取 OpenAPI schema
    openapi_schema = app.openapi()
    
    # 生成 JSON 格式
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
    print("[OK] 已生成 openapi.json")
    
    # 生成 YAML 格式
    with open("openapi.yaml", "w", encoding="utf-8") as f:
        yaml.dump(openapi_schema, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print("[OK] 已生成 openapi.yaml")
    
    print(f"\nAPI 文档信息:")
    print(f"   - 标题: {openapi_schema.get('info', {}).get('title', 'API')}")
    print(f"   - 版本: {openapi_schema.get('info', {}).get('version', '1.0.0')}")
    print(f"   - 路径数量: {len(openapi_schema.get('paths', {}))}")
    print(f"\n提示: 你也可以通过访问 http://localhost:8000/docs 查看 Swagger UI")
    print(f"     或访问 http://localhost:8000/redoc 查看 ReDoc")


if __name__ == "__main__":
    generate_swagger()

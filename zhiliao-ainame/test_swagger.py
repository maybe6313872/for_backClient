"""
测试 Swagger 文档是否正常生成
"""
import sys
from main import app

def test_swagger():
    """测试 Swagger 文档"""
    try:
        # 获取 OpenAPI schema
        schema = app.openapi()
        
        # 检查基本信息
        info = schema.get('info', {})
        print(f"Title: {info.get('title')}")
        print(f"Version: {info.get('version')}")
        print(f"Description: {info.get('description', 'N/A')[:50]}...")
        
        # 检查路径
        paths = schema.get('paths', {})
        print(f"\nTotal paths: {len(paths)}")
        print("\nAvailable API endpoints:")
        for path in sorted(paths.keys()):
            methods = list(paths[path].keys())
            print(f"  {path} - {', '.join(methods).upper()}")
        
        # 检查组件
        components = schema.get('components', {})
        schemas = components.get('schemas', {})
        print(f"\nTotal schemas: {len(schemas)}")
        print("\nAvailable schemas:")
        for schema_name in sorted(schemas.keys())[:10]:  # 只显示前10个
            print(f"  - {schema_name}")
        if len(schemas) > 10:
            print(f"  ... and {len(schemas) - 10} more")
        
        print("\n[OK] Swagger documentation is ready!")
        print("\nTo view Swagger UI:")
        print("  1. Start the server: uvicorn main:app --reload")
        print("  2. Open browser: http://localhost:8000/docs")
        print("  3. Or view ReDoc: http://localhost:8000/redoc")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to generate Swagger: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_swagger()
    sys.exit(0 if success else 1)

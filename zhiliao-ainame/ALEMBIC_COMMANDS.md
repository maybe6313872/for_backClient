# Alembic 数据库迁移命令指南

## 将模型同步到数据库的完整步骤

### 步骤1：检查当前迁移状态
查看当前数据库的迁移版本和待应用的迁移

```bash
alembic current
```

**说明**：显示当前数据库的迁移版本号

---

### 步骤2：查看迁移历史
查看所有迁移文件的列表和版本链

```bash
alembic history
```

**说明**：显示所有迁移文件的版本号、描述和依赖关系

---

### 步骤3：检查模型变更（可选）
如果修改了模型，需要生成新的迁移文件

```bash
alembic revision --autogenerate -m "描述信息"
```

**示例**：
```bash
alembic revision --autogenerate -m "add_user_table"
alembic revision --autogenerate -m "add_email_code_table"
```

**说明**：
- `--autogenerate`：自动检测模型变更并生成迁移脚本
- `-m`：添加迁移描述信息
- 会在 `alembic/versions/` 目录下生成新的迁移文件

---

### 步骤4：应用所有待执行的迁移
将模型同步到数据库（应用所有未应用的迁移）

```bash
alembic upgrade head
```

**说明**：
- `head`：表示最新版本
- 会按顺序执行所有未应用的迁移
- **这是最常用的命令，用于同步模型到数据库**

---

### 步骤5：验证迁移结果（可选）
检查迁移是否成功应用

```bash
alembic current
```

**说明**：确认当前数据库版本已更新到最新

---

## 其他常用命令

### 回滚到上一个版本
```bash
alembic downgrade -1
```

**说明**：回滚一个版本

---

### 回滚到指定版本
```bash
alembic downgrade <版本号>
```

**示例**：
```bash
alembic downgrade 08369504438d
```

**说明**：回滚到指定的迁移版本

---

### 回滚到初始状态（清空所有表）
```bash
alembic downgrade base
```

**说明**：回滚所有迁移，清空数据库表结构

---

### 升级到指定版本
```bash
alembic upgrade <版本号>
```

**示例**：
```bash
alembic upgrade 08369504438d
```

**说明**：升级到指定的迁移版本

---

### 查看迁移 SQL（不执行）
```bash
alembic upgrade head --sql
```

**说明**：查看将要执行的 SQL 语句，但不实际执行

---

### 手动创建空迁移文件
```bash
alembic revision -m "描述信息"
```

**说明**：创建空的迁移文件，需要手动编写升级和降级逻辑

---

## 完整工作流程示例

### 场景1：首次同步模型到数据库

```bash
# 1. 检查当前状态
alembic current

# 2. 生成迁移文件（如果模型有变更）
alembic revision --autogenerate -m "initial_migration"

# 3. 应用迁移到数据库
alembic upgrade head

# 4. 验证结果
alembic current
```

### 场景2：修改模型后同步

```bash
# 1. 修改模型文件（models/user.py 等）

# 2. 生成新的迁移文件
alembic revision --autogenerate -m "add_new_field"

# 3. 检查生成的迁移文件（可选）
# 打开 alembic/versions/xxx_add_new_field.py 检查

# 4. 应用迁移
alembic upgrade head
```

### 场景3：回滚迁移

```bash
# 1. 查看历史
alembic history

# 2. 回滚一个版本
alembic downgrade -1

# 3. 或回滚到指定版本
alembic downgrade <版本号>
```

---

## 注意事项

1. **确保数据库连接正确**
   - 检查 `settings/__init__.py` 中的 `DB_URI` 配置
   - 确保数据库服务正在运行

2. **迁移前备份数据**
   - 生产环境迁移前务必备份数据库
   - 使用 `alembic upgrade head --sql` 预览 SQL

3. **检查生成的迁移文件**
   - 自动生成的迁移可能不完美
   - 需要手动检查 `alembic/versions/` 下的迁移文件

4. **版本控制**
   - 迁移文件应该提交到 Git
   - 不要删除已应用的迁移文件

5. **异步数据库**
   - 本项目使用异步数据库，Alembic 会自动处理异步连接

---

## 快速参考

| 命令 | 用途 |
|------|------|
| `alembic current` | 查看当前数据库版本 |
| `alembic history` | 查看迁移历史 |
| `alembic revision --autogenerate -m "描述"` | 生成迁移文件 |
| `alembic upgrade head` | **应用所有迁移（最常用）** |
| `alembic downgrade -1` | 回滚一个版本 |
| `alembic upgrade head --sql` | 预览 SQL 语句 |

---

## 常见问题

### Q: 提示 "Target database is not up to date"
**A**: 需要先应用迁移：`alembic upgrade head`

### Q: 提示 "Can't locate revision identified by 'xxx'"
**A**: 检查迁移文件是否存在，或使用 `alembic history` 查看可用版本

### Q: 迁移失败怎么办？
**A**: 使用 `alembic downgrade -1` 回滚，修复问题后重新生成迁移

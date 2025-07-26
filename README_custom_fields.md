# 考勤自定义字段扩展使用说明

## 🚀 快速开始

### 方法一：使用快速设置脚本（推荐）

1. **下载脚本**
   ```bash
   # 将 quick_custom_fields_setup.py 文件放在bench目录下
   ```

2. **运行脚本**
   ```bash
   bench --site your-site.com execute quick_custom_fields_setup.py
   ```

3. **完成设置**
   - 脚本会自动创建所有自定义字段
   - 清除缓存并更新导入模板
   - 按照提示完成后续操作

### 方法二：手动创建

1. **进入bench控制台**
   ```bash
   bench --site your-site.com console
   ```

2. **执行创建命令**
   ```python
   from frappe.custom.doctype.custom_field.custom_field import create_custom_field
   
   # 创建工作地点字段
   create_custom_field(
       doctype="Attendance",
       fieldname="work_location",
       fieldtype="Select",
       label="工作地点",
       options="\n办公室\n远程办公\n出差\n客户现场\n其他",
       insert_after="details_section",
       reqd=0
   )
   
   # 创建其他字段...
   ```

3. **清除缓存**
   ```python
   frappe.clear_cache(doctype="Attendance")
   frappe.clear_cache()
   ```

## 📋 添加的自定义字段

| 字段名 | 类型 | 标签 | 说明 |
|--------|------|------|------|
| `work_location` | Select | 工作地点 | 办公室、远程办公、出差等 |
| `overtime_hours` | Float | 加班时长(小时) | 记录当日加班时长 |
| `attendance_note` | Small Text | 考勤备注 | 考勤相关说明 |
| `project` | Link | 项目 | 关联的工作项目 |
| `task` | Link | 任务 | 关联的具体任务 |
| `attendance_verified_by` | Link | 考勤确认人 | 确认考勤记录的人员 |
| `verification_date` | Datetime | 确认时间 | 考勤确认的时间 |
| `attendance_category` | Select | 考勤类别 | 正常出勤、加班、出差等 |
| `attendance_reason` | Select | 考勤原因 | 具体的工作原因 |

## 🔧 字段功能特点

### 1. 智能依赖关系
- 选择"出差"时，考勤原因和考勤类别变为必填
- 选择"加班"时，加班时长变为必填
- 项目变化时，任务字段自动清空

### 2. 数据验证
- 加班时长不能为负数
- 加班时长不能超过24小时
- 任务必须属于选择的项目

### 3. 自动计算
- 根据签到和签退时间自动计算工作时长
- 加班时自动设置考勤类别

## 📊 导入导出功能

### 更新后的导入模板包含：
- 原有字段：ID、Employee、Employee Name、Date、Status等
- 新增字段：Work Location、Overtime Hours、Attendance Note等

### 导出格式：
```csv
ID,Employee,Employee Name,Date,Status,Leave Type,Company,Naming Series,Work Location,Overtime Hours,Attendance Note,Project,Task,Attendance Category,Attendance Reason
```

## 🎯 使用场景

### 1. 远程办公管理
- 使用"工作地点"字段标记远程办公
- 通过"考勤备注"记录工作内容

### 2. 项目考勤跟踪
- 关联项目和任务
- 跟踪员工在不同项目上的工作时间

### 3. 加班管理
- 记录加班时长和原因
- 自动计算加班费用

### 4. 出差考勤
- 标记出差状态
- 记录出差原因和地点

## 🔍 验证和测试

### 1. 检查字段是否创建成功
```python
import frappe
meta = frappe.get_meta("Attendance")
custom_fields = [f for f in meta.fields if f.custom]
print("自定义字段:", [f.fieldname for f in custom_fields])
```

### 2. 测试字段功能
1. 创建新的考勤记录
2. 检查自定义字段是否显示
3. 测试字段的验证逻辑
4. 测试字段的依赖关系

### 3. 测试导入功能
1. 下载导入模板
2. 填写包含自定义字段的数据
3. 上传并验证导入结果

## 🛠️ 常见问题

### Q1: 字段不显示怎么办？
```python
# 清除缓存
frappe.clear_cache(doctype="Attendance")
frappe.clear_cache()

# 刷新浏览器页面
```

### Q2: 如何移除自定义字段？
```python
from frappe.custom.doctype.custom_field.custom_field import delete_custom_field

# 移除单个字段
delete_custom_field("Attendance-work_location")

# 或者使用脚本中的移除函数
remove_custom_attendance_fields()
```

### Q3: 导入功能不工作怎么办？
- 检查模板格式是否正确
- 验证字段映射是否匹配
- 查看错误日志

### Q4: 如何修改字段选项？
```python
# 修改Select字段的选项
field = frappe.get_doc("Custom Field", "Attendance-work_location")
field.options = "\n办公室\n远程办公\n出差\n客户现场\n其他\n新选项"
field.save()
```

## 📈 扩展建议

### 1. 添加更多字段类型
- 地理位置坐标（GPS）
- 设备信息（签到设备）
- 天气信息（外部API）

### 2. 增强验证逻辑
- 工作时间范围验证
- 节假日自动识别
- 重复考勤检查

### 3. 集成其他模块
- 与薪资模块集成
- 与项目管理集成
- 与审批流程集成

## 📞 技术支持

如果在使用过程中遇到问题，可以：

1. 检查Frappe日志文件
2. 查看控制台错误信息
3. 参考Frappe官方文档
4. 在社区论坛寻求帮助

## 📝 更新日志

- **v1.0** - 初始版本，包含基础自定义字段
- **v1.1** - 添加字段依赖关系和验证逻辑
- **v1.2** - 更新导入模板支持自定义字段

---

**注意**：在实施前请务必备份数据，并在测试环境中验证功能。
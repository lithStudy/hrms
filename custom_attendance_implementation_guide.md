# 自定义个性化考勤字段和状态类型实施指南

## 概述

本指南将帮助您在Frappe HRMS系统中自定义个性化的考勤字段和状态类型。系统提供了多种方法来实现这一目标，您可以根据具体需求选择最适合的方案。

## 方案选择

### 方案一：自定义字段扩展（推荐）
**适用场景**：在现有考勤功能基础上添加额外字段
**优点**：简单易行，不影响现有功能
**缺点**：无法修改核心状态选项

### 方案二：修改状态选项
**适用场景**：需要修改考勤状态类型
**优点**：可以完全自定义状态选项
**缺点**：可能影响现有数据

### 方案三：创建自定义文档类型
**适用场景**：需要全新的考勤管理方式
**优点**：完全自定义，功能强大
**缺点**：需要重新开发相关功能

## 详细实施步骤

### 方案一：自定义字段扩展

#### 1. 创建自定义应用（如果还没有）

```bash
bench new-app custom_attendance
bench --site your-site.com install-app custom_attendance
```

#### 2. 在自定义应用中创建字段配置

创建文件：`custom_attendance/custom_attendance_fields.py`

```python
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_attendance_custom_fields():
    """创建考勤自定义字段"""
    
    custom_fields = {
        "Attendance": [
            {
                "fieldname": "custom_attendance_section",
                "fieldtype": "Section Break",
                "label": "自定义考勤信息",
                "insert_after": "details_section",
            },
            {
                "fieldname": "work_location",
                "fieldtype": "Select",
                "label": "工作地点",
                "options": "\n办公室\n远程办公\n出差\n客户现场\n其他",
                "insert_after": "custom_attendance_section",
            },
            {
                "fieldname": "overtime_hours",
                "fieldtype": "Float",
                "label": "加班时长(小时)",
                "precision": "2",
                "insert_after": "work_location",
            },
            {
                "fieldname": "attendance_note",
                "fieldtype": "Small Text",
                "label": "考勤备注",
                "insert_after": "overtime_hours",
            },
            {
                "fieldname": "project",
                "fieldtype": "Link",
                "label": "项目",
                "options": "Project",
                "insert_after": "attendance_note",
            },
            {
                "fieldname": "task",
                "fieldtype": "Link",
                "label": "任务",
                "options": "Task",
                "depends_on": "project",
                "insert_after": "project",
            },
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)
```

#### 3. 在hooks.py中注册

```python
# custom_attendance/hooks.py
app_include_js = [
    "assets/custom_attendance/js/custom_attendance.js"
]

app_include_css = [
    "assets/custom_attendance/css/custom_attendance.css"
]

# 在安装时执行
on_setup = "custom_attendance.setup.create_custom_fields"
```

#### 4. 创建setup.py

```python
# custom_attendance/setup.py
from .custom_attendance_fields import create_attendance_custom_fields

def create_custom_fields():
    create_attendance_custom_fields()
```

### 方案二：修改状态选项

#### 1. 创建状态修改脚本

```python
# custom_attendance/custom_status.py
import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def customize_attendance_status():
    """自定义考勤状态选项"""
    
    # 修改状态选项
    make_property_setter(
        doctype="Attendance",
        fieldname="status", 
        property="options",
        value="\nPresent\nAbsent\nOn Leave\nHalf Day\nWork From Home\n出差\n培训\n会议\n其他",
        property_type="Text"
    )
    
    # 添加自定义状态字段
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    
    custom_fields = {
        "Attendance": [
            {
                "fieldname": "attendance_category",
                "fieldtype": "Select",
                "label": "考勤类别",
                "options": "\n正常出勤\n加班\n出差\n培训\n会议\n病假\n事假\n年假\n其他",
                "insert_after": "status",
            },
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)
```

### 方案三：创建自定义文档类型

#### 1. 创建文档类型定义

创建目录结构：
```
custom_attendance/
├── custom_attendance/
│   ├── doctype/
│   │   └── custom_attendance/
│   │       ├── __init__.py
│   │       ├── custom_attendance.json
│   │       ├── custom_attendance.py
│   │       └── custom_attendance.js
```

#### 2. 创建Python控制器

```python
# custom_attendance/doctype/custom_attendance/custom_attendance.py
import frappe
from frappe.model.document import Document

class CustomAttendance(Document):
    def validate(self):
        # 自定义验证逻辑
        if self.overtime_hours and self.overtime_hours < 0:
            frappe.throw("加班时长不能为负数")
    
    def before_save(self):
        # 保存前的处理逻辑
        if self.in_time and self.out_time:
            # 计算工作时长
            from frappe.utils import time_diff_in_hours
            self.working_hours = time_diff_in_hours(self.out_time, self.in_time)
```

#### 3. 创建JavaScript控制器

```javascript
// custom_attendance/doctype/custom_attendance/custom_attendance.js
frappe.ui.form.on('Custom Attendance', {
    refresh: function(frm) {
        // 页面刷新时的处理
    },
    
    custom_status: function(frm) {
        // 状态变化时的处理
        if (frm.doc.custom_status === '加班') {
            frm.set_df_property('overtime_hours', 'reqd', 1);
        } else {
            frm.set_df_property('overtime_hours', 'reqd', 0);
        }
    },
    
    project: function(frm) {
        // 项目变化时清空任务
        frm.set_value('task', '');
    }
});
```

## 更新导入功能

### 修改上传模板

如果您使用了自定义字段，需要更新上传模板功能：

```python
# 在upload_attendance.py中添加自定义字段支持
def add_header(w):
    status = ", ".join((frappe.get_meta("Attendance").get_field("status").options or "").strip().split("\n"))
    w.writerow(["Notes:"])
    w.writerow(["Please do not change the template headings"])
    w.writerow(["Status should be one of these values: " + status])
    w.writerow(["If you are overwriting existing attendance records, 'ID' column mandatory"])
    w.writerow([
        "ID", "Employee", "Employee Name", "Date", "Status", 
        "Leave Type", "Company", "Naming Series",
        "Work Location", "Overtime Hours", "Attendance Note",  # 自定义字段
        "Project", "Task"  # 自定义字段
    ])
    return w
```

## 权限配置

### 1. 角色权限

确保相关角色有适当的权限：

```python
# 在setup.py中添加权限
def setup_permissions():
    # 为HR角色添加自定义考勤权限
    roles = ["HR User", "HR Manager"]
    for role in roles:
        if not frappe.db.exists("Custom DocPerm", {"parent": "Custom Attendance", "role": role}):
            frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": "Custom Attendance",
                "role": role,
                "create": 1,
                "read": 1,
                "write": 1,
                "delete": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1
            }).insert()
```

### 2. 工作流配置

如果需要审批流程，可以创建工作流：

```python
def create_attendance_workflow():
    """创建考勤审批工作流"""
    if not frappe.db.exists("Workflow", "Custom Attendance Approval"):
        workflow = frappe.get_doc({
            "doctype": "Workflow",
            "workflow_name": "Custom Attendance Approval",
            "document_type": "Custom Attendance",
            "is_active": 1,
            "send_email_alert": 1,
            "workflow_state_field": "workflow_state"
        })
        
        # 添加工作流状态
        states = [
            {"state": "Draft", "style": "Draft"},
            {"state": "Pending Approval", "style": "Warning"},
            {"state": "Approved", "style": "Success"},
            {"state": "Rejected", "style": "Danger"}
        ]
        
        for state in states:
            workflow.append("states", state)
        
        # 添加工作流转换
        transitions = [
            {"state": "Draft", "action": "Submit", "next_state": "Pending Approval", "allowed": "HR User"},
            {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "HR Manager"},
            {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "HR Manager"}
        ]
        
        for transition in transitions:
            workflow.append("transitions", transition)
        
        workflow.insert()
```

## 测试和验证

### 1. 功能测试

```python
# tests/test_custom_attendance.py
import frappe
import unittest

class TestCustomAttendance(unittest.TestCase):
    def setUp(self):
        # 创建测试数据
        pass
    
    def test_custom_attendance_creation(self):
        # 测试自定义考勤创建
        attendance = frappe.get_doc({
            "doctype": "Custom Attendance",
            "employee": "TEST001",
            "attendance_date": "2024-01-01",
            "custom_status": "正常出勤",
            "work_location": "办公室"
        })
        attendance.insert()
        self.assertTrue(attendance.name)
    
    def test_custom_fields(self):
        # 测试自定义字段
        pass
```

### 2. 导入功能测试

```python
def test_custom_import():
    # 测试自定义字段导入
    pass
```

## 部署和维护

### 1. 部署步骤

```bash
# 1. 安装自定义应用
bench --site your-site.com install-app custom_attendance

# 2. 运行迁移
bench --site your-site.com migrate

# 3. 清除缓存
bench --site your-site.com clear-cache

# 4. 重启服务
bench restart
```

### 2. 数据迁移

如果需要迁移现有数据：

```python
def migrate_existing_attendance():
    """迁移现有考勤数据到自定义格式"""
    existing_attendance = frappe.get_all("Attendance", fields=["*"])
    
    for att in existing_attendance:
        # 创建自定义考勤记录
        custom_att = frappe.get_doc({
            "doctype": "Custom Attendance",
            "employee": att.employee,
            "attendance_date": att.attendance_date,
            "custom_status": att.status,
            # 映射其他字段
        })
        custom_att.insert()
```

## 注意事项

1. **备份数据**：在进行任何修改前，请备份现有数据
2. **测试环境**：先在测试环境中验证功能
3. **权限控制**：确保只有授权用户可以修改考勤数据
4. **数据一致性**：确保自定义字段与现有数据的兼容性
5. **性能考虑**：大量数据时考虑异步处理

## 常见问题

### Q1: 如何恢复默认状态选项？
```python
def reset_to_default():
    make_property_setter(
        doctype="Attendance",
        fieldname="status",
        property="options", 
        value="\nPresent\nAbsent\nOn Leave\nHalf Day\nWork From Home",
        property_type="Text"
    )
```

### Q2: 自定义字段不显示怎么办？
- 检查字段配置是否正确
- 清除浏览器缓存
- 检查权限设置

### Q3: 导入功能不工作怎么办？
- 检查模板格式
- 验证字段映射
- 查看错误日志

通过以上步骤，您可以成功地在Frappe HRMS系统中实现个性化的考勤字段和状态类型自定义。
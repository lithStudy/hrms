# Frappe HRMS 自定义字段扩展完整指南

## 概述

自定义字段扩展是Frappe框架中最常用的自定义方式，它允许您在现有文档类型基础上添加新的字段，而无需修改核心代码。本指南将详细介绍如何为考勤模块添加自定义字段。

## 方法一：通过自定义应用（推荐）

### 步骤1：创建自定义应用

```bash
# 在bench目录下创建自定义应用
bench new-app custom_attendance_fields

# 安装应用到站点
bench --site your-site.com install-app custom_attendance_fields
```

### 步骤2：创建字段配置文件

创建文件：`custom_attendance_fields/custom_attendance_fields/attendance_fields.py`

```python
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_attendance_custom_fields():
    """为考勤文档类型创建自定义字段"""
    
    custom_fields = {
        "Attendance": [
            # 1. 添加自定义考勤信息区域
            {
                "fieldname": "custom_attendance_section",
                "fieldtype": "Section Break",
                "label": "自定义考勤信息",
                "insert_after": "details_section",
                "collapsible": 1,
                "collapsed": 0,
            },
            
            # 2. 工作地点字段
            {
                "fieldname": "work_location",
                "fieldtype": "Select",
                "label": "工作地点",
                "options": "\n办公室\n远程办公\n出差\n客户现场\n其他",
                "insert_after": "custom_attendance_section",
                "reqd": 0,
                "in_standard_filter": 1,
                "in_list_view": 1,
            },
            
            # 3. 加班时长字段
            {
                "fieldname": "overtime_hours",
                "fieldtype": "Float",
                "label": "加班时长(小时)",
                "precision": "2",
                "insert_after": "work_location",
                "reqd": 0,
                "description": "记录当日加班时长",
            },
            
            # 4. 考勤备注字段
            {
                "fieldname": "attendance_note",
                "fieldtype": "Small Text",
                "label": "考勤备注",
                "insert_after": "overtime_hours",
                "reqd": 0,
                "description": "记录考勤相关说明",
            },
            
            # 5. 项目关联字段
            {
                "fieldname": "project",
                "fieldtype": "Link",
                "label": "项目",
                "options": "Project",
                "insert_after": "attendance_note",
                "reqd": 0,
                "in_standard_filter": 1,
                "description": "关联的工作项目",
            },
            
            # 6. 任务关联字段
            {
                "fieldname": "task",
                "fieldtype": "Link",
                "label": "任务",
                "options": "Task",
                "insert_after": "project",
                "reqd": 0,
                "depends_on": "project",
                "description": "关联的具体任务",
            },
            
            # 7. 考勤确认人字段
            {
                "fieldname": "attendance_verified_by",
                "fieldtype": "Link",
                "label": "考勤确认人",
                "options": "User",
                "insert_after": "task",
                "reqd": 0,
                "description": "确认考勤记录的人员",
            },
            
            # 8. 确认时间字段
            {
                "fieldname": "verification_date",
                "fieldtype": "Datetime",
                "label": "确认时间",
                "insert_after": "attendance_verified_by",
                "read_only": 1,
                "description": "考勤确认的时间",
            },
            
            # 9. 考勤类别字段
            {
                "fieldname": "attendance_category",
                "fieldtype": "Select",
                "label": "考勤类别",
                "options": "\n正常出勤\n加班\n出差\n培训\n会议\n病假\n事假\n年假\n调休\n其他",
                "insert_after": "verification_date",
                "reqd": 0,
                "in_standard_filter": 1,
                "description": "考勤的具体类别",
            },
            
            # 10. 考勤原因字段
            {
                "fieldname": "attendance_reason",
                "fieldtype": "Select",
                "label": "考勤原因",
                "options": "\n正常工作\n项目加班\n紧急任务\n客户会议\n培训学习\n出差办公\n其他",
                "insert_after": "attendance_category",
                "reqd": 0,
                "depends_on": "eval:doc.attendance_category in ['加班', '出差', '培训', '会议']",
                "description": "考勤的具体原因",
            },
            
            # 11. 地理位置字段
            {
                "fieldname": "location_coordinates",
                "fieldtype": "Data",
                "label": "地理位置坐标",
                "insert_after": "attendance_reason",
                "reqd": 0,
                "hidden": 1,
                "description": "GPS坐标信息",
            },
            
            # 12. 设备信息字段
            {
                "fieldname": "checkin_device",
                "fieldtype": "Data",
                "label": "签到设备",
                "insert_after": "location_coordinates",
                "reqd": 0,
                "description": "签到使用的设备信息",
            },
        ]
    }
    
    # 创建自定义字段
    create_custom_fields(custom_fields, ignore_validate=True)
    
    # 更新文档类型元数据
    frappe.clear_cache(doctype="Attendance")

def remove_attendance_custom_fields():
    """移除考勤自定义字段"""
    from frappe.custom.doctype.custom_field.custom_field import delete_custom_field
    
    fields_to_delete = [
        "Attendance-custom_attendance_section",
        "Attendance-work_location",
        "Attendance-overtime_hours",
        "Attendance-attendance_note",
        "Attendance-project",
        "Attendance-task",
        "Attendance-attendance_verified_by",
        "Attendance-verification_date",
        "Attendance-attendance_category",
        "Attendance-attendance_reason",
        "Attendance-location_coordinates",
        "Attendance-checkin_device"
    ]
    
    for field in fields_to_delete:
        if frappe.db.exists("Custom Field", field):
            delete_custom_field(field)
    
    # 清除缓存
    frappe.clear_cache(doctype="Attendance")

# 如果直接运行此文件
if __name__ == "__main__":
    create_attendance_custom_fields()
```

### 步骤3：创建应用配置文件

创建文件：`custom_attendance_fields/hooks.py`

```python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "custom_attendance_fields"
app_title = "Custom Attendance Fields"
app_publisher = "Your Company"
app_description = "Custom fields for attendance management"
app_email = "your-email@example.com"
app_license = "MIT"

# 应用安装时执行
on_setup = "custom_attendance_fields.setup.create_custom_fields"

# 应用卸载时执行
on_uninstall = "custom_attendance_fields.setup.remove_custom_fields"

# 包含的JavaScript文件
app_include_js = [
    "assets/custom_attendance_fields/js/custom_attendance.js"
]

# 包含的CSS文件
app_include_css = [
    "assets/custom_attendance_fields/css/custom_attendance.css"
]

# 文档类型权限
doc_events = {
    "Attendance": {
        "validate": "custom_attendance_fields.events.validate_attendance",
        "before_save": "custom_attendance_fields.events.before_save_attendance",
        "after_insert": "custom_attendance_fields.events.after_insert_attendance",
    }
}
```

### 步骤4：创建setup.py文件

创建文件：`custom_attendance_fields/setup.py`

```python
import frappe
from .attendance_fields import create_attendance_custom_fields, remove_attendance_custom_fields

def create_custom_fields():
    """创建所有自定义字段"""
    create_attendance_custom_fields()
    frappe.msgprint("自定义考勤字段创建成功！")

def remove_custom_fields():
    """移除所有自定义字段"""
    remove_attendance_custom_fields()
    frappe.msgprint("自定义考勤字段已移除！")
```

### 步骤5：创建事件处理文件

创建文件：`custom_attendance_fields/events.py`

```python
import frappe
from frappe.utils import now_datetime

def validate_attendance(doc, method):
    """验证考勤记录"""
    
    # 验证加班时长不能为负数
    if doc.overtime_hours and doc.overtime_hours < 0:
        frappe.throw("加班时长不能为负数")
    
    # 验证加班时长不能超过24小时
    if doc.overtime_hours and doc.overtime_hours > 24:
        frappe.throw("加班时长不能超过24小时")
    
    # 如果选择了项目，验证项目是否存在
    if doc.project and not frappe.db.exists("Project", doc.project):
        frappe.throw("选择的项目不存在")
    
    # 如果选择了任务，验证任务是否存在且属于选择的项目
    if doc.task:
        if not frappe.db.exists("Task", doc.task):
            frappe.throw("选择的任务不存在")
        elif doc.project:
            task_project = frappe.db.get_value("Task", doc.task, "project")
            if task_project != doc.project:
                frappe.throw("选择的任务不属于选择的项目")

def before_save_attendance(doc, method):
    """保存前的处理"""
    
    # 自动计算工作时长（如果有签到和签退时间）
    if doc.in_time and doc.out_time:
        from frappe.utils import time_diff_in_hours
        doc.working_hours = time_diff_in_hours(doc.out_time, doc.in_time)
    
    # 如果状态是加班，设置默认加班时长
    if doc.status == "Present" and doc.overtime_hours and doc.overtime_hours > 0:
        if not doc.attendance_category:
            doc.attendance_category = "加班"
    
    # 设置默认工作地点
    if not doc.work_location:
        doc.work_location = "办公室"

def after_insert_attendance(doc, method):
    """插入后的处理"""
    
    # 记录创建日志
    frappe.logger().info(f"创建考勤记录: {doc.name} - 员工: {doc.employee}")
    
    # 发送通知（如果需要）
    if doc.attendance_verified_by:
        send_verification_notification(doc)

def send_verification_notification(doc):
    """发送考勤确认通知"""
    try:
        # 创建通知
        notification = frappe.get_doc({
            "doctype": "Notification",
            "subject": f"考勤记录需要确认 - {doc.employee_name}",
            "type": "Alert",
            "document_type": "Attendance",
            "document_name": doc.name,
            "for_user": doc.attendance_verified_by,
            "message": f"员工 {doc.employee_name} 的考勤记录需要您确认。",
        })
        notification.insert()
    except Exception as e:
        frappe.logger().error(f"发送考勤确认通知失败: {str(e)}")
```

### 步骤6：创建JavaScript控制器

创建文件：`custom_attendance_fields/assets/custom_attendance_fields/js/custom_attendance.js`

```javascript
// 自定义考勤字段的JavaScript控制器
frappe.ui.form.on('Attendance', {
    refresh: function(frm) {
        // 页面刷新时的处理
        setup_custom_fields(frm);
    },
    
    work_location: function(frm) {
        // 工作地点变化时的处理
        if (frm.doc.work_location === '出差') {
            frm.set_df_property('attendance_reason', 'reqd', 1);
            frm.set_df_property('attendance_category', 'reqd', 1);
        } else {
            frm.set_df_property('attendance_reason', 'reqd', 0);
            frm.set_df_property('attendance_category', 'reqd', 0);
        }
    },
    
    attendance_category: function(frm) {
        // 考勤类别变化时的处理
        if (frm.doc.attendance_category === '加班') {
            frm.set_df_property('overtime_hours', 'reqd', 1);
            frm.set_df_property('attendance_reason', 'reqd', 1);
        } else {
            frm.set_df_property('overtime_hours', 'reqd', 0);
            frm.set_df_property('attendance_reason', 'reqd', 0);
        }
    },
    
    project: function(frm) {
        // 项目变化时清空任务
        frm.set_value('task', '');
        frm.refresh_field('task');
    },
    
    overtime_hours: function(frm) {
        // 加班时长变化时的处理
        if (frm.doc.overtime_hours && frm.doc.overtime_hours > 0) {
            if (!frm.doc.attendance_category) {
                frm.set_value('attendance_category', '加班');
            }
        }
    }
});

function setup_custom_fields(frm) {
    // 设置自定义字段的初始状态
    if (frm.doc.work_location === '出差') {
        frm.set_df_property('attendance_reason', 'reqd', 1);
    }
    
    if (frm.doc.attendance_category === '加班') {
        frm.set_df_property('overtime_hours', 'reqd', 1);
    }
    
    // 添加自定义按钮
    frm.add_custom_button(__('验证考勤'), function() {
        verify_attendance(frm);
    }, __('Actions'));
    
    frm.add_custom_button(__('导出详细报告'), function() {
        export_detailed_report(frm);
    }, __('Actions'));
}

function verify_attendance(frm) {
    // 验证考勤记录
    frappe.call({
        method: 'custom_attendance_fields.api.verify_attendance',
        args: {
            attendance_id: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint({
                    title: __('验证结果'),
                    message: r.message,
                    indicator: 'green'
                });
                frm.refresh();
            }
        }
    });
}

function export_detailed_report(frm) {
    // 导出详细报告
    frappe.call({
        method: 'custom_attendance_fields.api.export_detailed_report',
        args: {
            attendance_id: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                // 下载文件
                window.open(r.message, '_blank');
            }
        }
    });
}
```

### 步骤7：创建API文件

创建文件：`custom_attendance_fields/api.py`

```python
import frappe
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist()
def verify_attendance(attendance_id):
    """验证考勤记录"""
    try:
        attendance = frappe.get_doc("Attendance", attendance_id)
        
        # 设置验证信息
        attendance.attendance_verified_by = frappe.session.user
        attendance.verification_date = now_datetime()
        attendance.save()
        
        return "考勤记录验证成功！"
    except Exception as e:
        frappe.logger().error(f"验证考勤记录失败: {str(e)}")
        return f"验证失败: {str(e)}"

@frappe.whitelist()
def export_detailed_report(attendance_id):
    """导出详细报告"""
    try:
        attendance = frappe.get_doc("Attendance", attendance_id)
        
        # 生成报告内容
        report_content = generate_attendance_report(attendance)
        
        # 创建文件
        file_name = f"attendance_report_{attendance_id}_{frappe.utils.nowdate()}.txt"
        file_path = frappe.get_site_path('private', 'files', file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 创建文件记录
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "file_url": f"/private/files/{file_name}",
            "attached_to_doctype": "Attendance",
            "attached_to_name": attendance_id
        })
        file_doc.insert()
        
        return file_doc.file_url
    except Exception as e:
        frappe.logger().error(f"导出报告失败: {str(e)}")
        return None

def generate_attendance_report(attendance):
    """生成考勤报告内容"""
    report = f"""
考勤详细报告
============

员工信息:
- 员工ID: {attendance.employee}
- 员工姓名: {attendance.employee_name}
- 部门: {attendance.department}
- 公司: {attendance.company}

考勤信息:
- 考勤日期: {attendance.attendance_date}
- 考勤状态: {attendance.status}
- 工作地点: {getattr(attendance, 'work_location', '未设置')}
- 考勤类别: {getattr(attendance, 'attendance_category', '未设置')}
- 考勤原因: {getattr(attendance, 'attendance_reason', '未设置')}

时间信息:
- 签到时间: {attendance.in_time or '未记录'}
- 签退时间: {attendance.out_time or '未记录'}
- 工作时长: {attendance.working_hours or 0} 小时
- 加班时长: {getattr(attendance, 'overtime_hours', 0)} 小时

项目信息:
- 项目: {getattr(attendance, 'project', '未设置')}
- 任务: {getattr(attendance, 'task', '未设置')}

备注信息:
- 考勤备注: {getattr(attendance, 'attendance_note', '无')}

验证信息:
- 确认人: {getattr(attendance, 'attendance_verified_by', '未确认')}
- 确认时间: {getattr(attendance, 'verification_date', '未确认')}

生成时间: {now_datetime()}
"""
    return report
```

## 方法二：通过控制台直接创建

### 步骤1：使用bench控制台

```bash
# 进入bench控制台
bench --site your-site.com console
```

### 步骤2：执行创建命令

```python
# 在控制台中执行以下代码
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

# 创建加班时长字段
create_custom_field(
    doctype="Attendance",
    fieldname="overtime_hours",
    fieldtype="Float",
    label="加班时长(小时)",
    precision="2",
    insert_after="work_location",
    reqd=0
)

# 创建考勤备注字段
create_custom_field(
    doctype="Attendance",
    fieldname="attendance_note",
    fieldtype="Small Text",
    label="考勤备注",
    insert_after="overtime_hours",
    reqd=0
)

print("自定义字段创建成功！")
```

## 方法三：通过Web界面创建

### 步骤1：访问自定义字段页面

1. 登录到Frappe系统
2. 进入 **设置** > **自定义** > **自定义字段**
3. 点击 **新建**

### 步骤2：配置字段信息

填写以下信息：
- **文档类型**: Attendance
- **字段名**: work_location
- **标签**: 工作地点
- **字段类型**: Select
- **选项**: 
  ```
  办公室
  远程办公
  出差
  客户现场
  其他
  ```
- **插入位置**: details_section
- **必填**: 否

### 步骤3：保存并重复

保存后继续创建其他字段。

## 验证和测试

### 步骤1：检查字段是否创建成功

```python
# 在控制台中检查
import frappe
meta = frappe.get_meta("Attendance")
custom_fields = [f for f in meta.fields if f.custom]
print("自定义字段:", [f.fieldname for f in custom_fields])
```

### 步骤2：测试字段功能

1. 创建新的考勤记录
2. 检查自定义字段是否显示
3. 测试字段的验证逻辑
4. 测试字段的依赖关系

### 步骤3：检查导入功能

```python
# 更新导入模板以包含自定义字段
from hrms.hr.doctype.upload_attendance.upload_attendance import add_header
import frappe.utils.csvutils as csvutils

def custom_add_header(w):
    """自定义的头部添加函数"""
    w.writerow(["Notes:"])
    w.writerow(["Please do not change the template headings"])
    w.writerow([
        "ID", "Employee", "Employee Name", "Date", "Status", 
        "Leave Type", "Company", "Naming Series",
        "Work Location", "Overtime Hours", "Attendance Note",  # 自定义字段
        "Project", "Task", "Attendance Category", "Attendance Reason"  # 自定义字段
    ])
    return w
```

## 常见问题和解决方案

### 问题1：字段不显示

**解决方案**：
```python
# 清除缓存
frappe.clear_cache(doctype="Attendance")
frappe.clear_cache()

# 重新加载页面
```

### 问题2：字段验证失败

**解决方案**：
```python
# 检查字段配置
field = frappe.get_doc("Custom Field", "Attendance-work_location")
print(field.as_dict())

# 重新创建字段
frappe.delete_doc("Custom Field", "Attendance-work_location")
create_custom_field(...)
```

### 问题3：导入功能不工作

**解决方案**：
```python
# 更新导入模板
def update_import_template():
    # 修改upload_attendance.py中的add_header函数
    pass
```

## 最佳实践

1. **命名规范**：使用有意义的字段名，避免与现有字段冲突
2. **权限控制**：确保只有授权用户可以访问自定义字段
3. **数据验证**：为重要字段添加验证逻辑
4. **性能考虑**：避免创建过多不必要的字段
5. **文档记录**：记录所有自定义字段的用途和配置

## 总结

通过以上方法，您可以成功地为Frappe HRMS的考勤模块添加自定义字段。推荐使用自定义应用的方式，因为它提供了更好的可维护性和扩展性。记住在实施前备份数据，并在测试环境中验证功能。
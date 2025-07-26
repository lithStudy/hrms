# 自定义考勤状态配置
# 用于修改考勤状态选项

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def customize_attendance_status():
    """自定义考勤状态选项"""
    
    # 方法1：通过属性设置器修改状态选项
    make_property_setter(
        doctype="Attendance",
        fieldname="status", 
        property="options",
        value="\nPresent\nAbsent\nOn Leave\nHalf Day\nWork From Home\n出差\n培训\n会议\n其他",
        property_type="Text"
    )
    
    # 方法2：通过自定义字段添加新的状态字段
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    
    custom_fields = {
        "Attendance": [
            {
                "fieldname": "custom_status_section",
                "fieldtype": "Section Break", 
                "label": "自定义状态",
                "insert_after": "status",
            },
            {
                "fieldname": "attendance_category",
                "fieldtype": "Select",
                "label": "考勤类别",
                "options": "\n正常出勤\n加班\n出差\n培训\n会议\n病假\n事假\n年假\n其他",
                "insert_after": "custom_status_section",
            },
            {
                "fieldname": "attendance_reason",
                "fieldtype": "Select",
                "label": "考勤原因",
                "options": "\n正常工作\n项目加班\n紧急任务\n客户会议\n培训学习\n出差办公\n其他",
                "depends_on": "eval:doc.attendance_category in ['加班', '出差', '培训', '会议']",
                "insert_after": "attendance_category",
            },
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)

def reset_attendance_status():
    """重置考勤状态为默认值"""
    make_property_setter(
        doctype="Attendance",
        fieldname="status",
        property="options", 
        value="\nPresent\nAbsent\nOn Leave\nHalf Day\nWork From Home",
        property_type="Text"
    )

if __name__ == "__main__":
    customize_attendance_status()
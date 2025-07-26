# 自定义考勤字段配置
# 将此文件放在您的自定义应用中

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
                "fieldname": "column_break_custom",
                "fieldtype": "Column Break",
                "insert_after": "attendance_note",
            },
            {
                "fieldname": "project",
                "fieldtype": "Link",
                "label": "项目",
                "options": "Project",
                "insert_after": "column_break_custom",
            },
            {
                "fieldname": "task",
                "fieldtype": "Link",
                "label": "任务",
                "options": "Task",
                "depends_on": "project",
                "insert_after": "project",
            },
            {
                "fieldname": "attendance_verified_by",
                "fieldtype": "Link",
                "label": "考勤确认人",
                "options": "User",
                "insert_after": "task",
            },
            {
                "fieldname": "verification_date",
                "fieldtype": "Datetime",
                "label": "确认时间",
                "read_only": 1,
                "insert_after": "attendance_verified_by",
            },
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)

def remove_attendance_custom_fields():
    """移除考勤自定义字段"""
    from frappe.custom.doctype.custom_field.custom_field import delete_custom_field
    
    fields_to_delete = [
        "Attendance-work_location",
        "Attendance-overtime_hours", 
        "Attendance-attendance_note",
        "Attendance-project",
        "Attendance-task",
        "Attendance-attendance_verified_by",
        "Attendance-verification_date"
    ]
    
    for field in fields_to_delete:
        if frappe.db.exists("Custom Field", field):
            delete_custom_field(field)

if __name__ == "__main__":
    create_attendance_custom_fields()
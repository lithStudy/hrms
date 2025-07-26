#!/usr/bin/env python3
"""
快速设置考勤自定义字段脚本
使用方法：
1. 将此文件放在bench目录下
2. 运行: bench --site your-site.com execute quick_custom_fields_setup.py
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_custom_attendance_fields():
    """快速设置考勤自定义字段"""
    
    print("开始创建考勤自定义字段...")
    
    # 定义自定义字段
    custom_fields = {
        "Attendance": [
            # 自定义考勤信息区域
            {
                "fieldname": "custom_attendance_section",
                "fieldtype": "Section Break",
                "label": "自定义考勤信息",
                "insert_after": "details_section",
                "collapsible": 1,
                "collapsed": 0,
            },
            
            # 工作地点
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
            
            # 加班时长
            {
                "fieldname": "overtime_hours",
                "fieldtype": "Float",
                "label": "加班时长(小时)",
                "precision": "2",
                "insert_after": "work_location",
                "reqd": 0,
                "description": "记录当日加班时长",
            },
            
            # 考勤备注
            {
                "fieldname": "attendance_note",
                "fieldtype": "Small Text",
                "label": "考勤备注",
                "insert_after": "overtime_hours",
                "reqd": 0,
                "description": "记录考勤相关说明",
            },
            
            # 项目关联
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
            
            # 任务关联
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
            
            # 考勤确认人
            {
                "fieldname": "attendance_verified_by",
                "fieldtype": "Link",
                "label": "考勤确认人",
                "options": "User",
                "insert_after": "task",
                "reqd": 0,
                "description": "确认考勤记录的人员",
            },
            
            # 确认时间
            {
                "fieldname": "verification_date",
                "fieldtype": "Datetime",
                "label": "确认时间",
                "insert_after": "attendance_verified_by",
                "read_only": 1,
                "description": "考勤确认的时间",
            },
            
            # 考勤类别
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
            
            # 考勤原因
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
        ]
    }
    
    try:
        # 创建自定义字段
        create_custom_fields(custom_fields, ignore_validate=True)
        
        # 清除缓存
        frappe.clear_cache(doctype="Attendance")
        frappe.clear_cache()
        
        print("✅ 考勤自定义字段创建成功！")
        print("已添加的字段：")
        for field in custom_fields["Attendance"]:
            print(f"  - {field['label']} ({field['fieldname']})")
        
        print("\n📝 下一步操作：")
        print("1. 刷新浏览器页面")
        print("2. 进入考勤记录页面查看新字段")
        print("3. 测试字段功能")
        
    except Exception as e:
        print(f"❌ 创建自定义字段失败: {str(e)}")
        frappe.logger().error(f"创建自定义字段失败: {str(e)}")

def remove_custom_attendance_fields():
    """移除考勤自定义字段"""
    
    print("开始移除考勤自定义字段...")
    
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
    ]
    
    from frappe.custom.doctype.custom_field.custom_field import delete_custom_field
    
    removed_count = 0
    for field in fields_to_delete:
        if frappe.db.exists("Custom Field", field):
            try:
                delete_custom_field(field)
                removed_count += 1
                print(f"  - 已移除: {field}")
            except Exception as e:
                print(f"  - 移除失败: {field} - {str(e)}")
    
    # 清除缓存
    frappe.clear_cache(doctype="Attendance")
    frappe.clear_cache()
    
    print(f"✅ 已移除 {removed_count} 个自定义字段")

def check_existing_custom_fields():
    """检查现有的自定义字段"""
    
    print("检查现有的考勤自定义字段...")
    
    meta = frappe.get_meta("Attendance")
    custom_fields = [f for f in meta.fields if f.custom]
    
    if custom_fields:
        print("现有的自定义字段：")
        for field in custom_fields:
            print(f"  - {field.label} ({field.fieldname})")
    else:
        print("没有找到自定义字段")
    
    return custom_fields

def update_import_template():
    """更新导入模板以包含自定义字段"""
    
    print("更新导入模板...")
    
    try:
        # 获取upload_attendance模块
        from hrms.hr.doctype.upload_attendance import upload_attendance
        
        # 备份原始函数
        original_add_header = upload_attendance.add_header
        
        def custom_add_header(w):
            """自定义的头部添加函数"""
            status = ", ".join((frappe.get_meta("Attendance").get_field("status").options or "").strip().split("\n"))
            w.writerow(["Notes:"])
            w.writerow(["Please do not change the template headings"])
            w.writerow(["Status should be one of these values: " + status])
            w.writerow(["If you are overwriting existing attendance records, 'ID' column mandatory"])
            w.writerow([
                "ID", "Employee", "Employee Name", "Date", "Status", 
                "Leave Type", "Company", "Naming Series",
                "Work Location", "Overtime Hours", "Attendance Note",  # 自定义字段
                "Project", "Task", "Attendance Category", "Attendance Reason"  # 自定义字段
            ])
            return w
        
        # 替换函数
        upload_attendance.add_header = custom_add_header
        
        print("✅ 导入模板更新成功！")
        print("现在导出的模板将包含自定义字段")
        
    except Exception as e:
        print(f"❌ 更新导入模板失败: {str(e)}")

def main():
    """主函数"""
    
    print("=" * 50)
    print("考勤自定义字段快速设置工具")
    print("=" * 50)
    
    # 检查现有字段
    existing_fields = check_existing_custom_fields()
    
    if existing_fields:
        print(f"\n发现 {len(existing_fields)} 个现有自定义字段")
        response = input("是否要移除现有字段并重新创建？(y/N): ")
        if response.lower() == 'y':
            remove_custom_attendance_fields()
            print()
    
    # 创建自定义字段
    setup_custom_attendance_fields()
    
    # 更新导入模板
    print("\n" + "=" * 30)
    response = input("是否要更新导入模板以包含自定义字段？(Y/n): ")
    if response.lower() != 'n':
        update_import_template()
    
    print("\n" + "=" * 50)
    print("设置完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
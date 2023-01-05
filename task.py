import sqlite3
from datetime import datetime, timedelta


def get_attendance(employee_code, date):
    connection = sqlite3.connect('attendance.db')
    cursor = connection.cursor()

    cursor.execute("""
                    SELECT a.day, aa.Action, aa.ActionTime
                    FROM Attendance a
                    JOIN AttendanceActions aa ON a.Id = aa.AttendanceID
                    WHERE a.employee = (?) AND a.day = (?);
                   """, (employee_code, date))

    connection.commit()

    items = cursor.fetchall()

    result = {}

    if items:
        result["attended"] = True
    else:
        result["attended"] = False
        return result

    attendance = []
    for item in items:
        time = datetime.strptime(item[2], "%Y-%m-%d %I:%M %p")
        attendance.append((item[1], time))

    if len(attendance) == 2:
        duration = attendance[1][1] - attendance[0][1]
        result["duration"] = str(duration)
    elif len(attendance) == 3:
        next_day = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
        duration = attendance[1][1] - \
            attendance[0][1] + (next_day - attendance[2][1])
        result["duration"] = str(duration)
    elif len(attendance) == 1:
        action = attendance[0][0]
        attendance_datetime = attendance[0][1]
        if action == "CheckOut":
            previous_day = datetime.strptime(
                date, "%Y-%m-%d") - timedelta(days=1)
            previous_day = previous_day.strftime("%Y-%m-%d")

            cursor.execute("""
                            SELECT a.day, aa.Action, aa.ActionTime
                            FROM Attendance a
                            JOIN AttendanceActions aa ON a.Id = aa.AttendanceID
                            WHERE a.employee = (?) AND a.day = (?) ORDER BY aa.Id desc;
                            """, (employee_code, str(previous_day)))

            connection.commit()

            previous_day_attendance = cursor.fetchone()

            previous_day_attendance_datetime = datetime.strptime(
                previous_day_attendance[2], "%Y-%m-%d %I:%M %p")

            duration = attendance_datetime - previous_day_attendance_datetime

            result["duration"] = str(duration)

    connection.close()

    return result


print(get_attendance("EMP01", "2020-04-01"))


def get_attendance_history(employee_code):
    connection = sqlite3.connect('attendance.db')
    cursor = connection.cursor()

    cursor.execute("""
                    SELECT a.day, aa.Action, aa.ActionTime
                    FROM Attendance a
                    JOIN AttendanceActions aa ON a.Id = aa.AttendanceID
                    WHERE a.employee = (?);
                     """, (employee_code,))

    connection.commit()

    attendance_records = cursor.fetchall()

    attendance_history = {
        "days": []
    }

    for attendance in attendance_records:
        time = attendance[2]
        time = datetime.strptime(time, "%Y-%m-%d %I:%M %p")
        time = time - timedelta(hours=2)
        time = time.isoformat()

        attendance_history["days"].append({
            "date": attendance[0],
            "actions": [
                {
                    "action": attendance[1],
                    "time": time
                }
            ]
        })

    connection.close()

    return attendance_history


print(get_attendance_history("EMP01"))

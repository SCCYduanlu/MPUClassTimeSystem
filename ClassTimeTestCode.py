from datetime import datetime, timedelta
import os
import sys
import re

from datetime import datetime, timedelta
from urllib.parse import urlparse

def is_authentication_endpoint(redirect_url):
    try:
        # 解析URL
        parsed_url = urlparse(redirect_url)
        
        # 提取路径并分割成路由
        path_segments = parsed_url.path.strip('/').split('/')
        
        # 判断第一个路由是否是 'authenticationendpoint'
        if path_segments and path_segments[0] == 'authenticationendpoint':
            return True
        return False
    except Exception as e:
        print(f"Error parsing URL: {e}")
        return False

def get_month_boundaries(class_schedule):
    # 提取所有的日期并转为 datetime 对象
    dates = [datetime.strptime(item['date'], "%Y/%m/%d") for item in class_schedule]

    if not dates:  # 如果没有任何课程数据
        return earliest_month_first_day, latest_month_last_day

    # 找到最早和最晚的日期
    earliest_date = min(dates)
    latest_date = max(dates)

    # 获取最早日期所在月份的第一天
    earliest_month_first_day = earliest_date.replace(day=1)

    # 获取最晚日期所在月份的最后一天
    latest_month_last_day = (latest_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    

    return earliest_month_first_day, latest_month_last_day



def generate_calendar_html(course_schedule, start_month, end_month, output_file):
    """
    根据课表生成日历 HTML 文件。

    :param course_schedule: list, 每天的课程表，为列表，包含字典格式的课程信息。
    :param start_month: datetime, 日历的起始月份。
    :param end_month: datetime, 日历的结束月份。
    :param output_file: str, 生成的 HTML 文件路径。
    """
    # 初始化 HTML 内容
    html_content = """<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>课表日历</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: url('1.png') no-repeat center center fixed;
            background-size: cover;
            font-family: 'Arial', sans-serif;
            color: #333;
        }

        .calendar-container {
            background: rgba(255, 255, 255, 0.65); /* 增加透明度 */
            border-radius: 15px;
            padding: 20px;
            margin: 20px auto;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            max-width: 1200px;
            overflow-y: auto;
            height: 90vh;
        }

        .month {
            text-align: center;
            font-size: 36px; /* 增大月份标题字体 */
            font-weight: bold;
            margin: 20px 0;
            color: #4a4e69;
        }

        .weekdays, .days {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            text-align: center;
        }

        .day {
            padding: 12px; /* 加大内边距 */
            margin: 4px;
            border-radius: 12px;
            background: rgba(240, 248, 255, 0.7); /* 进一步增加透明度 */
            box-shadow: 3px 3px 8px rgba(209, 217, 230, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.7);
            font-size: 18px; /* 整体字体变大 */
            transition: all 0.3s ease;
        }

        .day:hover {
            transform: scale(1.03);
            box-shadow: 4px 4px 12px rgba(203, 213, 224, 0.7), -4px -4px 12px rgba(255, 255, 255, 0.8);
        }

        .day.empty {
            background: transparent;
            box-shadow: none;
        }

        .day .date {
            font-weight: bold;
            font-size: 20px; /* 日期字体更大 */
            color: #333;
        }

        .course {
            margin-top: 10px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.45); /* 课程框的透明度增加 */
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            font-size: 16px; /* 增大课程信息字体 */
            color: #555;
            line-height: 1.5;
        }

        .course div {
            margin-bottom: 5px;
        }

        .course strong {
            color: #4a4e69;
            font-size: 18px; /* 课程标题更突出 */
        }


        
        .time {
            font-size: 17px; /* 字体变大 */
            font-weight: bold; /* 加粗 */
            color: #1e3a8a; /* 深蓝色，突出显示 */
            margin-top: 5px; /* 与其他信息稍微拉开间距 */
            text-align: center; /* 居中对齐 */
        }
    </style>


</head>
<body>
    <div class='calendar-container'>"""

    # 转换输入的课程表为日期键的字典
    schedule_dict = {}
    for entry in course_schedule:
        date = entry['date']
        course_info = {
            'class_code': entry['class_code'],
            'subject_name': entry['subject_name'],
            'lecturer': entry['lecturer'],
            'classroom': entry['classroom'],
            'time': entry['time']
        }
        if date not in schedule_dict:
            schedule_dict[date] = []
        schedule_dict[date].append(course_info)

    current_date = datetime(start_month.year, start_month.month, 1)
    while current_date <= end_month:
        # 添加月份标题
        html_content += f"<div class='month'>{current_date.strftime('%Y年%m月')}</div>"
        html_content += "<div class='weekdays'>"
        html_content += "".join([
            '<div style="padding: 20px 0; font-size: 20px;">一</div>',
            '<div style="padding: 20px 0; font-size: 20px;">二</div>',
            '<div style="padding: 20px 0; font-size: 20px;">三</div>',
            '<div style="padding: 20px 0; font-size: 20px;">四</div>',
            '<div style="padding: 20px 0; font-size: 20px;">五</div>',
            '<div style="padding: 20px 0; font-size: 20px;">六</div>',
            '<div style="padding: 20px 0; font-size: 20px;">日</div>'
        ])

        html_content += "</div><div class='days'>"

        # 找到当前月份的第一天和最后一天
        first_day_of_month = current_date
        last_day_of_month = (current_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # 添加空白填充至第一个星期
        for _ in range(first_day_of_month.weekday()):
            html_content += "<div class='day empty'></div>"

        # 添加日期
        day = first_day_of_month
        while day <= last_day_of_month:
            day_str = day.strftime("%Y/%m/%d")
            if day_str in schedule_dict:
                # 如果当天有课程
                courses_html = "".join([f"""
                    <div class='course'>
                        <div><strong>{course['subject_name']}</strong></div>
                        <div>{course['class_code']}</div>
                        <div>{course['lecturer']}</div>
                        <div><strong>{course['classroom']}<strong></div>
                        <div class='time'>{course['time']}</div>
                    </div>""" for course in schedule_dict[day_str]])
                html_content += f"<div class='day'><div class='date'>{day.day}</div>{courses_html}</div>"
            else:
                # 如果当天没有课程
                html_content += f"<div class='day'><div class='date'>{day.day}</div></div>"
            day += timedelta(days=1)

        # 添加空白填充至最后一个星期
        for _ in range(6 - last_day_of_month.weekday()):
            html_content += "<div class='day empty'></div>"

        html_content += "</div>"  # 结束 days
        current_date += timedelta(days=31)
        current_date = current_date.replace(day=1)  # 跳到下个月

    # 结束 HTML
    html_content += "</div></body></html>"

    # 保存 HTML 文件
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)


    print(f"课表已生成：{output_file}")




import requests
from bs4 import BeautifulSoup
import ssl
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import chardet
from collections import defaultdict
import getpass

from datetime import datetime, timedelta

def find_dates(time_variable, weekdays):
    """
    从给定的时间段或日期中找到符合特定星期的日期。

    :param time_variable: str, 可以是时间段 (如 "2024/09/01-2024/10/05") 或单个日期 (如 "2024/10/08")。
    :param weekdays: list, 包含 0-7 的数字，0 表示星期天，1 表示星期一，以此类推。
    :return: list, 符合条件的日期列表，格式为 "YYYY/MM/DD"。
    """

    weekdays = set(weekdays)  # 去重并转为集合，便于快速查找
    print(Style.BRIGHT + Fore.CYAN + "课程时间段及周期")
    print(time_variable)
    print(weekdays)

    
    
    # 判断时间变量的格式
    if '-' in time_variable:  # 时间段
        start_date_str, end_date_str = time_variable.split('-')
        start_date = datetime.strptime(start_date_str.strip(), "%Y/%m/%d")
        end_date = datetime.strptime(end_date_str.strip(), "%Y/%m/%d")
        
        current_date = start_date
        result_dates = []
        while current_date <= end_date:
            if current_date.weekday() in weekdays:  # weekday() 返回 0 (周一) 到 6 (周日)
                result_dates.append(current_date.strftime("%Y/%m/%d"))
            current_date += timedelta(days=1)
        return result_dates

    else:  # 单个日期
        single_date = datetime.strptime(time_variable.strip(), "%Y/%m/%d")
        if single_date.weekday() in weekdays:
            print(single_date.weekday())
            return [single_date.strftime("%Y/%m/%d")]
        else:
            return []
        

def sort_key(entry):
    # 解析日期和开始时间
    date = datetime.strptime(entry['date'], '%Y/%m/%d')
    start_time = datetime.strptime(entry['time'].split('-')[0], '%H:%M')
    return (date, start_time)



# 自定义适配器，允许不安全的 SSL 重协商
class UnsafeSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT  # 允许不安全的 SSL 重协商
        context.set_ciphers('DEFAULT:@SECLEVEL=0')  # 降低安全级别
        kwargs['ssl_context'] = context
        return super(UnsafeSSLAdapter, self).init_poolmanager(*args, **kwargs)

# 登录页面和重定向页面的 URL
login_url = "https://banner-prod-xe-01.ipm.edu.mo:8446/BannerExtensibility/customPage/page/StudentHomePage"
base_url = "https://account.ipm.edu.mo/commonauth"



# 创建会话并使用自定义的 SSL 适配器
session = requests.Session()
session.mount('https://', UnsafeSSLAdapter())
from colorama import Fore, Back, Style


# 发送 GET 请求，获取登录页面内容
print(Style.BRIGHT + Fore.CYAN + "\n" + "=" * 40)
print(Fore.GREEN + "欢迎使用理工课表提取系统")
print("版本: " + Style.BRIGHT + Fore.YELLOW + "V0.0.2 测试版")
print(Fore.MAGENTA + "你输入的所有信息不会以任何形式传输到第三方平台，仅限用于向学校官网请求课表")
print(Fore.CYAN + "Make By Chieri")
print("=" * 40 + "\n" + Style.RESET_ALL)


print(Style.BRIGHT + Fore.CYAN + """
╔════════════════════════════════╗
║        选择理工  迈向成功      ║
╚════════════════════════════════╝
""" + Style.RESET_ALL)

print(Fore.CYAN + "正在请求一次性登录验证 token...")
try:
    response = session.get(login_url, timeout=30)
    if response.status_code == 200:
        # print("成功获取登录页面!")
        
        # 使用 BeautifulSoup 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取隐藏字段中的参数
        session_data_key = soup.find('input', {'name': 'sessionDataKey'})['value']


        print(Fore.GREEN + f"验证 Token: {session_data_key}")

        # 用户信息
        print(Fore.CYAN + "\n请输入以下登录信息:")
        username = input(Fore.YELLOW + "学生账号: ")
        password = getpass.getpass(Fore.YELLOW + "学生账号密码 (输入时不会显示): ")
        print(Fore.GREEN + "密码输入完成！")

        login_payload = {
            'usernameUserInput': username,
            'username': f"{username}@carbon.super",
            'password': password,
            'sessionDataKey': session_data_key,
        }

        response = session.post(base_url, data=login_payload, allow_redirects=False)

        # 检查是否发生重定向 (302 Found)
        if response.status_code == 302:
            # 获取重定向的 URL（CAS 登录页面）
            redirect_url = response.headers['Location']
            print(Fore.CYAN + f"重定向到: {redirect_url}")
            if is_authentication_endpoint(redirect_url):
                print(Style.BRIGHT + Fore.RED + "account.ipm.edu.mo:Login failed! Please recheck the username and password and try again.!!!\n账号或密码错误，请重新运行该文件!!!" + Style.RESET_ALL)
                input("\n按下 Enter 键退出程序...")
                sys.exit()



            # 第二步：发送 GET 请求，访问重定向 URL
            response = session.get(redirect_url, allow_redirects=False)

            # 如果成功重定向到 CAS 登录页面，继续进行登录操作
            if response.status_code == 302:
                # 获取新的 sessionDataKey
                new_session_data_key = response.headers['Location'].split('sessionDataKey=')[-1]
                print(Fore.CYAN + f"新 Session Key: {new_session_data_key}")

        
        
            # 访问指定页面（time_stud.asp）
            next_page_url = f"https://wapps2.ipm.edu.mo/siweb_cas/time_stud.asp?la=ch"
            time_data = {
                "la": "ch",
            }
            next_response = session.get(next_page_url, data=time_data, timeout=30)
            next_response = session.get(next_page_url, data=time_data, timeout=30) #必须两次才能出中文课表

            if next_response.status_code == 200:
                print(Fore.GREEN + "成功获取课表数据！正在整理课表...")
                
                detected_encoding = chardet.detect(next_response.content)['encoding']

                # 使用检测到的编码重新解码
                next_response.encoding = detected_encoding
                soup = BeautifulSoup(next_response.text, 'html.parser')



                # 提取表格数据
                rows = soup.select("table[border='1'] tr")[1:]  # 跳过表头

                courses = defaultdict(list)

                current_class_code = ""
                current_subject_name = ""
                current_term = ""


                schedule = []

                TBA_message = ""

                for row in rows:
                    week_list = []
                    cols = row.find_all('td')
                    if len(cols) >= 12:
                        first_clis = cols[0].get_text(strip=True) or current_term
                        if first_clis == "":


                            pattern = r'^(\d{4}/\d{2}/\d{2}),\s*(\w{3}),\s*(\d{2}:\d{2}-\d{2}:\d{2}),\s*(.*)$'

                            week_map = {
                                "MON": 0,
                                "TUE": 1,
                                "WED": 2,
                                "THU": 3,
                                "FRI": 4,
                                "SAT": 5,
                                "SUN": 6
                            }
                            match = re.match(pattern, cols[2].get_text(strip=True))
                            if match:
                                period = match.group(1)
                                week_list.append(week_map.get(match.group(2).upper(), None))
                                time = match.group(3)
                                classroom = match.group(4)
                            else:
                                lecturer = cols[1].get_text(strip=True)
                                classroom = cols[2].get_text(strip=True)
                                period = cols[3].get_text(strip=True)
                                time = cols[4].get_text(strip=True)
                                for i, col in enumerate(cols[-7:]):
                                    if col.find('img'):
                                        week_list.append(i-1)

                        elif "班別數目" in first_clis:
                            continue

              
                        else:
                            term = cols[0].get_text(strip=True) or current_term
                            class_code = cols[1].get_text(strip=True) or current_class_code
                            subject_name = cols[2].get_text(strip=True) or current_subject_name
                            lecturer = cols[3].get_text(strip=True)
                            classroom = cols[4].get_text(strip=True)
                            if "安排" in classroom:
                                TBA_message += f"{class_code}-{subject_name} 由老师安排\n"
                                continue
                            period = cols[5].get_text(strip=True)
                            time = cols[6].get_text(strip=True)
                            for i, col in enumerate(cols[-7:]):
                                if col.find('img'):
                                    week_list.append(i-1)


                        day_list = find_dates(period, week_list)



                        
                        class_schedule = [
                            {
                                "date": date,
                                "class_code": class_code,
                                "subject_name": subject_name,
                                "lecturer": lecturer,
                                "classroom": classroom,
                                "time": time
                            }
                            for date in day_list
                        ]
                        print(Fore.GREEN + class_code + subject_name)
                        print(Style.BRIGHT + Fore.CYAN + "\n" + "=" * 40)
                        print(class_schedule)
                        print(Style.BRIGHT + Fore.CYAN + "\n" + "=" * 40)
                        schedule += class_schedule

                # print(schedule)
                if schedule == []:
                    print(Fore.WHITE + "閣下之上課時間表暫時未能提供。\n如有任何查詢，請與招生註冊處聯絡。" + Style.RESET_ALL)
                    sys.exit()

                sorted_data = sorted(schedule, key=sort_key)

                earliest_month_first_day, latest_month_last_day = get_month_boundaries(schedule)
                output_file = f"{username}ClassTime.html"

                # 生成日历
                generate_calendar_html(sorted_data, earliest_month_first_day, latest_month_last_day, output_file)
                os.startfile(output_file)
                print(Fore.YELLOW + "该程序生成的课表仅供参考，请以学校官网课表为主。开发者无法保证该系统不出任何错误，建议生成课表后个人再检查一次~")
                print(Fore.WHITE + f"课表制作成功~")
                print(TBA_message)
                input("\n按下 Enter 键退出程序...")






                

            else:
                print(Fore.RED + f"请求课表页面失败，状态码: {next_response.status_code}")
                input("\n按下 Enter 键退出程序...")

        else:
            print(Fore.RED + "登录失败，请检查用户名和密码！")
            input("\n按下 Enter 键退出程序...")

    else:
        print(Fore.RED + f"登录页面请求失败，状态码: {response.status_code}")
        input("\n按下 Enter 键退出程序...")


except requests.exceptions.SSLError as e:
    print(Fore.RED + "SSL 错误:" + str(e))
    print("请检查电脑是否有代理网络未关闭")
    input("\n按下 Enter 键退出程序...")

except requests.exceptions.RequestException as e:
    print(Fore.RED + "请求错误:" + str(e))
    input("\n按下 Enter 键退出程序...")


from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from .models import User, UserLog, MNumber, WorkCenter, NPC
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql import select, delete
import pandas as pd
import csv
from . import resource_path
import psutil
from .generate_barcode import generate_bcode
from .scanner_logic import scan_in, scan_out

auth = Blueprint('auth', __name__)

def is_csv_opened_in_excel(csv_file):
    for proc in psutil.process_iter():
        try:
            if "EXCEL.EXE" in proc.name():
                for file in proc.open_files():
                    if csv_file.lower() in file.path.lower():
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False



@auth.route('/', methods=['GET', 'POST'])
def login():
    
    
    # the_admin = User(username='admin', password=generate_password_hash(
    #             'daniel114', method='pbkdf2', salt_length=16), full_name='Daniel Tham', employee_num = 0)
    # db.session.add(the_admin)
    # db.session.commit()
    
    # the_admin_log = UserLog(date = "N/A", full_name = 'Daniel Tham', employee_num = 0,
    #                 clock_in_time = "N/A", clock_out_time = "N/A", hours_clocked = 0, project_num = 0,
    #                 part_num = 0, hours_allocated = 0, npc = -1, machine = "", work_center = -1,  work_center_rate = "")
    # db.session.add(the_admin_log)
    # db.session.commit()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
            
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                if check_password_hash(user.password, password) and (user.username == 'admin'):
                    login_user(user, remember=True)
                    return redirect(url_for('auth.admin_portal'))
                else:
                    login_user(user, remember=True)
                    return redirect(url_for('views.employee_portal'))
            else:
                flash('Incorrect password, try again.', category='error')
                return render_template("login.html", user=current_user) 
        else:
            flash('Username does not exist.', category='error')
            return render_template("login.html", user=current_user) 

    return render_template("login.html", user=current_user)    

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/clock-in-out', methods=['GET','POST'])
def clock_in_out():
     # Use scanner to scan username to clock in and out people
        
    # input field for clock in and submit button
    # input field for clock out and submit button
    if request.method == 'POST':
        
        if request.form.get('submit_clock_in') == 'Clock In':
            
            username = request.form.get('insert_user_in')
            scan_in(username)
        
        elif request.form.get('submit_clock_out') == 'Clock Out':
            
            username = request.form.get('insert_user_out')
            scan_out(username)
        

    return render_template("clock_in_out.html", user=current_user)
    

@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_portal():   
    
    get_username = select(User.username)
    res_stmt = db.session.execute(get_username).fetchall()
    username_list = []
    
    for username_i in res_stmt:
        username_list.append(str(username_i).strip('(').strip(')').strip(',').strip('"').strip('\''))
        
    username_list.remove('admin')
    print(username_list)
    
    if request.method == 'POST':

        if request.form.get('submit_m') != 'submit_m' and request.form.get('timesheet') != 'Download Timesheet' and request.form.get('submit') == 'Submit Info':
            username = request.form.get('username') # must be unique
            full_name = request.form.get('full_name')
            employee_num = request.form.get('employee_num') # must be unique
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            

            user = User.query.filter_by(username=username).first() 
            if user:
                print("Checking Unique Username.....")
            elif len(username) < 4 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Username must be greater than 3 characters.', category='error')
                return render_template("admin.html", user=current_user)
            elif len(full_name) < 1 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Please enter full name.', category='error')
                return render_template("admin.html", user=current_user)
            elif len(password1) < 7 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Password must be at least 7 characters.', category='error')
                return render_template("admin.html", user=current_user)
            elif password1 != password2 and request.form.get('timesheet') != 'Download Timesheet':
                flash('Passwords don\'t match.', category='error')
                return render_template("admin.html", user=current_user , username_list=username_list)
            
            
            # checks for unique username number by checking db with number already created   
            username_result = ""
            
            username_val =  select(User.username).where(User.username == username)
            username_res = db.session.execute(username_val).fetchall()
            for rowb in username_res:
                username_result = rowb[0]
                
            if (str(username_result) == username) or username == "":
                flash('Please enter an unique username!', category='error')
                return render_template("admin.html", user=current_user , username_list=username_list)
                
            # checks for unique employee number checking db with number already created  
            employee_num_result = 0
            
            employee_num_val =  select(UserLog.employee_num).where(UserLog.employee_num == employee_num)
            employee_num_res = db.session.execute(employee_num_val).fetchall()
            for rowb in employee_num_res:
                employee_num_result = rowb[0]
            
            if (str(employee_num_result) == employee_num) or employee_num == "":
                flash('Please enter an unique employee number!', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            
            if request.form.get('submit') == 'Submit Info' and (len(username) < 4 or len(full_name) < 1 or len(password1) < 7 or password1 != password2 or  len(employee_num) < 1):
                flash('Some fields are empty', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)

            else: 
                
                new_user = User(username = username, password = generate_password_hash(
                    password1, method = 'pbkdf2', salt_length = 16), full_name = full_name, employee_num = employee_num)
                
                db.session.add(new_user)
                db.session.commit()

                # generates barcode
                generate_bcode(employee_num)
                
                flash('Account created!', category='success')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
        # submit m#
        elif request.form.get('submit_m') == 'Submit M#':
        
            # query 
            m_num = request.form.get('insert_m')
            
            if m_num.isalpha() or not m_num.isalnum():
                flash('Invalid Input', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            
            next_m_num = MNumber(m_num = m_num)
            db.session.add(next_m_num)
            db.session.commit()
            flash('M# Inserted', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('delete_m') == 'Delete M#':
        
            m_num = request.form.get('delete_mnum')
            
            sel_stmt = select(MNumber.m_num).where(MNumber.m_num == m_num)
            sel_stmt_res = db.session.execute(sel_stmt).fetchall()
            sel_stmt_result = 0
            
            for row in sel_stmt_res:
                sel_stmt_result = row[0]
                
            if m_num.isalpha() or not m_num.isalnum():
                flash('Invalid Input', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            
            if int(m_num) == sel_stmt_result:         
                stmt = MNumber.query.filter_by(m_num = m_num).first()
                db.session.delete(stmt)
                db.session.commit()
                flash('M# Deleted', category='success')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
            else:
                flash('M# already deleted or not in system', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('submit_npc') == 'Submit NPC':
        
            # query 
            npc = request.form.get('insert_npc')
            
            if npc.isalpha() or not npc.isalnum():
                flash('Invalid Input', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            
            next_npc = NPC(npc = npc)
            db.session.add(next_npc)
            db.session.commit()
            flash('NPC Inserted', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('delete_npc') == 'Delete NPC':
        
            # query 
            npc = request.form.get('delete_npc_form')
            
            sel_stmt = select(NPC.npc).where(NPC.npc == npc)
            sel_stmt_res = db.session.execute(sel_stmt).fetchall()
            sel_stmt_result = 0
            
            for row in sel_stmt_res:
                sel_stmt_result = row[0]
                
            if npc.isalpha() or not npc.isalnum():
                flash('Invalid Input', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            
            if int(npc) == sel_stmt_result:         
                stmt = NPC.query.filter_by(npc = npc).first()
                db.session.delete(stmt)
                db.session.commit()
                flash('NPC Deleted', category='success')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
            else:
                flash('NPC already deleted or not in system', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('submit_work_center') == 'Submit Work Center':
        
            work_center = request.form.get('insert_work_center')
        
            if work_center.isalpha() or not work_center.isalnum():
                flash('Invalid Input', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            
            next_work_center = WorkCenter(work_center = work_center, username_list=username_list)
            db.session.add(next_work_center)
            db.session.commit()
            flash('Work Center Inserted', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('delete_work_center') == 'Delete Work Center':
        
            # query 
            work_center = request.form.get('delete_work_center_form')
            
            sel_stmt = select(WorkCenter.work_center).where(WorkCenter.work_center == work_center)
            sel_stmt_res = db.session.execute(sel_stmt).fetchall()
            sel_stmt_result = 0
            
            for row in sel_stmt_res:
                sel_stmt_result = row[0]
                
            if work_center.isalpha() or not work_center.isalnum():
                flash('Invalid Input', category='error')
                return render_template("admin.html", user=current_user)
            
            if int(work_center) == sel_stmt_result:         
                stmt = WorkCenter.query.filter_by(work_center = work_center).first()
                db.session.delete(stmt)
                db.session.commit()
                flash('Work Center Deleted', category='success')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
            else:
                flash('Work Center already deleted or not in system', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list) 
        
        # Delete User Login information    
        elif request.form.get('submit_delete_user') == 'Delete User':
        
            print("testing")
            # query 
            user = request.form.get('search_filter')
            print(user)
            
            sel_stmt = select(User.username).where(User.username == user)
            sel_stmt_res = db.session.execute(sel_stmt).fetchall()
            print(sel_stmt_res)
            sel_stmt_result = 0
            
            for row in sel_stmt_res:
                sel_stmt_result = row[0]        
                
            print(sel_stmt_result)                             
            
            if user == sel_stmt_result:         
                stmt = User.query.filter_by(username = user).first()
                db.session.delete(stmt)
                db.session.commit()
                flash('User Deleted', category='success')
                return render_template("admin.html", user=current_user, username_list=username_list)
        
            else:
                flash('User already deleted or not in system', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list) 
        
            
        elif request.form.get('labourhours') == 'Download Labour Import Hours':
        
            # you can ask input for date for when to get timesheet
            csv_file_path = "LabourImportHours.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('Labour Hours Sheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            labourhours_stmt = select(db.column('project_num'), db.column('project_num'), db.column('date'), db.column('work_center'), db.column('work_center_rate'), db.column('employee_num'), db.column('machine'), db.column('hours_allocated'), db.column('part_num'), db.column('npc')).select_from(UserLog)
            result = db.session.execute(labourhours_stmt).fetchall()
            df = pd.DataFrame(result)
            df.columns = ['EMPTY', 'JOB', 'Entry Date', 'WorkCenter', 'Work Center Rate', 'Employee', 'Machine', 'Runtime', 'Operation', 'NPC']
            df['EMPTY'] = " "
            df.to_csv('./csv_files/LabourImportHours.csv', index = False)
            
            flash('Labour Hours Sheet', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)

        # Time in/out and total hours 
        elif request.form.get('timesheet') == 'Download Timesheet':
        
            # you can ask input for date for when to get timesheet
            csv_file_path = "timesheet.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('Timesheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            timesheet_stmt = select(db.column('employee_num'), db.column('clock_in_time'), db.column('clock_out_time'), db.column('hours_clocked')).select_from(UserLog)
            result = db.session.execute(timesheet_stmt).fetchall()
            df = pd.DataFrame(result)
            df.columns = ['Employee', 'Time In', 'Time Out', 'Total Hours']
            df.to_csv('./csv_files/timesheet.csv', index = False)
            
            flash('Dowloading Timesheet', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('m#') == 'Download M#s':
        
            # you can ask input for date for when to get timesheet
            
            csv_file_path = "mnum.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('M Number Sheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            m_num_stmt = select('*').select_from(MNumber)
            result = db.session.execute(m_num_stmt).fetchall()
            df = pd.DataFrame(result)
            df.to_csv('./csv_files/mnum.csv', index = False)
            
            flash('Dowloading M#s', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('workcenter') == 'Download Work Centers':
        
            # you can ask input for date for when to get timesheet
            
            csv_file_path = "workcenter.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('Work Center Sheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            workcenter_stmt = select('*').select_from(WorkCenter)
            result = db.session.execute(workcenter_stmt).fetchall()
            df = pd.DataFrame(result)
            df.to_csv('./csv_files/workcenter.csv', index = False)
            flash('Dowloading Work Centers', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('npc') == 'Download NPCs':
        
            # you can ask input for date for when to get timesheet
            
            csv_file_path = "npc.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('NPC sheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            npc_stmt = select('*').select_from(NPC)
            result = db.session.execute(npc_stmt).fetchall()
            df = pd.DataFrame(result)
            df.to_csv('./csv_files/npc.csv', index = False)
            flash('Dowloading NPCs', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('mastersheet') == 'Download Master Sheet':
        
            # you can ask input for date for when to get timesheet
            
            csv_file_path = "mastersheet.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('Mastersheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            master_stmt = select('*').select_from(UserLog)
            result = db.session.execute(master_stmt).fetchall()
            df = pd.DataFrame(result)
            df.to_csv('./csv_files/mastersheet.csv', index = False)
            flash('Dowloading Master Sheet', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
        
        elif request.form.get('users') == 'Download Users':
        
            # you can ask input for date for when to get timesheet
            
            csv_file_path = "users.csv"
            if is_csv_opened_in_excel(csv_file_path):
                flash('Users Sheet is already opened', category='error')
                return render_template("admin.html", user=current_user, username_list=username_list)
            else:
                pass
            
            # query 
            user_stmt = select('*').select_from(User)
            result = db.session.execute(user_stmt).fetchall()
            df = pd.DataFrame(result)
            df.to_csv('./csv_files/users.csv', index = False)
            flash('Dowloading Users', category='success')
            return render_template("admin.html", user=current_user, username_list=username_list)
            
        else:
            flash('Something went wrong', category='error')
            return render_template("admin.html", user=current_user, username_list=username_list) 
            
            
    return render_template("admin.html", user=current_user, username_list=username_list)    






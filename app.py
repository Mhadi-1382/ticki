
"""
Ticki (Ticket System) App
GitHub: https://github.com/Mhadi-1382/ticki
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash
from persiantools.jdatetime import JalaliDateTime
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
mySQL = MySQL(app)
mail = Mail(app)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'ticki')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'info.daha.uni@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'info.daha.uni@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.secret_key = os.urandom(24)


@app.errorhandler(404)
def not_found(e):
    return render_template('pages/404.html')


@app.route('/', methods=['GET'])
def index():
    cursor_get_tickets = mySQL.connection.cursor()
    cursor_get_tickets.execute('SELECT * FROM tickets')
    
    return render_template('index.html', get_tickets=cursor_get_tickets.fetchall())


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        signupUsername = request.form.get('signupUsername')
        signupPassword = request.form.get('signupPassword')
        signupEmail = request.form.get('signupEmail')
        signupTel = request.form.get('signupTel')
        signupDateCreated = JalaliDateTime.now().strftime('%Y-%m-%d %H:%M')

        cursor = mySQL.connection.cursor()
        if cursor.execute('SELECT email FROM users WHERE email = "{}"'.format(signupEmail)):
            flash(message='کاربری با این ایمیل وجود دارد.', category='error')
        # elif cursor.execute('SELECT username FROM users WHERE username = "{}"'.format(signupUsername)):
        #     flash(message='کاربری با این نام وجود دارد.', category='error')
        elif cursor.execute('SELECT phone FROM users WHERE phone = "{}"'.format(signupTel)):
            flash(message='کاربری با این شماره وجود دارد.', category='error')
        else:
            cursor.execute('INSERT INTO users (username, password, email, phone, date_created) VALUES (%s,%s,%s,%s,%s)', (signupUsername, signupPassword, signupEmail, signupTel, signupDateCreated,))
            mySQL.connection.commit()

            cursorRoleId = mySQL.connection.cursor()
            cursorRoleId.execute('SELECT role_id FROM users WHERE email = "{}"'.format(signupEmail))

            session['username'] = signupUsername
            session['password'] = signupPassword
            session['email'] = signupEmail
            session['phone'] = signupTel
            session['role_id'] = cursorRoleId.fetchall()[0][0]
            session.permanent = True

            cursor.close()

            # mail_message = Message(
            #     subject= 'ایجاد حساب',
            #     recipients= [str(signupEmail)]
            # )
            # mail_message.html = f'<div dir="rtl"><p style="margin-bottom: 40px;">{signupUsername}، حساب کاربری شما در تیکی با موفقیت ایجاد شد.</p> <p>با تشکر، واحد پشتیبان تیکی</p></div>'
            # mail.send(mail_message)

            return redirect(url_for('index')), flash(message=f'{signupUsername}، حساب کاربری شما با موفقیت ایجاد شد.', category='success')

    return render_template('pages/signup.html')
@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        signinPassword = request.form.get('signinPassword')
        signinEmail = request.form.get('signinEmail')

        cursor = mySQL.connection.cursor()
        if cursor.execute('SELECT * FROM users WHERE password = "{}" AND email = "{}"'.format(signinPassword, signinEmail)):
            cursorIsActive = mySQL.connection.cursor()
            if cursorIsActive.execute('SELECT * FROM users WHERE is_active = 1 AND email = "{}"'.format(signinEmail)):
                for data in cursor.fetchall():
                    session['username'] = data[1]
                    session['phone'] = data[4]
                    session['role_id'] = data[6]

                session['password'] = signinPassword
                session['email'] = signinEmail
                session.permanent = True

                if session['role_id'] == 1:
                    return redirect(url_for('admin'))

                flash(message=f'{session["username"]}، شما با موفقیت به حساب خود وارد شدید.', category='success')

                return redirect(url_for('index'))
            else:
                flash(message='حساب شما غیرفعال یا مسدود می باشد.', category='error')
        else:
            flash(message='اطلاعات خود را بررسی و مجدد تلاش کنید.', category='error')

    return render_template('pages/signin.html')
@app.route('/signout/', methods=['GET'])
def signout():
    session.clear()
    return redirect(url_for('signin'))


@app.route('/admin/panel/', methods=['GET'])
def admin():
    if session['role_id'] == 1:
        cursor_len_tickets = mySQL.connection.cursor()
        cursor_len_tickets.execute('SELECT * FROM tickets')
        cursor_len_users = mySQL.connection.cursor()
        cursor_len_users.execute('SELECT * FROM users')

        cursor_len_tickets_open = mySQL.connection.cursor()
        cursor_len_tickets_open.execute('SELECT * FROM tickets WHERE ticket_status = "باز"')
        cursor_len_tickets_close = mySQL.connection.cursor()
        cursor_len_tickets_close.execute('SELECT * FROM tickets WHERE ticket_status = "بسته"')

        cursor_tickets_open = mySQL.connection.cursor()
        cursor_tickets_open.execute('SELECT * FROM tickets WHERE ticket_status = "باز"')
        cursor_tickets_close = mySQL.connection.cursor()
        cursor_tickets_close.execute('SELECT * FROM tickets WHERE ticket_status = "بسته"')

        return render_template('panel/panel.html', len_tickets=int(len(cursor_len_tickets.fetchall())), len_users=int(len(cursor_len_users.fetchall())), len_tickets_open=int(len(cursor_len_tickets_open.fetchall())), len_tickets_close=int(len(cursor_len_tickets_close.fetchall())), tickets_open=cursor_tickets_open.fetchall(), tickets_close=cursor_tickets_close.fetchall())
    else:
        return redirect('not_found')
@app.route('/admin/ticket/response/<int:id>/', methods=['GET', 'POST'])
def admin_ticket_response(id):
    if session['role_id'] == 1:
        if request.method == 'POST':
            ticketResponse = request.form.get('ticketResponse')
            ticketEamil = request.form.get('ticketEamil')
            ticketTitle = request.form.get('ticketTitle')
            ticketUsername = request.form.get('ticketUsername')
            ticketDateResponse = JalaliDateTime.now().strftime('%Y-%m-%d %H:%M')

            cursor = mySQL.connection.cursor()
            if cursor.execute(f'UPDATE tickets SET ticket_response = "{ticketResponse}", ticket_status = "بسته", date_response = "{ticketDateResponse}" WHERE id = "{id}"'):
                mySQL.connection.commit()
                cursor.close()

                # mail_message = Message(
                #     subject= 'پاسخ جدید برای تیکت شما',
                #     recipients= [str(ticketEamil)]
                # )
                # mail_message.html = f'<div dir="rtl"><p>سلام {ticketUsername}، برای تیکت شما با موضوع ({ticketTitle}) پاسخ جدید ثبت شده است.</p> <h4 style="margin-bottom: 40px;">{ticketResponse}</h4> <p>با تشکر، واحد پشتیبان تیکی</p></div>'
                # mail.send(mail_message)

                flash(message=f'پاسخ تیکت با شناسه {id} با موفقیت ثبت شده است.', category='success')
            else:
                flash(message=f'ثبت پاسخ با شناسه {id} با مشکل مواجه شده است.', category='error')
        return redirect(url_for('admin'))
    else:
        return redirect('not_found')
@app.route('/admin/tickets/', methods=['GET'])
def admin_tickets():
    if session['role_id'] == 1:
        cursor_tickets = mySQL.connection.cursor()
        cursor_tickets.execute('SELECT * FROM tickets')

        return render_template('panel/panel_tickets.html', tickets=cursor_tickets.fetchall())
    else:
        return redirect('not_found')
@app.route('/admin/tickets/remove/<int:id>/', methods=['GET', 'POST'])
def admin_tickets_remove(id):
    if session['role_id'] == 1:
        if request.method == 'POST':
            cursor = mySQL.connection.cursor()
            if cursor.execute('DELETE FROM tickets WHERE id = "{}"'.format(id)):
                mySQL.connection.commit()
                cursor.close()

                flash(message=f'تیکت با شناسه {id} با موفقیت حذف شد.', category='success')
            else:
                flash(message=f'حذف تیکت با شناسه {id} با مشکل مواجه شد.', category='error')

        return redirect(url_for('admin_tickets'))
    else:
        return redirect('not_found')
@app.route('/admin/users/', methods=['GET'])
def admin_users():
    if session['role_id'] == 1:
        cursor_users = mySQL.connection.cursor()
        cursor_users.execute('SELECT * FROM users')

        return render_template('panel/panel_users.html', users=cursor_users.fetchall())
    else:
        return redirect('not_found')
@app.route('/admin/users/remove/<int:id>/', methods=['GET', 'POST'])
def admin_users_remove(id):
    if session['role_id'] == 1:
        if request.method == 'POST':
            cursor = mySQL.connection.cursor()
            if cursor.execute('DELETE FROM users WHERE id = "{}"'.format(id)):
                mySQL.connection.commit()
                cursor.close()

                flash(message=f'کاربر با شناسه {id} با موفقیت حذف شد.', category='success')
            else:
                flash(message=f'حذف کاربر با شناسه {id} با مشکل مواجه شد.', category='error')

        return redirect(url_for('admin_users'))
    else:
        return redirect('not_found')
@app.route('/admin/users/disable/<int:id>/', methods=['GET', 'POST'])
def admin_users_disable(id):
    if session['role_id'] == 1:
        if request.method == 'POST':
            cursor = mySQL.connection.cursor()
            if cursor.execute('UPDATE users SET is_active = "0" WHERE id = "{}"'.format(id)):
                mySQL.connection.commit()
                cursor.close()

                flash(message=f'کاربر با شناسه {id} با موفقیت غیرفعال شد.', category='success')
            else:
                flash(message=f'غیرفعال سازی کاربر با شناسه {id} با مشکل مواجه شد.', category='error')

        return redirect(url_for('admin_users'))
    else:
        return redirect('not_found')
@app.route('/admin/users/enable/<int:id>/', methods=['GET', 'POST'])
def admin_users_enable(id):
    if session['role_id'] == 1:
        if request.method == 'POST':
            cursor = mySQL.connection.cursor()
            if cursor.execute('UPDATE users SET is_active = "1" WHERE id = "{}"'.format(id)):
                mySQL.connection.commit()
                cursor.close()

                flash(message=f'کاربر با شناسه {id} با موفقیت فعال شد.', category='success')
            else:
                flash(message=f'فعال سازی کاربر با شناسه {id} با مشکل مواجه شد.', category='error')

        return redirect(url_for('admin_users'))
    else:
        return redirect('not_found')


@app.route('/ticket/send/', methods=['GET', 'POST'])
def ticket_send():
    if session:
        if request.method == 'POST':
            ticketTitle = request.form.get('ticketTitle')
            ticketQuery = request.form.get('ticketQuery')
            ticketDateCreated = JalaliDateTime.now().strftime('%Y-%m-%d %H:%M')

            cursor = mySQL.connection.cursor()
            if cursor.execute('INSERT INTO tickets (ticket_title, ticket_query, ticket_username, ticket_email, ticket_phone, date_created) VALUES (%s,%s,%s,%s,%s,%s)', (ticketTitle, ticketQuery, session['username'], session['email'], session['phone'], ticketDateCreated,)):
                mySQL.connection.commit()

                # mail_message = Message(
                #     subject= 'تیکت شما ایجاد شد',
                #     recipients= [session['email']]
                # )
                # mail_message.html = f'<div dir="rtl"><p style="margin-bottom: 40px;">سلام {session["username"]}، تیکت شما با موضوع ({ticketTitle}) با موفقیت ثبت گردید و به زودی توسط همکاران ما پاسخ داده خواهد شد.</p> <p>با تشکر، واحد پشتیبان تیکی</p></div>'
                # mail.send(mail_message)

                # cursor_admin_email = mySQL.connection.cursor()
                # cursor_admin_email.execute('SELECT email FROM users WHERE role_id = 1')

                # mail_message_admin = Message(
                #     subject= 'تیکت جدیدی ثبت شد',
                #     recipients= [str(cursor_admin_email.fetchall()[0][0])]
                # )
                # mail_message_admin.html = f'<div dir="rtl"><p style="margin-bottom: 40px;">سلام مدیر، تیکت جدیدی با موضوع {ticketTitle} در سایت ثبت شد، لطفا وارد پنل شوید و تیکت را بررسی کنید.</p> <p>با تشکر، واحد پشتیبان تیکی</p></div>'
                # mail.send(mail_message_admin)

                cursor.close()

                flash(message='تیکت شما با موفقیت ثبت گردید و به زودی توسط همکاران ما پاسخ داده خواهد شد.', category='success')
            else:
                flash(message='ثبت تیکت شما با مشکل مواجه شد، مجدد تلاش کنید.', category='error')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('signin'))
@app.route('/ticket/search/', methods=['GET', 'POST'])
def ticket_search():
    Q = ''
    ticketSearch = ''

    if request.method == 'POST':
        ticketSearch = request.form.get('ticketSearch')
        
        if ticketSearch == '' or ticketSearch == ' ':
            ticketSearch = ''
            Q = ''
        else:
            cursor = mySQL.connection.cursor()
            if cursor.execute('SELECT * FROM tickets WHERE ticket_title LIKE "%{}%"'.format(ticketSearch)):
                Q = cursor.fetchall()
            else:
                Q = ['NOT_FOUND']

    return render_template('pages/search.html', searchQuery=Q, ticketSearch=ticketSearch)


if __name__ == '__main__':
    app.run(debug=True)

import mysql.connector

from config import config

def is_format(number):
    if 'e' not in  str(number):
        return float(number)
    else:
        return float(f"{number:.8f}")

def get_username_password(CID): # دریافت نام کاربری و کلمه عبور کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select username,password from user where cid=%s"
    cursor.execute(SQL_Quary, (CID,))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0]

def get_wallet(cid,currency): # دریافت ادرس و موجودی ولت
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select amount,id from wallet where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary, (cid,currency))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return float(result[0][0])

def get_transactions(cid): # دریافت تاریخچه خرید و فروش کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "select * from transactions where user_id=%s"
    cursor.execute(SQL_Quary,(cid,))
    res = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    if len(res)>25:
        return res[-25:]
    else:
        return res
    
def get_address_currency(cid,currency):# دریافت ادرس ولت کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select ID from wallet where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary, (cid,currency))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0][0]

def get_cid(wallet_id,currency): # بدست اوردن cid کاربر از طریق ادرس ولت
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select user_id from wallet where ID=%s and currency=%s"
    cursor.execute(SQL_Quary, (wallet_id,currency))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0][0]

def get_wallet_id(cid,currency): # دریافت ادرس ولت کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select ID from wallet where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary, (cid,currency))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0][0]

def get_account_movements(cid): # تاریخچه انتقال های کاربر را نمایش می دهد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "select * from account_movements where paying_user=%s"
    cursor.execute(SQL_Quary, (cid,))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    if len(result)>40:
        return result[-40:]
    else:
        return result
    
def get_account_movements_admin(): # دریافت تاریخچه تمام انتقال ها برای ادمین
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "select datetime,Amount,currency,paying_user,receiving_user from account_movements"
    cursor.execute(SQL_Quary,)
    res = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    if len(res)>40:
        return res[-40:]
    else:
        return res
    
def get_amount_commission(): # دریافت مقدار کارمزد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select amount_commission from fee where `id`=1"
    cursor.execute(SQL_Quary,)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return float(result[0][0])

def get_favorites(user_id): # دریافت علاقه مندی های کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "SELECT CURRENCY FROM  FAVORITES WHERE USER_ID=%s"
    cursor.execute(SQL_Quary,(user_id,))
    result = cursor.fetchall()
    favorites=[]
    for i in range(len(result)):
        favorites.append(result[i]['CURRENCY'])
    return favorites

def get_users_data(): # دریافت cid تمام کاربران
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT CID FROM USER"
    cursor.execute(SQL_Quary)
    result = [i[0] for i in cursor.fetchall()]
    return result

def get_user_data(USER_ID):# دریافت اطلاعات کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Query = "SELECT * FROM USER WHERE CID=%s"
    cursor.execute(SQL_Query,(USER_ID,))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0]

def get_wallet_data():   # دریافت تمام cid و ارز های ولت
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT user_id,currency FROM WALLET"
    cursor.execute(SQL_Quary)
    result = cursor.fetchall()
    return result
 
def get_wallet_data_address(currency): # دریافت تمام ادرس های ولت یک ارز
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT id FROM WALLET WHERE CURRENCY=%s"
    cursor.execute(SQL_Quary,(currency,))
    result = [i[0] for i in cursor.fetchall()]
    return result

def get_wallet_user(USER_ID): # دریافت تمام موجودی های ولت کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "SELECT * FROM WALLET WHERE USER_ID= %s AND AMOUNT>0"
    cursor.execute(SQL_Quary,(USER_ID,))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

def get_currency_data(): # دریافت لیست تمامی ارز ها
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT CODE FROM CURRENCY"
    cursor.execute(SQL_Quary)
    result = cursor.fetchall()
    currency=[i[0] for i in result]
    return currency

def get_wallet_crrency(cid):# دریافت ارز های داخل کیف پول بیشتر که موجوی انها از صفر بیشتر است و دلار و تومان نیستند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT CURRENCY FROM WALLET where user_id=%s and amount>0 and currency!='TMN' and currency!='USDTTMN'"
    cursor.execute(SQL_Quary,(cid,))
    result = cursor.fetchall()
    currency=[i[0] for i in result if i!='TMN']
    return currency

def get_wallet_address():# دریافت ادرس و ارز از ولت
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT id,currency FROM WALLET"
    cursor.execute(SQL_Quary)
    result = cursor.fetchall()
    return result

def get_all_user():# دریافت cid,username تمام کاربران
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "SELECT CID,username FROM USER"
    cursor.execute(SQL_Quary)
    result = cursor.fetchall()
    user_list=[]
    for i in result:
        user_list.append(i)
    return user_list

def get_all_user_cid():# دیافت cid تمام کاربران
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT CID FROM USER"
    cursor.execute(SQL_Quary)
    result = cursor.fetchall()
    user_list=[]
    for i in result[1:]:
        user_list.append(i[0])
    return user_list

def get_warning(CID): # دریافت تعداد خطا ها
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT WARNING FROM USER WHERE CID = %s"
    cursor.execute(SQL_Quary, (CID,))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0][0]

def get_spams():# دریافت افراد اسپم
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT * FROM SPAMS"
    cursor.execute(SQL_Quary)
    result = cursor.fetchall()
    spams=[]
    for cid in result:
        spams.append(cid[0])
    return result

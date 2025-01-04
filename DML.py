import mysql.connector

from config import config

def get_favorites(user_id): # ارز های مورد علاقه کاربر را بر میگرداند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT CURRENCY FROM  FAVORITES WHERE USER_ID=%s"
    cursor.execute(SQL_Quary,(user_id,))
    result = cursor.fetchall()
    favorites = [currency[0] for currency in result]
    return favorites

def get_wallet(cid,currency): # ادرس و نوع ولت را برمیگرداند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select amount,id from wallet where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary, (cid,currency))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return float(result[0][0])

def get_amount_commission(): # مقدار کارمزد را بر می گرداند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "select amount_commission from fee where `id`=1"
    cursor.execute(SQL_Quary,)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return float(result[0][0])

def get_warning(CID): # تعداد دفعاتی که کاربر پیام نا مربوط ارسال کرده است
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "SELECT WARNING FROM USER WHERE CID = %s"
    cursor.execute(SQL_Quary, (CID,))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result[0][0]

def insert_user_data(CID,USERNAME,Fname_Lname=None,PASSWORD=None,PHONE=None): # کاربر اولین بار که از ربات استفاده می کند cid,username ان را وارد دیتابیس می کند 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """INSERT INTO USER (CID,USERNAME,Fname_Lname,PASSWORD,PHONE)
    VALUES (%s,%s, %s, %s, %s)"""
    cursor.execute(SQL_Quary, (CID,USERNAME,Fname_Lname,PASSWORD,PHONE))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

def update_user_data(CID,Fname_Lname,PASSWORD,PHONE,Authentication):  # کاربر در دیتابیس ثبت می شود
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """UPDATE USER SET Fname_Lname=%s,PASSWORD=%s,PHONE=%s,Authentication=%s WHERE CID=%s"""
    cursor.execute(SQL_Quary, (Fname_Lname,PASSWORD,PHONE,Authentication,CID))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

def insert_favorite(USER_ID,CURRENCY): # ارز را به علاقه مندی ها اضافه می کند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_quary = """ INSERT INTO FAVORITES (USER_ID,CURRENCY) VALUES (%s,%s)"""
    cursor.execute(SQL_quary,(USER_ID,CURRENCY.upper()))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid 

def delete_favorite(USER_ID,CURRENCY): # ارز را از علاقه مندی ها حذف می کند
    currency=get_favorites(USER_ID)
    if CURRENCY in currency:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        SQL_quary = """ DELETE FROM FAVORITES WHERE USER_ID=(%s) AND CURRENCY=(%s)"""
        cursor.execute(SQL_quary,(USER_ID,CURRENCY.upper()))
        conn.commit()
        cursor.close()
        conn.close()
        return cursor.lastrowid 
    else: 
        return False

def insert_wallet_data(USER_ID,CURRENCY,AMOUNT): # ولت ایجاد می کند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """INSERT INTO WALLET (USER_ID,CURRENCY,AMOUNT)
    VALUES (%s,%s, %s)"""
    cursor.execute(SQL_Quary, (USER_ID,CURRENCY,AMOUNT))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

def insert_currency(CODE): # به جدول ارز ها ارز جدید اضافه می کند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """INSERT INTO CURRENCY (CODE)
    VALUES (%s)"""
    cursor.execute(SQL_Quary, (CODE,))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

def buying_currency1(cid,amount_p,base):  # مبلغ پرداخت شده کاربر را به ولت تومان صرافی انتقال می دهد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    amount_p_tmn=get_wallet(cid,base)-amount_p
    amount_d_tmn=get_wallet(1385200618,base)+amount_p
    SQL_Quary =" update wallet set amount=%s where user_id=%s and currency=%s;"
    cursor.execute(SQL_Quary, (amount_p_tmn,cid,base))
    SQL_Quary="update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary,(amount_d_tmn,base))
    conn.commit()
    cursor.close()
    conn.close()

def buying_currency2(amount_p,amount_d,currency,base): # مبلغ در صرافی را از تومان به ارز مورد نظر تبدیل می کند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    fee = float(get_amount_commission())
    fee_=fee*amount_p
    amount_p_tmn1=get_wallet(1385200618,base)-(amount_p-fee_)
    SQL_Quary = "update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary, (amount_p_tmn1,base))
    fee_=fee*amount_d
    amount_d_currency=get_wallet(1385200618,currency)+(amount_d-fee_)
    SQL_Quary = "update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary,(amount_d_currency,currency))
    conn.commit()
    cursor.close()
    conn.close()

def buying_currency3(cid,amount_d,currency): # ارز تبدیل شده را از ولت صرافی به ولت کاربر انتقال می دهد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    fee = float(get_amount_commission())
    fee_=fee*amount_d
    amount_d-=fee_
    exchange_wallet=get_wallet(1385200618,currency)-amount_d
    user_wallet=get_wallet(cid,currency)+amount_d
    SQL_Quary =" update wallet set amount=%s where user_id=1385200618 and currency=%s;"
    cursor.execute(SQL_Quary, (exchange_wallet,currency))
    SQL_Quary="update wallet set amount=%s where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary,(user_wallet,cid,currency))
    conn.commit()
    cursor.close()
    conn.close()

def sell_currency1(cid,amount_d,currency): # ارز مورد نظر را به ولت صرافی انتقال می دهد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    exchange_wallet=get_wallet(1385200618,currency)+amount_d
    user_wallet=get_wallet(cid,currency)-amount_d
    SQL_Quary =" update wallet set amount=%s where user_id=1385200618 and currency=%s;"
    cursor.execute(SQL_Quary, (exchange_wallet,currency))
    SQL_Quary="update wallet set amount=%s where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary,(user_wallet,cid,currency))
    conn.commit()
    cursor.close()
    conn.close()

def sell_currency2(amount_d,amount_p,currency,base): # ارز منتقل شده به ولت صرافی را به تومان تبدیل می کند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    amount_p_tmn1=get_wallet(1385200618,base)+amount_d
    SQL_Quary = "update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary, (amount_p_tmn1,base))
    amount_d_currency=get_wallet(1385200618,currency)-amount_p
    SQL_Quary = "update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary,(amount_d_currency,currency))
    conn.commit()
    cursor.close()
    conn.close()

def sell_currency3(cid,amount_p,base): # تومان را از ولت صرافی به ولت کاربر انتقال می دهد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    fee = float(get_amount_commission())
    fee_=fee*amount_p
    amount_p_tmn=get_wallet(cid,base)+(amount_p-fee_)
    amount_d_tmn=get_wallet(1385200618,base)-(amount_p-fee_)
    SQL_Quary =" update wallet set amount=%s where user_id=%s and currency=%s;"
    cursor.execute(SQL_Quary, (amount_p_tmn,cid,base))
    SQL_Quary="update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary,(amount_d_tmn,base))
    conn.commit()
    cursor.close()
    conn.close()

def insert_transactions(user_id,currency,amount,deal,amount_rate): # ثبت تراکنش های خرید و فروش
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "insert into transactions (user_id,currency,amount,deal,amount_rate) values (%s,%s,%s,%s,%s);"
    cursor.execute(SQL_Quary,(user_id,currency,amount,deal,amount_rate))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def update_wallet_tmn(cid,amount):  # اقزایش موجودی ولت تومان کاربر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    amount=int(amount)
    fee = float(get_amount_commission())*amount
    amount-=fee
    exchange_wallet=get_wallet(1385200618,'TMN')-amount
    SQL_Quary = " update wallet set amount=%s where user_id=1385200618 and currency='TMN'"
    cursor.execute(SQL_Quary,(exchange_wallet,))   
    amount_p_tmn=get_wallet(cid,'TMN')+amount
    SQL_Quary = " update wallet set amount=%s where user_id=%s and currency='TMN'"
    cursor.execute(SQL_Quary,(amount_p_tmn,cid))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def update_wallet(cid,amount,currency): # افزایش موحودی ولت ارز
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    amount_p_tmn=get_wallet(cid,currency)+int(amount)
    SQL_Quary = " update wallet set amount=%s where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary,(amount_p_tmn,cid,currency))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def withdrawal_from_account(cid,amount,fee): # برداشت تومان از ولت
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    fee_= fee + get_wallet(1385200618,'TMN')
    SQL_Quary = " update wallet set amount=%s where user_id=%s and currency='TMN'"
    cursor.execute(SQL_Quary,(fee_,1385200618))
    amount_p_tmn = get_wallet(cid,'TMN')-amount
    SQL_Quary = " update wallet set amount=%s where user_id=%s and currency='TMN'"
    cursor.execute(SQL_Quary,(amount_p_tmn,cid))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def withdrawal_from_wallet(cid,amount,currency,m_cid): # انتقال ارز از یک ولت به ولت هم نوع دیگر
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    fee = float(get_amount_commission())
    fee_=fee*amount
    amount_wallet=get_wallet(cid,currency)-float(amount)
    SQL_Quary = " update wallet set amount=%s where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary,(amount_wallet,cid,currency))
    amount-=fee_
    amount_m_wallet=get_wallet(m_cid,currency)+float(amount)
    SQL_Quary = " update wallet set amount=%s where user_id=%s and currency=%s"
    cursor.execute(SQL_Quary,(amount_m_wallet,m_cid,currency))
    SQL_Quary = " update wallet set amount=%s where user_id=1385200618 and currency=%s"
    cursor.execute(SQL_Quary,(fee_,currency))
    conn.commit()
    cursor.close()
    conn.close()
    return True
     
def insert_account_movements(paying_user,amount,currency,origin_id,receiving_user,destination_id,transmission_type): # ثبت انتقال ها
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    SQL_Quary = "insert into account_movements (paying_user,amount,currency,origin_id,receiving_user,destination_id,transmission_type) values (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(SQL_Quary,(paying_user,amount,currency,origin_id,receiving_user,destination_id,transmission_type))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def update_change_fee(amount): # تغییر درصد کارمزد
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = "update fee set amount_commission=%s where id=1"
    cursor.execute(SQL_Quary, (str(amount),))
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

def add_spams(CID,permanent='True'): # افزودن کاربر به اسپم ها
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """INSERT INTO SPAMS (CID,permanent) VALUES (%s,%s)"""
    cursor.execute(SQL_Quary, (CID,permanent))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def remove_spams(CID):  # حذف کاربر  از اسپم ها
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = """DELETE FROM SPAMS WHERE CID = %s;"""
    cursor.execute(SQL_Quary, (CID,))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def update_warning(cid): # افزودن به تعداد دفعاتی که کاربر پیام نا مربوط ارسال کرده است
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    number_warnings = get_warning(cid)+1
    SQL_Quary = " update user set warning =%s where cid = %s"
    cursor.execute(SQL_Quary,(number_warnings,cid))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def update_warning_to_zero(cid): # تعداد خطا ها را صفر می کند
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Quary = " update user set warning = 0 where cid = %s"
    cursor.execute(SQL_Quary,(cid,))
    conn.commit()
    cursor.close()
    conn.close()
    return True
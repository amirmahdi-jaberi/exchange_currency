import requests  
import telebot
import datetime
import time
import threading 
import logging
 
from telebot.types import ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove

from config import mytoken,admin,bank_card_photo,bank_card
from persian_text import help_text

from DQL import get_username_password,get_wallet,get_cid,get_account_movements,get_all_user_cid,get_all_user,get_wallet_crrency
from DQL import get_transactions,get_address_currency,get_wallet_data,get_favorites,get_currency_data,get_wallet_data_address,get_users_data
from DQL import get_user_data,get_wallet_user,get_amount_commission,get_wallet_id,get_spams,get_warning,get_account_movements_admin

from DML import buying_currency1,withdrawal_from_wallet,buying_currency3,update_wallet,remove_spams,withdrawal_from_account,update_change_fee
from DML import sell_currency1,sell_currency2,sell_currency3,insert_transactions,insert_favorite,delete_favorite,update_wallet_tmn,insert_account_movements
from DML import insert_user_data,insert_wallet_data,update_user_data,buying_currency2,add_spams,update_warning,update_warning_to_zero

API_TOKEN = mytoken 

bot = telebot.TeleBot(API_TOKEN)

Users=dict() # برای ذخیره اطلاعات کاربر حین ثبت نام

user_step={}

admin_cid = admin # import config

user_step[admin_cid]=''

user_dataa={}

transaction_information={}

logging.basicConfig(filename='main.log',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%b-%d %A %H:%M:%S' ,level=logging.INFO)

def check_spams():          #تابعی برای اینکه چک کند کاربرانی به طور موقت اسپم شدند پس از یک ساعت از لیست اسپم ها خارج شوند
    spam = get_spams()
    spams=[(id[0],id[2]) for id in spam if id[1]=='False' ]
    for i in spams:
        h_1=datetime.timedelta(minutes=60)
        cid_=i[0]
        now=datetime.datetime.today()
        spam_time=i[1]+h_1
        if now>=spam_time:
            remove_spams(cid_)
            logging.info(f'User {cid_} was automatically removed from the spam list')
            update_warning_to_zero(cid_)

def is_plus(text):          #برای چک کردن اینکه ارز مورد نظر رشد کرده یا ضرر کرده است
    if text>=0:
        return f'+{text}%🔼'
    else:
        return f'{text}%🔽'

def is_plus2(text):         #برای چک کردن اینکه ارز مورد نظر رشد کرده یا ضرر کرده است
    if text>=0:
        return f'🟢+{str(text)}%'
    else:
        return f'🔴{str(text)}%'

def get_change(currency):    # درصد تغییر ارز طی روز گذشته را برمیگرداند 
    response = requests.get('https://api.wallex.ir/v1/markets') 
    if response.status_code == 200: 
        ch_24h = response.json()['result']['symbols'][currency]['stats']["24h_ch"]
        return ch_24h
    else:
        return False

def is_str(text):           #متن وارد شده فقط حاوی حروف باشد
    text1=text.replace(' ','')
    if text1.isalpha():
        return True 
    else:
        return False

def get_price(text,response):        #قیمت ارزی که به ان بدهیم را برمیگرداند
    if text.upper()=='TMN':
        return 1
    elif response.status_code == 200:
        price = response.json()['result']['symbols'][text.upper()]['stats']['bidPrice']
        return float(price)
    else:
        return False

def is_spam(cid,username):  #چک کردن اسپم بودن کاربر و اگر اولین بار کاربر ربات را استفاده می کند به جدول user  اضافه شود
    users=get_users_data()
    spam=get_spams()
    spams=[]
    for id in spam:
        spams.append(id[0])
    if cid not in users:
        insert_user_data(cid,username)
        insert_wallet_data(cid,'TMN',0)
        insert_wallet_data(cid,'USDTTMN',0)
    return cid in spams

def is_int(number):         #چک کردن اینکه متن وارد شده عدد است
    num=str(number).replace('.','')
    if num.isdigit():
        return True
    else:
        return False

def is_card(card_number):   # این تابع چک میکند ایا شماره کارت واقعی است یا نه * برای زمانی که کاربر قصد برداشت دارد
    list_number=[]
    num=2
    if len(str(card_number))==16:
        for i in str(card_number):
            if num==2:
                n=int(i)*2
                if n>9:
                    list_number.append(n-9)
                else:
                    list_number.append(n)
                num-=1
            else:
                list_number.append(int(i))
                num+=1
        if sum(list_number)%10==0:
            return True
        else:
            return False  
    else:
        return False

def is_format(number):      # اگر عدد به صورت علمی باشد به صورت اعشاری بر میگرداند
    if 'e' not in  str(number):
        return float(number)
    else:
        return f"{number:.8f}"

def run_bot():              # اجرا شدن تابع check_spams هر 60 ثانیه یک بار
    next_run = time.time() 
    while True:
         if time.time() >= next_run:
            check_spams() 
            next_run = time.time() + 60

@bot.callback_query_handler(func= lambda call: True)
def callback_query_handler(call):
    id       = call.id
    cid      = call.message.chat.id
    mid      = call.message.message_id
    username = call.from_user.username
    data     = call.data
    if not data.startswith('افزودن به علاقه مندی ها') and not data.startswith('حذف از علاقه مندی ها'):
        user_step[cid]=None
    if is_spam(cid,username):return
    user_dataa.setdefault(cid,{})
    Users.setdefault(cid,[])
    transaction_information.setdefault(cid,{})
    print(f'call id: {id}, cid: {cid}, mid: {mid}, data: {data}')
    bot.answer_callback_query(id,f"شما <<{data}>> انتخاب کردید.")
    if data=='تاریخچه تراکنش ها':           # اگر کاربر ثبت نام کرده باشد دو گزینه خرید و فروش و انتقال به ان نشان میدهد
        user_data=get_user_data(cid)
        if user_data['Authentication']=='False':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('ایجاد حساب کاربری 👤', callback_data='ایجاد حساب کاربری'),InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('👤 ابتدا لطفاً حساب کاربری خود را ایجاد کنید.',cid,mid,reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('خرید و فروش 💎', callback_data='تاریخچه خرید و فروش ها'),InlineKeyboardButton('انتقال ها 🔃', callback_data='تاریخچه واریز و برداشت ها'))
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('انتخاب کنید 🔸',cid,mid,reply_markup=markup)
    elif data=='admin_panel':                # منوی دسترسی های ادمین
        if cid==admin_cid:
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('تاریخچه انتقال ها 📜', callback_data='transfer_history'))
            markup.add(InlineKeyboardButton('کیف پول صرافی 💰', callback_data='exchange_wallet_balance'))
            markup.add(InlineKeyboardButton('تغییر درصد کارمزد 🔄', callback_data='change_commission'))
            markup.add(InlineKeyboardButton('لیست کاربران 👥', callback_data='user_list'))
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('مدیریت',cid,mid,reply_markup=markup)
    elif data=='transfer_history':           # ادمین انتخاب می کند تاریخچه انتقال های چه زمانی را ببیند
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('24 ساعت گذشته 🌙', callback_data='1_d'))
        markup.add(InlineKeyboardButton('3 روز گذشته ⏲️', callback_data='3_d'))
        markup.add(InlineKeyboardButton('7 روز گذشته 📅', callback_data='7_d'))
        markup.add(InlineKeyboardButton('برگشت', callback_data='admin_panel'))
        logging.info('Admin viewed transaction history')
        bot.edit_message_text('🔔 کاربر گرامی، لطفاً یکی از گزینه‌های زیر را انتخاب نمایید:',cid,mid,reply_markup=markup)
    elif data=='1_d':                        # نمایش انتقال های 24 ساعت  گذشته
        transaction=get_account_movements_admin()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='transfer_history'))
        today=datetime.datetime.today()
        day_1=datetime.timedelta(days=1)
        text='تاریخچه یک روز گذشته 🌓\n\n'
        for tran in transaction:
            Date=tran['datetime']
            distance=today-Date
            if distance<day_1:
                amount         = float(tran['Amount'])
                currency       = tran['currency']
                paying_user    = tran['paying_user']
                receiving_user = tran['receiving_user']
                text+=f"🔄انتقال {amount:.8f} عدد ارز {currency} از {paying_user} به {receiving_user} در تاریخ {Date} \n\n"
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='3_d':                        # نمایش انتقال های 72 ساعت  گذشته
        transaction=get_account_movements_admin()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='transfer_history'))
        today=datetime.datetime.today()
        day_3=datetime.timedelta(days=3)
        text='تاریخچه سه روز گذشته ⏲️\n\n'
        for tran in transaction:
            Date=tran['datetime']
            distance=today-Date
            if distance<day_3:
                amount         = float(tran['Amount'])
                currency       = tran['currency']
                paying_user    = tran['paying_user']
                receiving_user = tran['receiving_user']
                text+=f"🔄انتقال {amount:.8f} عدد ارز {currency} از {paying_user} به {receiving_user} در تاریخ {Date} \n\n"
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='7_d':                        # نمایش انتقال های  هفته  گذشته
        transaction=get_account_movements_admin()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='transfer_history'))
        today=datetime.datetime.today()
        day_7=datetime.timedelta(days=7)
        text='تاریخچه هفته  گذشته 📅\n\n'
        for tran in transaction:
            Date=tran['datetime']
            distance=today-Date
            if distance<day_7:
                amount         = float(tran['Amount'])
                currency       = tran['currency']
                paying_user    = tran['paying_user']
                receiving_user = tran['receiving_user']
                text+=f"🔄انتقال {amount:.8f} عدد ارز {currency} از {paying_user} به {receiving_user} در تاریخ {Date} \n\n"
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='exchange_wallet_balance':    # نمایش کیف پول صرافی 
        res = get_wallet_user(1385200618)    # cid  صرافی می باشد
        text = str()
        wallet_balance=int()
        response = requests.get('https://api.wallex.ir/v1/markets')
        usdt = get_price('USDTTMN',response)
        for i in res:
            currency = i["currency"]
            price    = get_price(currency,response)
            amount   = float(i["amount"])
            inventory= amount * price
            if currency[-4:]=='USDT':
                wallet_balance += inventory * usdt
            else:
                wallet_balance += inventory
            text+=f'''🚩 ادرس : {i["ID"]}\n📀 ارز : {currency}\n🔢 مقدار : {is_format(amount)}\n💲 قیمت : {is_format(price)}\n💳 موجودی : {inventory:.2f}\n{70*'-'}\n'''        
        text+=f'💰موجودی به تومان : {int(wallet_balance)}\n💰موجودی به دلار : {round(wallet_balance/usdt,2)}'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='admin_panel'))
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
        logging.info('Admin viewed the exchange wallet section')
    elif data=='change_commission':          # برای تغییر کارمزد است و از کاربر میخواهد مقدار جدید را وارد کند
        markup = InlineKeyboardMarkup()         
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='admin_panel'))
        fee = get_amount_commission()
        bot.edit_message_text(f"""🔔 کاربر گرامی،\n\nکارمزد حال حاضر : {fee*100}%\n
💡 لطفاً مقدار مورد نظر خود را به صورت عدد اعشاری وارد نمایید، مانند 0.4 یا 10.0 یا 2.4.\n\nسپاسگزاریم 🙏""",cid,mid,reply_markup=markup)
        user_step[cid]='amount_commission'
    elif data=='amount_commission':          # کاربر تایید می کند که درصد کارمزد تغییر کند
        amount=user_dataa[cid]['amount_commission']
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)
        update_change_fee(amount) # تغییر درصد کارمزد
        fee = get_amount_commission()
        logging.info(f'Admin changed the fee to {fee*100}%')
        bot.send_message(cid,f'''🔔 کاربر گرامی،\n\n💡 درصد کارمزد شما به {fee*100}% تغییر کرد.''')
    elif data=='user_list':                  # نشان دادن cid و username کاربران ربات و چند گزینه مر بوط به کاربران
        users=get_all_user()
        text = f'CHAT ID{" "*10}:  USERNAME\n'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('ارسال پیام به کاربر 💬', callback_data='send_message_to_user'))
        markup.add(InlineKeyboardButton('ارسال پیام همگانی 📢', callback_data='send_message_ALLusers'))
        markup.add(InlineKeyboardButton('کاربران مسدود 🚫',callback_data='spam_user'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='admin_panel'))
        for user in users:
            text += f"{user['CID']}  :  @{user['username'] }\n"
            bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='send_message_to_user':       # از ادمین درخواست CID میکند برای ارسال پیام به کاربر
        bot.edit_message_text('''🔔 کاربر گرامی،\n\nلطفاً CID کاربر مورد نظر را وارد کنید.\n\nسپاسگزاریم 🙏''',cid,mid)
        user_step[cid]='send_message_to_user'
    elif data=='send_message_ALLusers':      # از ادمین درخواست پیام میکند برای ارسال به همه ی کاربران
        bot.edit_message_text('''🔔 کاربر گرامی،\n\nلطفاً پیام خود را وارد کنید.\n\nسپاسگزاریم 🙏''',cid,mid)
        user_step[cid]='send_message_ALLusers'
    elif data=='confirm_sending_message':    # تایید می شود که پیام به تمامی کاربران ارسال شود
        users =  get_all_user_cid()
        text=user_dataa[cid]['message_all_user']
        for i in users:
            bot.send_message(i,f'📢 این پیام از طرف ادمین ربات می‌باشد:\n\n💬 {text}')
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)
        logging.info("Admin sent a message to all users")
        bot.send_message(cid,'پیام شما با موفقیت به تمامی کاربران ارسال شد.🙏')
    elif data=='spam_user':                  # لیست کاربران اسپم را نشان میدهد به همرام دو گزینه حذف یا اضافه کردن به اسپم ها
        spam=get_spams()
        spams=[]
        for id in spam:
            spams.append(id[0])
        text='لیست کاربران مسدود نمایش داده شد, برای کپی کردن شناسه عددی، لطفاً بر روی آن ضربه بزنید 🙏\n\n'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('حذف کاربر ❌', callback_data='remove_user_spam'),InlineKeyboardButton('افزودن کاربر ➕', callback_data='add_user_spam'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='admin_panel'))
        for user in spams:
            text+=f'🔹`{user}`\n'
        bot.edit_message_text(text,cid,mid,reply_markup=markup,parse_mode='MarkdownV2')
    elif data=='add_user_spam':              # از ادمین درخواست cid می کند و ان را به لیست spam ها اضافه می کند                   
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='admin_panel'))
        bot.edit_message_text('''🔐 لطفاً شناسه عددی کاربر (CID) را وارد کنید.''',cid,mid,reply_markup=markup)
        user_step[cid]='add_user_spams'
    elif data=='remove_user_spam':           # از ادمین درخواست cid می کند تا کاربر را از لیست اسپم  ها حذف کند
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='admin_panel'))
        bot.edit_message_text('🔐 لطفاً شناسه عددی کاربر (CID) را وارد کنید.',cid,mid,reply_markup=markup)
        user_step[cid]='remove_user_spams'
    elif data=='support':                    # از کاربر درخواست پیام  میکند و پیام را به پشتیبانی ارسال می کند
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        bot.edit_message_text('📲 لطفاً پیام مورد نظر را در قالب یک پیامک ارسال کنید.',cid,mid,reply_markup=markup)
        user_step[cid]='support_message'    
    elif data=='تاریخچه خرید و فروش ها':    # تاریخچه 25 تراکنش اخر کاربر را نشان  میدهد
        res = get_transactions(cid)
        text="📚 تاریخچه 25 تراکنش آخر\n"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='تاریخچه تراکنش ها'))
        for tran in res:
            amount   = float(tran['amount'])
            currency = tran["currency"]
            deal     = tran['deal']
            rate     = tran['amount_rate']
            date     = tran['date']
            text+=f"""
#️⃣ شماره تراکنش : {tran['ID']}
💳 نام ارز : {currency}
📍 مقدار : {amount:.8f}
🔄 نوع تراکنش : {deal}
💲 به قیمت واحد : {rate}
📆 تاریخ : {date}\n"""
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='خرید & فروش':               # اگر کاربر حساب کاربری ایجاد کرده باشد دو گزینه خرید و قروش نمایش می دهد
        user_data=get_user_data(cid)
        if user_data['Authentication']=='False':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('ایجاد حساب کاربری 👤', callback_data='ایجاد حساب کاربری'),InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('👤 ابتدا لطفاً حساب کاربری خود را ایجاد کنید.',cid,mid,reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('خرید 🛒', callback_data='خرید'),InlineKeyboardButton('فروش 🏷️', callback_data='فروش'))
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('💳 لطفاً نوع تراکنش خود را انتخاب کنید:',cid,mid,reply_markup=markup)
    elif data=='خرید':                       # از کاربر اسم ارز دیجیتال را درخواست می کند
        bot.edit_message_text('''🔐 لطفاً نام ارز مورد نظر را به انگلیسی و به صورت کامل وارد نمایید، مانند "BTCTMN" یا "BTCUSDT".\n
💡 برای راهنمایی بیشتر، می‌توانید به لیست قیمت ارزها مراجعه کنید.''',cid,mid,reply_markup=None)
        user_step[cid]='buying'
    elif data=='فروش':                       # در صورتی که کاربر ارزی داخل کیف پول خود داشته باشد ان را به صورت دکمه شیشه ای نمایش می دهد
        markup = InlineKeyboardMarkup()
        currencies=get_wallet_crrency(cid) # ارز های موجود در کیف پول کاربر را نمایش می دهد
        if len(currencies)==0:
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='خرید & فروش'))
            markup.add(InlineKeyboardButton('افزایش موجودی 💵', callback_data='واریز')) 
            bot.edit_message_text('🔔 موجودی کیف پول شما ناکافی می‌باشد.',cid,mid,reply_markup=markup)  
        else:
            for currency in currencies:
                markup.add(InlineKeyboardButton(currency,callback_data=f'فروش/{currency}'))
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='خرید & فروش'))
            bot.edit_message_text('🔁 لطفاً ارز مورد نظر خود را انتخاب کنید:',cid,mid,reply_markup=markup)   
    elif data=='واریز & برداشت':            # اگر کاربر حساب کاربری داشته باشد دو گزینه واریز و برداشت ار نشان  میدهد
        user_data=(get_user_data(cid))
        if user_data['Authentication']=='False':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('ایجاد حساب کاربری 👤', callback_data='ایجاد حساب کاربری'),InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('👤 ابتدا لطفاً حساب کاربری خود را ایجاد کنید.',cid,mid,reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('واریز 📥', callback_data='واریز'),InlineKeyboardButton('برداشت  📤', callback_data=f'برداشت'))
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('💳 لطفاً نوع تراکنش خود را انتخاب کنید:',cid,mid, reply_markup=markup)
    elif data=='تاریخچه واریز و برداشت ها':# تاریخچه 40 انتقال اخیر کاربر را نمایش می دهد
        transaction=get_account_movements(cid)
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='تاریخچه تراکنش ها'))
        text='تاریخچه 40 انتقال اخیر 📌'
        for tran in transaction:
            amount   = is_format(tran['Amount'])
            date     = tran['datetime']
            currency = tran['currency']
            if tran['transmission_type']=='Deposit':
                type_     = 'واریز  📥'
                wallet_id = tran['origin_id']
                od        = 'مبدا'
            else:
                type_     = 'برداشت  📤'
                wallet_id = tran['destination_id']
                od        = 'مقصد'  
            text+=f"\n\n🔄{type_} ارز {currency} به مقدار {amount:.8f} آدرس {od} {wallet_id} در تاریخ {date}"
        bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='کیف پول':                    # نمایش کیف پول
        bot.edit_message_text('در حال بررسی . . . 🗨',cid,mid)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        markup.add(InlineKeyboardButton('افزایش موجودی 💵', callback_data='واریز')) 
        user_data = get_user_data(cid)
        if user_data['Authentication']=='False': # اگر حساب کاربری نداشته باشد
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('ایجاد حساب کاربری 👤', callback_data='ایجاد حساب کاربری'),InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('👤 ابتدا لطفاً حساب کاربری خود را ایجاد کنید.',cid,mid,reply_markup=markup)
        else:
            # دریافت تمامی اطلاعات کیف پول به صورت لیست
            wallet_currencies = get_wallet_user(cid) 
            # اگر کیف پول خالی باشد
            if len(wallet_currencies) == 0: 
                bot.edit_message_text('👜 موجودی کیف پول شما فعلاً صفر است.',cid,mid,reply_markup=markup)
            else:
                response = requests.get('https://api.wallex.ir/v1/markets')
                usdt     = get_price('USDTTMN',response)
                all_ch   = []  # ذخیر درصد تغییر هر ارز در روز گذشته
                # نمایش   تومان به صورت جداگانه چون داخل  API وجود ندارد
                TMN      = wallet_currencies[0]  
                amount   = int(TMN['amount'])
                text     =f'''🚩 ادرس : {TMN["ID"]}\n📀 ارز : TMN\n🔢 مقدار : {amount}\n💲 قیمت : 1\n📉درصد تغییر (۲۴): ---\n💳 موجودی : {amount}\n{70*'-'}\n'''
                wallet_balance = amount
                data           = response.json()
                for CUR in wallet_currencies[1:]:
                    currency  = CUR["currency"]
                    total     = float(data['result']['symbols'][currency]['stats']['bidPrice'])
                    amount    = float(CUR["amount"])
                    ch_24h    = data['result']['symbols'][currency]['stats']["24h_ch"]
                    inventory = total * amount
                    address   = CUR["ID"]
                    all_ch.append(ch_24h)
                    if currency[-4:]=='USDT':  
                        # اگر ارز بر بستر دلار باشد
                        wallet_balance += inventory * usdt
                    else:
                        wallet_balance += inventory
                    text+=f'''🚩  ادرس : {address}
📀  ارز : {currency}
🔢  مقدار : {amount:.8f}
💲  قیمت : {is_format(total)}
📉 درصد تغییر (۲۴) : {is_plus(ch_24h)}
💳 موجودی : {inventory:.2f}
{70*'-'}\n'''
                if len(all_ch)  == 0: all_ch.append(0)
                yesterday_ch     = is_plus( ( sum(all_ch) / len(all_ch) ) ) # بدست اوردن درصد تغییر کل در 24 ساعت گذشته
                total_price_usdt = round( wallet_balance / usdt , 2 ) # نرخ موجودی کل به دلار
                text+=f'''
📉 درصد تغییر (۲۴)    : {yesterday_ch}\n
💴 موجودی کل به تومان : {int(wallet_balance)}\n
💵 موجودی کل به دلار   : {total_price_usdt}'''
                bot.edit_message_text(text,cid,mid,reply_markup=markup)
    elif data=='لیست قیمت رمز ارز ها':      # چند گزینه برای نمایش قیمت ارز ها نشان می دهد
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('دلار 💷', callback_data='دلار'),InlineKeyboardButton('تومان 💶', callback_data='تومان'))
        markup.add(InlineKeyboardButton('علاقه مندی ها 💖', callback_data='علاقه مندی ها'),InlineKeyboardButton('جستجو 🔍', callback_data='جستجو'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        bot.edit_message_text('💰 نمایش قیمت‌ها به چه صورت باشد؟',cid,mid,reply_markup=markup)  
    elif data=='حساب کاربری':                # اطلاعات حساب کاربری کاربر را نمایش می دهد
        user_data=(get_user_data(cid))
        if user_data['Authentication']=='False': # اگر کاربر حساب کاربری ایجاد نکرده باشد
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('ایجاد حساب کاربری', callback_data='ایجاد حساب کاربری'),InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            bot.edit_message_text('👤 ابتدا لطفاً حساب کاربری خود را ایجاد کنید.',cid,mid,reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            text=f"""🔹 اطلاعات حساب کاربری\n
👤 نام نام خانوادگی   :  {user_data['Fname_Lname']}\n
📞 شماره موبایل        :  {user_data['phone']}\n
🆔 نام کاربری            :  {user_data['username']}\n
📅 تاریخ ایجاد حساب :  {user_data['creation_date']}\n"""
            bot.edit_message_text(text,cid,mid,reply_markup=markup)       
    elif data=='علاقه مندی ها':               # علاقه مندی های کاربر را نمایش می دهد
        text=str()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('دلار 💷', callback_data='دلار'),InlineKeyboardButton('تومان 💶', callback_data='تومان'))
        markup.add(InlineKeyboardButton('جستجو 🔍', callback_data='جستجو'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        currencies=get_favorites(cid)
        if len(currencies)==0:  # اگر لیست علاقه مندی ها خالی
            bot.edit_message_text('📝 لیست علاقه‌مندی‌های شما در حال حاضر خالی است.',cid,mid,reply_markup=markup)
        else:
            response = requests.get('https://api.wallex.ir/v1/markets')
            if response.status_code == 200 :
                data= response.json()['result']['symbols']
                for currency in currencies:
                    symbol = data[currency]
                    if symbol['stats']['bidPrice'] == '-' : continue
                    price  = float(symbol['stats']['bidPrice'])
                    ch_24h = symbol['stats']["24h_ch"]
                    if ch_24h=='-':continue  # بعضی مواقع API این علامت را می دهد
                    ch_24h = is_plus2(ch_24h)
                    text+=f"💎{symbol['symbol']}/{symbol['faName']}\n{ch_24h}\n💲 {price}\n\n"
                
                bot.edit_message_text(text,cid,mid,reply_markup=markup)
            else:        
                bot.edit_message_text('در سیستم اخلال پیش آمده لطفا دقایقی دیگر مراجعه کنید\nبا تشکر',cid,mid,reply_markup=markup)    
    elif data=='ایجاد حساب کاربری':          # برای ایجاد حساب کاربری از کاربر درخواست نام می کند
        Users[cid].append(cid)
        bot.edit_message_text('📋 لطفاً نام و نام خانوادگی خود را به صورت کامل وارد کنید',cid,mid)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        user_step[cid]='Fname_Lname'
    elif data=='واریز':                      # از کاربر می پرسد واریز پگونه باشد
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('تومان  💶', callback_data='واریز تومان'),InlineKeyboardButton('ارز های دیگر 🌐', callback_data='واریز ارز های دیگر'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='واریز & برداشت'))
        bot.edit_message_text('لطفاً ارز مورد نظر خود را انتخاب کنید ⭐:',cid,mid,reply_markup=markup)
    elif data=='برداشت':                     # از کاربر می پرسد برداشت چگونه باشد 
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('تومان 💶', callback_data='برداشت تومان'),InlineKeyboardButton('ارز های دیگر 🌐', callback_data='برداشت ارز های دیگر'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='واریز & برداشت'))
        bot.edit_message_text('لطفاً ارز مورد نظر خود را انتخاب کنید ⭐:',cid,mid,reply_markup=markup)
    elif data=='برداشت ارز های دیگر':       # ارز های موجود در کیف پول کاربر را برای برداشت نشان می دهد
        currencies = get_wallet_crrency(cid)
        markup = InlineKeyboardMarkup()
        if len(currencies) == 0: # موجودی کیف پول خالی باشد
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برداشت'))
            markup.add(InlineKeyboardButton('افزایش موجودی 💵', callback_data='واریز')) 
            bot.edit_message_text('🔔 موجودی کیف پول شما ناکافی می‌باشد.',cid,mid,reply_markup=markup)  
        else: 
            for currency in currencies: # ارز های موجود را در قالب دکمه شیشه ای نمایش میدهد
                markup.add(InlineKeyboardButton(currency,callback_data=f'برداشت/{currency}'))
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برداشت'))
            bot.edit_message_text('لطفاً ارز مورد نظر خود را انتخاب کنید ⭐:',cid,mid,reply_markup=markup)    
    elif data=='برداشت تومان':
        amount= int(get_wallet(cid,'TMN'))
        if amount == 0: # اگر موجودی 0 باشد 
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برداشت'))
            markup.add(InlineKeyboardButton('افزایش موجودی 💵', callback_data='واریز')) 
            bot.edit_message_text('🔔 موجودی کیف پول تومان شما ناکافی می‌باشد.',cid,mid,reply_markup=markup)
        else: # موجودی تومان را نمایش می دهد و مقدار مورد نظر برداشت را میگیرد
            user_dataa[cid]['currency']='TMN'
            bot.edit_message_text(f'''💸 لطفاً مبلغ مورد نظر برداشت را وارد کنید:\n\n🔹 موجودی شما: {amount} تومان\n\n🔹 حداقل مبلغ قابل برداشت: 50,000 تومان''',cid,mid,reply_markup=None)
            user_step[cid]='amount_withdrawal'
    elif data=='جستجو':
        markup=InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='لیست قیمت رمز ارز ها'))
        bot.edit_message_text('''🔐 لطفاً نام ارز مورد نظر را به انگلیسی و به صورت کامل وارد نمایید، مانند "BTCTMN" یا "BTCUSDT".\n
💡 برای راهنمایی بیشتر، می‌توانید به لیست قیمت ارزها مراجعه کنید.''',cid,mid,reply_markup=markup)        
        user_step[cid]='search'
    elif data=='تومان':                      # نمایش قیمت تمام ارز ها به تومان
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('دلار 💷', callback_data='دلار'))
        markup.add(InlineKeyboardButton('علاقه مندی ها 💖', callback_data='علاقه مندی ها'),InlineKeyboardButton('جستجو 🔍', callback_data='جستجو'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        bot.edit_message_text('لطفا کمی منتظر باشید . . . ⏳',cid,mid,reply_markup=markup)
        response=requests.get('https://api.wallex.ir/v1/markets')   # دریافت اطلاعات ارز ها
        if response.status_code == 200:
            data= response.json()['result']['symbols']
            tmn=str()
            for currency in data:
                symbol = data[currency] # بدست اوردن اطلاعت هر ارز در قالب یک دیکشنری
                name   = symbol['symbol']
                if name[-3:] != 'TMN': continue   # فقط ارز های بر بستر تومان
                fa_name= symbol['faName']
                if symbol['stats']['bidPrice']=='-': continue
                price  = is_format(symbol['stats']['bidPrice'])
                ch_24h = symbol['stats']["24h_ch"]    # درصد تغییر 24 ساعت گذشته
                if ch_24h=='-':continue
                ch_24h = is_plus2(ch_24h)
                tmn+=f"💎{name}/{fa_name}\n{ch_24h}\n💲 {price}\n\n" 
            bot.edit_message_text(tmn,cid,mid,reply_markup=markup)
        else:
            bot.edit_message_text('در سیستم اخلال پیش آمده لطفا دقایقی دیگر مراجعه کنید\nبا تشکر',cid,mid,reply_markup=markup)           
    elif data=='دلار': 
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('تومان 💶', callback_data='تومان'))
        markup.add(InlineKeyboardButton('علاقه مندی ها 💖', callback_data='علاقه مندی ها'),InlineKeyboardButton('جستجو 🔍', callback_data='جستجو'))
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
        bot.edit_message_text('لطفا کمی منتظر باشید . . . ⏳',cid,mid,reply_markup=markup)
        response=requests.get('https://api.wallex.ir/v1/markets')  # دریافت اطلاعات ارز ها
        if response.status_code == 200:
            data= response.json()['result']['symbols']
            usdt=str()
            for currency in data:
                symbol = data[currency]   # بدست اوردن اطلاعت هر ارز در قالب یک دیکشنری
                name   = symbol['symbol']
                if name[-4:] != 'USDT': continue  # فقط ارز های بر بستر دلار
                fa_name= symbol['faName']
                if symbol['stats']['bidPrice']=='-': continue
                price  = is_format(symbol['stats']['bidPrice'])
                ch_24h = symbol['stats']["24h_ch"]   # درصد تغییر 24 ساعت گذشته
                if ch_24h=='-':continue
                ch_24h = is_plus2(ch_24h)
                usdt+=f"💎{name}/{fa_name}\n{ch_24h}\n💲 {price}\n\n" 
            bot.edit_message_text(usdt,cid,mid,reply_markup=markup)
        else:
            bot.edit_message_text('در سیستم اخلال پیش آمده لطفا دقایقی دیگر مراجعه کنید\nبا تشکر',cid,mid,reply_markup=markup)           
    elif data in ['خیر','برگشت']:
        markup=InlineKeyboardMarkup()
        if cid==admin_cid:
            markup.add(InlineKeyboardButton('مدیریت 🗂️', callback_data='admin_panel'))        
        markup.add(InlineKeyboardButton('لیست قیمت رمز ارز ها 📈',callback_data='لیست قیمت رمز ارز ها'))
        markup.add(InlineKeyboardButton('واریز & برداشت 🏦',callback_data='واریز & برداشت'),InlineKeyboardButton('خرید & فروش 💎', callback_data='خرید & فروش'))
        markup.add(InlineKeyboardButton('کیف پول 💼',callback_data='کیف پول'),InlineKeyboardButton('تاریخچه تراکنش ها 📜', callback_data='تاریخچه تراکنش ها'))
        markup.add(InlineKeyboardButton('پشتیبانی 📞', callback_data='support'),InlineKeyboardButton('حساب کاربری 👤', callback_data='حساب کاربری'))        
        bot.edit_message_text("صفحه اصلی 🏠",cid,mid,reply_markup=markup)
    elif data=='withdrawal_confirmation':     # برداشت تومان از کیف پول
        currency   = user_dataa[cid]['currency']
        card_number= user_dataa[cid]['card_number']
        name       = user_dataa[cid]['name']
        amount     = user_dataa[cid]['amount']
        m_wallet_id= get_wallet_id(cid,currency)
        fee = get_amount_commission()
        fee_ = fee*amount
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)  # ارسال اطلاعات برداشت به ادمین
        bot.send_message(admin_cid,f'🔔 تراکنش برداشت از حساب:\n\n📌 کاربر: {cid}\n📌 مبلغ: {amount} تومان\n📌 شماره کارت: {card_number}\n📌به نام: آقا/خانم {name}')
        bot.send_message(cid,'🔔 تایید شد\n\n💳 تا فردا ساعت ۱۵:۰۰ به حساب شما واریز می‌گردد.')
        withdrawal_from_account(cid,amount,fee_) # برداشت تومان از کیف پول
        amount -= fee_
        logging.info(f'User {cid} withdrew {amount} Toman to {card_number} from their account')
        insert_account_movements(cid,amount,'TMN',m_wallet_id,cid,card_number,'withdrawal') # ثبت اطلاعات برداشت
    elif data=='واریز تومان':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='واریز'))
        bot.edit_message_text('لطفاً مقدار مورد نظر را وارد کنید 📥',cid,mid,reply_markup=markup)
        user_step[cid]='amount_deposit'
    elif data=='واریز ارز های دیگر':         # اسم ارز می گیرد و ادرس کیف پول را می دهد
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('برگشت ↩️', callback_data='واریز'))
        bot.edit_message_text('''🔐 لطفاً نام ارز مورد نظر را به انگلیسی و به صورت کامل وارد نمایید، مانند "BTCTMN" یا "BTCUSDT".\n
💡 برای راهنمایی بیشتر، می‌توانید به لیست قیمت ارزها مراجعه کنید.''',cid,mid,reply_markup=markup)
        user_step[cid]='currency_deposit'
    elif data=='withdrawal_from_wallet':      # برداشت ارز از کیف پول
        currency = user_dataa[cid]['currency']
        amount = user_dataa[cid]['amount']
        fee = get_amount_commission()
        fee_=fee*amount
        update_wallet(1385200618,fee_,currency)  # مقدار کارمزد به ولت همان ارز صرافی انتقال می یابد
        logging.info(f'Fee of {amount} {currency} was charged from user {cid}')
        wallet_id = user_dataa[cid]['wallet_id'] # ادرس ولت مقصد
        m_cid = get_cid(wallet_id,currency) # دریافت cid ولت مقصد
        m_wallet_id = get_wallet_id(cid,currency) # ادرس ولت مبدا
        withdrawal_from_wallet(cid,amount,currency,m_cid) # تراکنش انتقال
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)
        bot.send_message(cid,f'🔔 تراکنش برداشت از حساب \n\n🔹 مقدار : {amount:.8f}\n\n🔹 ارز : {currency}\n\n🔹 آدرس مقصد : {wallet_id}\n\nانجام شد✅')
        amount-=fee_
        bot.send_message(m_cid,f'🔔 تراکنش واریز به حساب\n\n🔹 مقدار : {amount:.8f}\n\n🔹 ارز : {currency}\n\n🔹 آدرس مبدا : {m_wallet_id}\n\nانجام شد✅')
        insert_account_movements(cid,amount,currency,m_wallet_id,m_cid,wallet_id,'withdrawal') # ثبت انتقال
        insert_account_movements(m_cid,amount,currency,m_wallet_id,cid,wallet_id,'Deposit') # ثبت انتقال
        logging.info(f'User {cid} transferred {amount} {currency} to wallet {wallet_id} of user {m_cid}')
    elif data=='buying_currency':
        data = transaction_information[cid]['buying_currency'] # اطلاعات خرید
        currency_ = data[0]
        total_price = float(data[3])
        if currency_.endswith('TMN'):
            inventory = get_wallet(cid,'TMN') 
        else:
            inventory = float(get_wallet(cid,'USDTTMN'))
        if total_price < inventory: # با توجه به ارز پایه موجودی کیف پول را بررسی می کند و اگر کمتر از مقدار خرید باشد به کاربر اطلاع میدهد
            bot.send_message(cid,'''🔐 لطفاً نام کاربری و کلمه عبور خود را به ترتیب زیر وارد کنید:\n
👤 نام کاربری * کلمه عبور 🔑\n
📍 حتما توجه داشته باشید بین نام کاربری و کلمه عبور خود از * استفاده کنید و  نام کاربری شما username تلگرام  شما است 🙏.''')
            user_step[cid]='confirm_password'
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('افزایش موجودی 💵', callback_data='واریز'),InlineKeyboardButton('برگشت ↩️', callback_data='برگشت'))
            if currency_.endswith('TMN'):
                bot.send_message(cid,'🔔 موجودی کیف پول تومان شما ناکافی می‌باشد.',reply_markup=markup)
            else:
                bot.send_message(cid,'🔔 موجودی کیف پول دلار شما ناکافی می‌باشد.',reply_markup=markup)
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)
    elif data=='selling_currency':             # برای فروش ارز درخواست نام کاربری و کلمه عبور می کند
        bot.edit_message_reply_markup(cid,mid,reply_markup=None)   
        bot.send_message(cid,'''🔐 لطفاً نام کاربری و کلمه عبور خود را به ترتیب زیر وارد کنید:\n
👤 نام کاربری * کلمه عبور 🔑\n
📍 حتما توجه داشته باشید بین نام کاربری و کلمه عبور خود از * استفاده کنید و  نام کاربری شما username تلگرام  شما است 🙏.''')
        user_step[cid]='currency_sales_amount'
    elif data.startswith('شارژ حساب'):        # تایید واریز تومان به حساب
        other,amount,cid = data.split('/')
        wallet_id = get_wallet_id(cid,'TMN') # بدست اوردن آیدی کیف پول
        bot.edit_message_reply_markup(admin_cid,mid,reply_markup=None)
        update_wallet_tmn(cid,amount)  # افزایش موجودی کاربر
        logging.info(f'User {cid} deposited {amount} toman')
        amount = int(amount)
        fee = float(get_amount_commission())*amount
        amount -= fee 
        bot.send_message(cid,f'🔔 تراکنش شارژ حساب:\n🔹 مبلغ: {amount} تومان\n\n☑ تایید شد.')
        insert_account_movements(cid,amount,"TMN",None,cid,wallet_id,'Deposit')  
    elif data.startswith('تایید نشد'):        # رسید واریز به ادمین ارسال شده و در صورت تایید نشدن دزخواست توضیحات میکند
        user_cid=data.split('/')[-1]
        bot.edit_message_reply_markup(admin_cid,mid,reply_markup=None)
        markup=ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('تصویر واضخ نیست')
        markup.add('فاکتور ارسال شده معتبر نیست')
        markup.add("تاریخ و زمان در تصویر مشخص نیست")
        markup.add("مبلغ واریز با مبلغ از قبل تعیین شده متفاوت است")      
        bot.send_message(admin_cid,'علت تایید نشدن را بنویسید:',reply_markup=markup)
        user_step[admin_cid]='تایید نشد'
        user_dataa[admin_cid]['comfirm']=user_cid
    elif data.startswith('حذف از علاقه مندی ها'):# ارز را از علاقه مندی ها حذف می کند
        currency=data.split('/')[-1].upper()
        delete_favorite(cid,currency)
        logging.info(f'User {cid} removed {currency} from favorites')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('افزودن به علاقه مندی ها ➕❤️',callback_data=f'افزودن به علاقه مندی ها/{currency}'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    elif data.startswith('فروش'):             # اطلاعات ارز مورد نظر برای فروش را نشان می دهد و از کاربر تعداد فروش را می خواهد
        currency_  = data.split('/')[1].upper()
        amount     = get_wallet(cid,currency_) # بدست اوردن موحودی ان ارز
        response   = requests.get('https://api.wallex.ir/v1/markets')
        symbol     = response.json()['result']['symbols'][currency_] # بذست اوردن اطلاعات ان ارز
        price      = float(symbol['stats']['bidPrice'])
        text       = str()
        total_price= price * amount
        if price!='-':
            ch_24h = symbol['stats']["24h_ch"]
            ch_24h = is_plus2(ch_24h)   # نمایش اطلاعات ارز مورد نظر برای فروش و گرفتن تعداد مورد نظر برای فروش
            text+=f"⭐ نام : {symbol['symbol']}/{symbol['faName']}\n💲 قیمت : {price}\n🔢 تعداد : {amount:.8f}\n💰 مجموع قیمت : {total_price}\n\n🟢 تعداد مورد نظر خود برای فروش را وارد کنید:"
            bot.edit_message_text(text,cid,mid,reply_markup=None)
            user_step[cid]='selling_currency'
            transaction_information[cid]['selling_currency'] = symbol["symbol"]
        else:
            bot.send_message(cid,'🔔 اختلال در سیستم پیش آمده است.\n\nدر اسرع وقت رسیدگی می‌شود.')
    elif data.startswith('افزودن به علاقه مندی ها'): # افزودن به علاقه مندی ها
        currency = data.split('/')[-1].upper()
        insert_favorite(cid,currency) # ارز را به علاقه مندی ها اضافه کرد
        logging.info(f'User {cid} added {currency} to favorites')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('حذف از علاقه مندی ها ❌❤️', callback_data=f'حذف از علاقه مندی ها/{currency}'))
        bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    elif data.startswith('برداشت'):             # برای بردشت ارز مقدار مورد نظر را میپرسد
        currency = data.split('/')[-1]
        amount   = get_wallet(cid,currency)
        amount   = is_format(amount)
        text     = f'💎 نام : {currency}\n🔢 تعداد : {amount:.8f}\n\n📥 لطفاً مقدار مورد نظر برداشت را وارد کنید.'
        bot.edit_message_text(text,cid,mid)
        user_dataa[cid]['currency']=currency
        user_step[cid]='withdrawal_amount'

@bot.message_handler(commands=['start'])
def message_start(message):
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    markup=InlineKeyboardMarkup()
    if cid==admin_cid:
        markup.add(InlineKeyboardButton('مدیریت 🗂️', callback_data='admin_panel'))        
    markup.add(InlineKeyboardButton('لیست قیمت رمز ارز ها 📈',callback_data='لیست قیمت رمز ارز ها'))
    markup.add(InlineKeyboardButton('واریز & برداشت 🏦',callback_data='واریز & برداشت'),InlineKeyboardButton('خرید & فروش 💎', callback_data='خرید & فروش'))
    markup.add(InlineKeyboardButton('کیف پول 💼',callback_data='کیف پول'),InlineKeyboardButton('تاریخچه تراکنش ها 📜', callback_data='تاریخچه تراکنش ها'))
    markup.add(InlineKeyboardButton('پشتیبانی 📞', callback_data='support'),InlineKeyboardButton('حساب کاربری 👤', callback_data='حساب کاربری'))        
    bot.send_message(cid, "🌟 به صرافی JBCOIN خوش آمدید! 🌟\n\n🔹 برای دریافت راهنمایی و اطلاعات بیشتر، لطفاً دستور /help را وارد کنید.",reply_markup=markup)
    user_step[cid]=None
    user_dataa[cid]={}

@bot.message_handler(commands=['help'])
def message_help(message):
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    bot.send_message(cid,help_text)   # متن راهنمایی را از فایل persian text ایمپورت شده است
    user_step[cid]=None
    user_dataa[cid]={}

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='send_message_to_user')
def message_text_to_user(message): # cid که ادمین میخواهد به ان  پیام ارسال کند را دریافت می کند و درخواست پیام می کند
    cid=message.chat.id
    user_cid=message.text
    users = get_all_user_cid()
    username = message.from_user.username
    if is_spam(cid,username):return
    if user_cid.isdigit() and len(user_cid)==10:
        if int(user_cid) in users:
            bot.send_message(cid,'📩 لطفاً پیام خود را وارد کنید:')
            user_step[cid]='message_text'
            user_dataa[cid]['user_cid']=user_cid
        else:
            bot.send_message(cid,'🚫 شناسه کاربری وارد شده (CID) صحیح نمی‌باشد.')
    else:
        bot.send_message(cid,'🚫 شناسه کاربری وارد شده (CID) صحیح نمی‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='send_message_ALLusers')
def send_message_to_users(message): # پیام کاربر را میگیرد و مجوز ارسال پیام به همه کاربران را درخواست می کند
    cid=message.chat.id
    text=message.text
    username = message.from_user.username
    if is_spam(cid,username):return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('بله 👍', callback_data='confirm_sending_message'),InlineKeyboardButton('خیر 👎', callback_data='برگشت'))
    bot.send_message(cid,f'❓ پیام زیر برای تمامی کاربران ربات ارسال شود؟\n\n\n💬 پیام : {text}',reply_markup=markup)
    user_dataa[cid]['message_all_user']=text

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='message_text')
def send_a_message_to_user(message): # پیام ادمین را دریاغت می کند و به کاربر ارسال می کند
    cid=message.chat.id
    text=f'📢 این پیام از طرف ادمین ربات می‌باشد:\n\n💬 {message.text}'
    user_cid=user_dataa[cid]['user_cid'] # cid  کاربر که در مرحله قبل دریافت و ذخیره شده است
    username = message.from_user.username
    if is_spam(cid,username):return
    bot.send_message(user_cid,text)
    logging.info(f'Admin sent message "{message.text}" to user {user_cid}')
    bot.send_message(cid,'✅ پیام شما به کاربر ارسال شد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='wallet_address')
def wallet_address_test(message): # ادرس ولت مقصد را دریافت می کند و از کاربر تایید نهایی برای انتقال را می گیرد
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    
    currency  = user_dataa[cid]['currency']
    amount    = user_dataa[cid]['amount']
    wallets   = get_wallet_data_address(currency) # گرفتن تمام ولت های ارز مورد نظر
    wallet_id = message.text
    markup    = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('بله 👍', callback_data='withdrawal_from_wallet'),InlineKeyboardButton('خیر 👎', callback_data='خیر'))
    
    if int(wallet_id) in wallets:   # چک می کند ایا کیف پول وجود دارد یا خیر
        text=f'🔔 انتقال ارز:\n\n🔹 نوع ارز: {currency}\n\n🔹 تعداد: {amount:.8f}\n\n🔹 کیف پول مقصد: {wallet_id}\n\n❓ آیا انجام شود؟'
        bot.send_message(cid,text,reply_markup=markup)
        user_dataa[cid]['wallet_id']=wallet_id
    
    else:
        bot.send_message(cid,'🚫 آدرس کیف پول وارد شده نامعتبر می‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='amount_commission')
def fee_change(message): # مقدار جدید کارمزد را دریافت کرده و از ادمین تایید میخواهد
    cid = message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return 
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('بله 👍', callback_data='amount_commission'),InlineKeyboardButton('خیر 👎', callback_data='admin_panel'))
    
    if is_int(message.text):
        amount = float(message.text)
        
        if 0<=amount<=100:
            amount_fee = str(amount/100)
            bot.send_message(cid,f'🔔 تغییر کارمزد تراکنش‌ها:\n\n🔹 مقدار جدید: {amount}%\n\n🔹 آیا این تغییر اعمال شود؟',reply_markup=markup)
            user_dataa[cid]['amount_commission']=amount_fee  
        
        else:
            bot.send_message(cid,'🚫 عدد وارد شده باید میان 0 تا 100 باشد.')        
    
    else:
        bot.send_message(cid,'🚫 عدد وارد شده صحیح نمی‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='withdrawal_amount')
def currency_withdrawal_amount(message): # تعداد مورد نظر ارز برای برداشت را دریافت کرده و از کاربر تقاضای ادرس ولت مقصد را می کند
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    
    if is_int(message.text):
        response       = requests.get('https://api.wallex.ir/v1/markets')
        number         = float(message.text)
        currency       = user_dataa[cid]['currency']
        amount_wallet  = get_wallet(cid,currency)
        price          = get_price(currency,response)
        total_price    = number * price
        if total_price>=50000:
            if  number<=amount_wallet:
                bot.send_message(cid,f'''📥 آدرس کیف پول مقصد را وارد کنید.\n
🔴 توجه داشته باشید: در صورت مغایرت ارز کیف پول مقصد با ارز واریزی ({currency})، ارز واریز شده از بین می‌رود.''')
                user_dataa[cid]['amount']=number
                user_step[cid]='wallet_address'
            else:
                bot.send_message(cid,'⚠️ عدد وارد شده بیش از حد مجاز است و از موجودی شما بیشتر می‌باشد.')
        else:
            bot.send_message(cid,f'🔴 حداقل مبلغ انتقال: 50,000 تومان\n\n🔹 مبلغ انتقال شما در حال حاضر: {total_price} تومان')
    else:
        bot.send_message(cid,'🚫 عدد وارد شده نامعتبر می‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='currency_deposit')
def get_currency_address(message): # برای واریز ارز به کاربر ادرس ولت را می دهد
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    
    currencies = get_currency_data()  # دریافت لیست ارز ها
    currency   = message.text.upper()
    
    if currency in currencies:  # اگر اسم ارز وارد شده صحیح باشد
        wallet_list = get_wallet_data()
        
        if (cid,currency) not in wallet_list: # اگر کاربر ولت را نداشته باشد ایجاد می کند
            insert_wallet_data(cid,currency,0)
        wallet_id = get_address_currency(cid,currency) # دریافت ادرس ولت
        response  = requests.get('https://api.wallex.ir/v1/markets')
        data      = response.json()['result']['symbols'][message.text.upper()]
        icon      = data['baseAsset_png_icon']   # دریافت عکس ارز با استفاده از API
        fa_name   = data["faBaseAsset"]
        name      = f'{data["symbol"]}/{data["faName"]}'
        
        bot.send_photo(cid,icon,f'''🔔 اطلاعات کیف پول:\n\n🔹 نام ارز: {name}\n\n🔹 آدرس: {wallet_id}\n
🔴 هشدار: این آدرس فقط برای ارز {fa_name} می‌باشد. در صورتی که ارز دیگری واریز شود، از بین خواهد رفت.''')
    
    else:
        bot.send_message(cid,'🚫 نام ارز وارد شده معتبر نمی‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='amount_deposit')
def send_exchangr_card_number(message): # مبلغ برداشت تومان را دریافت می کند و عکس شماره کارت را ارسال می کند
    cid = message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    
    if is_int(message.text):
        amount = int(message.text)
        if amount >= 50000:
            photo_id         = bank_card_photo # عکس و شماره کارت بانک از فایل config 
            bank_card_number = bank_card
            bot.send_photo(cid,photo_id,caption=f"""🔔 لطفاً مبلغ {amount} تومان را به شماره کارت زیر واریز نمایید:\n
💳 شماره کارت: `{bank_card_number}`\n
🔹 به نام: امیر مهدی جابری\n
📸 پس از واریز، عکس فیش خود را همینجا و در همین لحظه ارسال کنید\n
⚠️ توجه داشته باشید:\n
1 در صورت مغایرت مبلغ فیش واریزی با مبلغ اعلام شده، فیش شما تایید نخواهد شد
2 حتماً ساعت و تاریخ در فاکتور واریزی مشخص باشد""",parse_mode='MarkdownV2')
            logging.info(f'Bank card number {bank_card_number} was sent to user {cid}')
            user_step [cid]='photo'
            user_dataa[cid]['amount_deposit'] = amount
        else:
            bot.send_message(cid,'⚠️ حداقل مبلغ واریز 50,000 می‌باشد.')
    else:
        bot.send_message(cid,'🚫 مبلغ وارد شده صحیح نمی‌باشد. لطفاً مجدداً وارد کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='Fname_Lname')
def insert_firstname_lastname(message): # اسم کاربر را دریافت میکند و از کاربر درخواست کلمه عبور می کند
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    name = message.text
    if is_str(name) and len(name)<50:
        Users[cid].append(name)
        bot.reply_to(message,'تایید شد ✅')
        bot.send_message(cid,'🔐 لطفاً کلمه عبور خود را وارد کنید.')
        user_step[cid]='password'
    else:
        bot.send_message(cid,'🚫 نامعتبر می‌باشد. لطفاً به صورت صحیح وارد کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='password')
def insert_password(message): # کلمه عبور را دریافت می کند و از کاربر درخواست شماره تلفن می کند
    cid = message.chat.id
    username = message.from_user.username
    if is_spam(cid,username): return
    password = str(message.text)
    if len(password)<25:
        Users[cid].append(password) # ذخیره اطلاعات
        bot.reply_to(message,'تایید شد ✅')
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton('📱 آیا مایلید شماره تلفن خود را به اشتراک بگذارید؟', request_contact=True))
        bot.send_message(cid, '📱 لطفاً شماره تلفن خود را ارسال کنید.\n(0939.......)', reply_markup=markup)
        user_step[cid]='phone_number'
    else:
        bot.send_message(cid,'🚫 نامعتبر می‌باشد. لطفاً به صورت صحیح وارد کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='phone_number')
def insert_phone_number(message): # شماره تلفن را دریافت می کند و تمامی اطلاعات را وارد دیتابیس می کند
    cid = message.chat.id
    username = message.from_user.username
    number = str(message.text)
    markup = ReplyKeyboardRemove()
    if is_spam(cid,username):return
    if number.isdigit() and len(number) == 11 :
        Users[cid].append(number) # شماره را به اطلاعات کاربر اضافه می کند
        Users[cid].append('True') # حالت احراز حویت کاربر را به True تغییر داده میشود
        password = Users[cid][2]
        bot.reply_to(message,'تایید شد ✅')
        update_user_data(*Users[cid]) # اطلاعات کاربر را در دیتابیس آپدیت می کند
        logging.info(f'User {cid} registered with phone number {number} and username {username}')
        bot.send_message(cid,f'''✅ حساب کاربری شما با موفقیت ایجاد شد.\n\n🔹 نام کاربری: {username}\n\n🔹 کلمه عبور: {password}\n\n
⚠️ لطفاً نام کاربری و کلمه عبور خود را فراموش نکنید و در جای امن نگهداری کنید.''',reply_markup=markup)
        user_step[cid]=None
    else:
        bot.send_message(cid,'🚫 نامعتبر می‌باشد. لطفاً به صورت صحیح وارد کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='amount_withdrawal')
def amount_withdrawal_tmn(message): # مقدار برداشت تومان را دریافت می کند و  از کاربر می خواهد شماره کارت بانکی خود را ارسال کند
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    wallet = get_wallet(cid,'TMN') # موجودی ولت تومان کاربر
    if is_int(message.text):
        amount=int(message.text) # مقداری که کاربر می خواهد برداشت کند
        
        if 50000>amount:
            bot.send_message(cid,'🚫 مبلغ وارد شده کمتر از 50,000 تومان می باشد . لطفاً مجدداً وارد کنید.')
        elif amount>=wallet:
            bot.send_message(cid,'🚫 مبلغ وارد شده بیشتر از موجودی شما می باشد . لطفاً مجدداً وارد کنید.')
        
        else:
            bot.send_message(cid,'''🔔 لطفاً شماره کارت حساب مقصد و نام صاحب حساب را به صورت زیر وارد کنید:\n
💳 1234567812345678 \n👤 نام و نام خانوادگی\n\n
⚠️ توجه داشته باشید: اگر نام وارد شده با نام مالک شماره کارت مغایرت داشته باشد، مبلغ واریز نمی‌شود.''')
            user_step[cid]='destination_card_number'
            user_dataa[cid]['amount']=amount
    else:
        bot.send_message(cid,'🚫 مبلغ وارد شده معتبر نمی‌باشد. لطفاً مجدداً وارد کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='destination_card_number')
def confirm_withdrawal_from_account(message): # شماره کارت کاربر را جهت برداشت دریافت میکند و از کارب تایید نهایی برای برداشت را میخواهد
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    if len(message.text.split('\n'))==2: # شماره کارت و نام صاحب کارت را با \n جدا میکند
        card_number , name = message.text.split('\n')
        amount = user_dataa[cid]['amount']
        if is_int(card_number) and is_card(card_number):  # بررسی می کند که شماره کارت صحیح باشد
            fee = float(get_amount_commission()*100)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('بله 👍',callback_data=f'withdrawal_confirmation'),InlineKeyboardButton('خیر 👎',callback_data='خیر'))
            bot.send_message(cid,f'''💵 مبلغ: {amount} \n\n💳 به حساب: {card_number} \n\n📝 به نام: {name} \n
💡 بدون احتساب {fee}% کارمزد برداشت 🔴\n
نکته: در صورت اشتباه بودن شماره کارت یا نام صاحب حساب، وجه مورد نظر از بین می‌رود.\n
وجه تا فردا ساعت 15:00 به حساب شما واریز می‌شود. ✅ آیا تأیید می‌کنید؟''',reply_markup=markup)
            user_dataa[cid]['card_number'] = card_number
            user_dataa[cid]['name'] = name
        else:
            bot.send_message(cid,'🚫 شماره کارت وارد شده صحیح نمی‌باشد.')
    else:
        bot.send_message(cid,'🚫 متن وارد شده نا درست می باشد.\n💡 توجه داشته باشید که نام و نام خانوادگی حتماً باید زیر شماره کارت قرار بگیرد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='amount_buying_currency')
def amount_buying_currency(message): # مقدار خربد ارز را دریافت می کند و از کاربر درخواست تایید نهایی می کند
    cid = message.chat.id
    mid = message.message_id
    username = message.from_user.username
    if is_spam(cid,username):return
    number = message.text
    if is_int(number):
        symbol      = user_dataa[cid]['symbol']
        response    = requests.get('https://api.wallex.ir/v1/markets')
        data        = response.json()['result']['symbols'][symbol]
        fa_name     = data['faName']
        price       = float(data['stats']['bidPrice'])
        number1     = float(message.text)
        total_price = round(price*number1,3)
        usdt        = get_price('USDTTMN',response)
        if symbol.endswith('USDT'): # اگر ارز بر بستر دلار باشد قیمت را ضرب دلار می کند تا چک کند از 50000 بیشتر است
            total_price *= usdt
        if total_price>=50000:
            if symbol.endswith('USDT'): # قیمت تومان را به دلار تبدیل می کند
                total_price/=usdt
            transaction_information[cid]['buying_currency']=[symbol,price,number,total_price] # اطلاعات خرید را ذخیره می کند برای مرحله بعد
            markup=InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('بله 👍', callback_data='buying_currency'),InlineKeyboardButton('خیر 👎', callback_data='خیر'))
            text=f"⭐ نام : {symbol}/{fa_name}\n💲 قیمت : {price}\n🔢 تعداد : {number1:.8f}\n💰 مجموع قیمت : {total_price}\n\n🟢 آیا می خواهید که تراکنش انجام شود؟"
            bot.send_message(cid,text,reply_markup=markup)
            bot.delete_message(cid,mid-1) # زیبایی کار
        else:
            bot.send_message(cid,'🔔 کاربر گرامی، لطفاً توجه داشته باشید که حداقل مبلغ تراکنش 50000 تومان می‌باشد.')
    else:
        bot.send_message(cid,'''🔔 کاربر گرامی، عدد وارد شده نامعتبر می‌باشد. لطفاً مجدداً تلاش کنید و عدد صحیح را وارد نمایید.
📊 در صورت نیاز به راهنمایی بیشتر، به پشتیبانی پیام بدهید.''')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id) in  ['search','buying'])
def get_currency_dataa(message): # در صورت جستجو یا برای خرید ارز اسم ارز را می گیرد و اطلاعات دقیقی به کاربر می دهد
    cid = message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    currency = message.text.upper()
    response=requests.get('https://api.wallex.ir/v1/markets')
    currencies = get_currency_data()
    if response.status_code == 200 and currency in currencies:
        data     = response.json()['result']['symbols'][currency]
        stats    = data['stats']
        day      = is_plus(stats["24h_ch"]) # درصد تغییر ارز را میگیرد و چک میکند مثبت است یا منفی برای گذاشتن ایموجی مثبت و منفی
        week     = is_plus(stats["7d_ch"])
        symbol   = data["symbol"]
        icon     = data['baseAsset_png_icon']
        faName   = data["faName"]
        highPrice= float(stats["24h_highPrice"])
        lowPrice = float(stats["24h_lowPrice"])
        volume   = float(stats["24h_volume"])
        markup   =InlineKeyboardMarkup()
        favorites=get_favorites(cid)   
        if currency in favorites:  # بررسی می کند ایا ارز در علاقه مندی ها وجود دارد یا نه و با توجه به ان دکمه شیشه ای را تغییر می دهد
            markup.add(InlineKeyboardButton('حذف از علاقه مندی ها ❌❤️', callback_data=f'حذف از علاقه مندی ها/{message.text}'))
        else:
            markup.add(InlineKeyboardButton('افزودن به علاقه مندی ها ➕❤️',callback_data=f'افزودن به علاقه مندی ها/{message.text}'))
        text=f'''\n⭐ نام ارز : {symbol}\{faName}\n
💲 آخریت قیمت : {float(stats["bidPrice"])}\n
📈 درصد تغییر قیمت(24h)  :  {day}\n
📉 درصد تغییر قیمت(7d)  :  {week}\n
🔺 بیشترین قیمت(24h)  :  {highPrice}\n
🔻 کمترین قیمت (24h)  :  {lowPrice}\n
📊 حجم معاملات (24h)  :  {volume}
'''
        if user_step[cid]=='search':  # اگر کاربر از بخش جستجو امده باشد
            bot.send_photo(cid,icon,caption=text,reply_markup=markup)
        elif user_step[cid]=='buying': # اگر کاربر از بخش خرید ارز امده باشد
            text+='\n\n\n🟢 تعداد مورد نظر خود برای خرید را وارد کنید:'
            bot.send_photo(cid,icon,caption=text,reply_markup=markup)
            user_dataa[cid]['symbol'] = symbol # نام ارز را برای مرحله بعدی ذخیره می کند
            user_step[cid] = 'amount_buying_currency'
    else:
        bot.send_message(cid,'''🔐 نام ارز وارد شده نادرست است. لطفاً دوباره تلاش کنید و نام ارز مورد نظر را به انگلیسی و به صورت کامل وارد نمایید، مانند "BTCTMN" یا "BTCUSDT".\n
💡 برای راهنمایی بیشتر، می‌توانید به لیست قیمت ارزها مراجعه کنید.''')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='selling_currency')
def amount_currency_sell(message): # مقدار فروش ارز را دریافت می کند و از کاربر تایید نهایی را می خواهد
    cid = message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    text = str()
    if is_int(message.text):
        amount        = float(message.text)
        currency      = transaction_information[cid]['selling_currency'] # اطلاعات فروش که در مرحله قبل ذخیره شده
        amount_wallet = get_wallet(cid,currency) # دریافت موجودی ولت ارز کاربر
        if amount <= amount_wallet:
            response    = requests.get('https://api.wallex.ir/v1/markets')
            data        = response.json()['result']['symbols']
            symbol      = data[currency]
            currency    = symbol['symbol']
            price       = float(symbol['stats']['bidPrice'])
            usdt        = float(data['USDTTMN']['stats']['bidPrice'])
            name        = f"{symbol['symbol']}/{symbol['faName']}"
            total_price = price*amount
            if currency.endswith('USDT'):
                total_price=total_price*usdt
            if total_price >= 50000: 
                text+=f"⭐ نام : {name}\n💲 قیمت : {price}\n🔢 تعداد : {amount:.8f}\n💰 مجموع قیمت : {total_price}\n\nآیا می‌خواهید که تراکنش انجام شود؟ ✅"
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('بله 👍', callback_data='selling_currency'),InlineKeyboardButton('خیر 👎', callback_data='خیر'))
                transaction_information[cid]['selling_currency']=[currency,amount,price]
                bot.send_message(cid,text,reply_markup=markup)
            else:
                bot.send_message(cid,f'⚠️ حداقل مبلغ تراکنش 50,000 می‌باشد.\n\n💸 مبلغ فعلی تراکنش شما {total_price} تومان می‌باشد.')
        else:
            bot.send_message(cid,'🚫 تعداد وارد شده بیشتر از موجودی شما می‌باشد.')
    else:
        bot.send_message(cid,'🚫 ورودی نامعتبر می‌باشد. لطفاً به صورت صحیح وارد کنید.\n\n💡 برای اعشار از . استفاده کنید')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='confirm_password')
def confirm_password(message):    # کلمه عبور و نام کاربری را می گیرد و اگر تایید شود تراکنش خرید را انجام می دهد
    cid = message.chat.id
    mid = message.message_id
    username = message.from_user.username
    if is_spam(cid,username) :return
    if len(message.text.split('*')) == 2:
        username,password = message.text.split('*') # نام کاربری و کلمه عبور که کاربر برای خرید ارز وارد کرده است
        user,pas = get_username_password(cid) # نام کاربری و کلمه عبور کاربر را از دیتابیس میگیرد
        if username!=user:
            bot.send_message(cid,'👤 نام کاربری وارد شده اشتباه است. لطفاً دوباره تلاش کنید.')
        elif password!=pas:
            bot.send_message(cid,'🔑 کلمه عبور وارد شده اشتباه است. لطفاً دوباره تلاش کنید.')
        else: # اگر نام کاربری و پسورد درست باشد تراکنش خرید انجام می شود
            symbol,price,number,total_price=transaction_information[cid]['buying_currency'] # اطلاعات ذخیره شده در مرحله قبل
            number      = float(number)
            total_price = float(total_price)
            wallet_list = get_wallet_data()
            base='USDTTMN'
            if (cid,symbol) not in wallet_list:   # چک میکند اگر کاربر ولت ان ارز نداشته باشد برایش ایجاد می کند
                insert_wallet_data(cid,symbol,0)
            if (1385200618,symbol) not in wallet_list: # اگر صرافی ولت ان ارز را نداشته باشد ایجاد می کند
                insert_wallet_data(1385200618,symbol,0)
            if symbol.endswith('TMN'):
                base='TMN'             
            buying_currency1(cid,total_price,base) # مبلغ پرداخت شده کاربر را به ولت تومان صرافی انتقال می دهد
            buying_currency2(total_price,number,symbol,base) # مبلغ در صرافی را از تومان به ارز مورد نظر تبدیل می کند
            buying_currency3(cid,number,symbol) # ارز تبدیل شده را از ولت صرافی به ولت کاربر انتقال می دهد
            insert_transactions(cid,symbol,number,'buy',price)  # تراکنش را ذخیره می کند
            logging.info(f'User {cid} purchased {number} {symbol} at unit price of {price}')
            if base=='TMN':
                fa_base='تومان'
            else:
                fa_base='دلار'
            bot.send_message(cid,f'''🔔 تراکنش خرید شما با موفقیت انجام شد.\n\n💰 مبلغ پرداختی: {total_price:.2f} {fa_base}''')
            bot.delete_message(cid,mid) # حذف کلمه عبور ارسال شده توسط کاربر
    else:
        bot.send_message(cid,'🔐 نام کاربری یا کلمه عبور وارد شده اشتباه است. لطفاً دوباره تلاش کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='add_user_spams')
def add_user_spams(message):  # cid کاربر را دریافت از ادمین دریافت می کند برای اضافه کردن به ایست اسپم
    cid=message.chat.id
    username = message.from_user.username
    user_cid = str(message.text)
    if is_spam(cid,username):return
    spam = get_spams() # cid کاربران اسپم را به صورت تاپل در لیست دریافت می کند
    spams = []
    for id in spam:  
        spams.append(id[0])
    if user_cid.isdigit() and len(user_cid)==10:
        if int(user_cid) not  in spams: # اگر کاربر در لیست اسپم ها حضور نداشته باشد
            add_spams(user_cid)   # کاربر را به لیست اسپم ها اضافه میکند
            logging.info(f'User {cid} was blocked by admin')
            bot.send_message(cid,f'🚫 کاربر {user_cid} به لیست مسدودها اضافه شد.')
            user_step[cid]=None
        else:
            bot.send_message(cid,'🚫 شناسه کاربری وارد شده در لیست مسدودها وجود دارد.')
    else:
        bot.send_message(cid,'🚫 شناسه کاربری وارد شده درست نمی‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='remove_user_spams')
def remove_user_spams(message): # cid کاربر را از ادمین دریافت می کنه و از لیست اسپم ها حذف میکنه
    cid=message.chat.id
    username = message.from_user.username
    user_cid=message.text
    if is_spam(cid,username):return
    spam=get_spams() # cid کاربران اسپم را به صورت تاپل در لیست دریافت می کند
    spams=[]
    for id in spam:
        spams.append(id[0])
    if user_cid.isdigit() and len(user_cid)==10:
        if int(user_cid) in spams: # اگر کاربر در لیست اسپم ها حضور داشته باشد
            remove_spams(user_cid) # کاربر را از لیست اسپم ها حذف میکند
            update_warning_to_zero(user_cid)
            logging.info(f'User {cid} was unblocked by admin')
            bot.send_message(cid,f'🚫 کاربر {user_cid} از لیست مسدودها حذف شد.')
            user_step[cid]=None
        else:
            bot.send_message(cid,'🚫 شناسه کاربری وارد شده در لیست مسدودها وجود ندارد.')
    else:
        bot.send_message(cid,'🚫 شناسه کاربری وارد شده درست نمی‌باشد.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='support_message')
def support_message(message): # پیام دریافت شده از کاربر را به ادمین ارسال می کند
    cid = message.chat.id
    username = message.from_user.username
    message_ = message.text
    if is_spam(cid,username):return
    bot.send_message(admin_cid,f'📧 پیام از طرف کاربر `{cid}` می‌باشد▪\n\n📨 پیام: {message_}',parse_mode='MarkdownV2')
    logging.info(f'User {cid} sent a message to support')
    bot.send_message(cid,'✅ پیام شما به پشتیبانی ارسال شد.')
    user_step[cid]=None

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='currency_sales_amount')
def currency_sales_amount(message):  # کلمه عبور و نام کاربری را می گیرد و اگر تایید شود تراکنش فروش را انجام می دهد
    cid = message.chat.id
    mid = message.message_id
    username = message.from_user.username
    if is_spam(cid,username):return
    if len(message.text.split('*')) == 2:
        username,password = message.text.split('*') # نام کاربری و کلمه عبور که کاربر برای فروش ارز وارد کرده است
        user_n,pasw = get_username_password(cid) # نام کاربری و کلمه عبور کاربر را از دیتابیس میگیرد
        if username != user_n:
            bot.send_message(cid,'👤 نام کاربری وارد شده اشتباه است. لطفاً دوباره تلاش کنید.')
        elif password != pasw:
            bot.send_message(cid,'🔑 کلمه عبور وارد شده اشتباه است. لطفاً دوباره تلاش کنید.')
        else: # اگر نام کاربری و پسورد درست باشد تراکنش فروش انجام می شود
            symbol,number,price = transaction_information[cid]['selling_currency']# اطلاعات فروش که ذخیره شده است
            number   = float(number)
            price    = float(price)
            amount_d = number * price
            if symbol.endswith('TMN'):
                base='TMN'
                fa_base='تومان'
            else:
                base='USDTTMN'
                fa_base='دلار'
            sell_currency1(cid,number,symbol)   # ارز مورد نظر را به ولت صرافی انتقال می دهد
            sell_currency2(amount_d,number,symbol,base) # ارز منتقل شده به ولت صرافی را به تومان تبدیل می کند
            sell_currency3(cid,amount_d,base) # تومان را از ولت صرافی به ولت کاربر انتقال می دهد
            insert_transactions(cid,symbol,number,'sell',price) # تراکنش فروش را ثبت می کند
            logging.info(f'User {cid} sold {number} {symbol} at unit price of {price}')
            bot.send_message(cid,f'''🔔 تراکنش فروش شما با موفقیت انجام شد.\n\n💰 مبلغ دریافتی: {amount_d:.3f} {fa_base}''')
            bot.delete_message(cid,mid)# حذف کلمه عبور ارسال شده توسط کاربر
    else:
        bot.send_message(cid,'🔐 نام کاربری یا کلمه عبور وارد شده اشتباه است. لطفاً دوباره تلاش کنید.')

@bot.message_handler(func= lambda m: user_step.get(m.chat.id)=='تایید نشد')
def send_message_invoice_not_approved(message): #پیام علت نایید نشدن را به کاربر ارسال می کند
    username = message.from_user.username
    cid = message.chat.id
    if is_spam(cid,username):return
    user_cid = int(user_dataa[cid]['comfirm'])
    bot.send_message(user_cid,f'🚫 فاکتور شما تایید نشد.\n\n📋 توضیحات: {message.text}\n\n📍  کاربر گرامی جهت پیگیری, فیش واریز خود را به بخش پشتیبانی ارسال کنید . به درخواست شما در اسرع وقت رسیدگی میشود\n\n سپاسگذاریم 🙏')
    user_dataa[cid]={}
    logging.info(f'Receipt submitted by user {user_cid} was not approved due to {message.text}')

@bot.message_handler(content_types=['contact'])
def insert_phone_number_contact(message): # شماره موبایل فرد را دریافت می کند و برای کاربر حساب کاربری ایجاد می کند
    cid=message.chat.id
    markup = ReplyKeyboardRemove()
    username = message.from_user.username
    if is_spam(cid,username):return
    if message.contact is not None:
        phone_number = message.contact.phone_number
        Users[cid].append(phone_number)
        Users[cid].append('True')
        password = Users[cid][2]
        bot.reply_to(message,'تایید شد ✅')
        update_user_data(*Users[cid]) # حساب کاربری را آپدیت می کند
        logging.info(f'User {cid} registered with phone number {phone_number} and username {username}')
        bot.send_message(cid,f'✅ حساب کاربری شما با موفقیت ایجاد شد\n\n👤 نام کاربری: {username}\n\n🔑 کلمه عبور: {password}',reply_markup=markup)
        user_step[cid]=None
    else:
        bot.send_message(cid,'🚫 نامعتبر می‌باشد. لطفاً به صورت صحیح وارد کنید.')

@bot.message_handler(content_types=['photo'])
def photo_handler(message): # فاکتور ارسال شده توسط کاربر را به ادمین ارسال می کند تا ادمین تایید یت تکذیب کند
    cid=message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    if user_step[cid]=='photo':
        amount  = user_dataa[cid]['amount_deposit']
        photo   = message.photo[-1] # id عکس را بدست می اورد
        file_id = photo.file_id
        markup  = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('بله 👍', callback_data=f'شارژ حساب /{amount}/{cid}'),InlineKeyboardButton('خیر 👎', callback_data=f'تایید نشد/{cid}'))
        bot.send_photo(admin_cid,file_id,caption=f'💵 مبلغ : {amount}\n\n👤 شناسه کاربر : {cid}\n\n✅ آیا تأیید می‌شود؟',reply_markup=markup)
        bot.send_message(cid,'⏳ فاکتور ارسالی شما در حال بررسی می‌باشد.\n\n🕒 تا نهایت یک ساعت دیگر خبر تایید شدن یا تایید نشدن را به اطلاع شما می‌رسانیم.')
        logging.info(f'Deposit receipt of user {cid} for the amount of {amount} toman was sent to admin')
        user_dataa[cid]["file_id"]=file_id
    else:
        bot.reply_to(message,'لطفا از ارسال پیام‌های نامربوط خودداری کنید و به موضوعات مورد بحث پایبند باشید.\nبا تشکر🌹.')

@bot.message_handler(func=lambda message: True) 
def handler_message(message): # هندلر جنرال از کاربر بیشتر از 20 یار پیام نامربوط بدهد به مدت یک ساعت اسپم میشود
    cid = message.chat.id
    username = message.from_user.username
    if is_spam(cid,username):return
    bot.reply_to(message,'لطفا از ارسال پیام‌های نامربوط خودداری کنید و به موضوعات مورد بحث پایبند باشید.\nبا تشکر🌹.')
    update_warning(cid)
    number_warning = get_warning(cid)
    if number_warning == 20 :
        add_spams(cid,'False')
        logging.info(f'User {cid} was added to the admin list for one hour')
        bot.send_message(cid,'''🚫 هشدار: دسترسی محدود شد 🚫\n
متاسفانه به دلیل ارسال زیاد پیام‌های نامربوط، شما به مدت 1 ساعت نمی‌توانید به ربات پیام ارسال کنید. لطفاً در ارسال پیام‌های بعدی دقت کنید تا به قوانین جامعه احترام بگذارید.\n
سپاس از درک و همکاری شما.\n\n🕒🛑💬''')
        
def listener(messages): 
    for m in messages:
        cid=m.chat.id
        username = m.from_user.username
        if is_spam(cid,username):return
        user_dataa.setdefault(cid,{})
        Users.setdefault(cid,[])
        transaction_information.setdefault(cid,{})
        if m.content_type == 'text':
            print(f'{m.chat.first_name}  [{cid}] : {m.text}')
        elif m.content_type == 'photo':
            print(f'{m.chat.first_name}  [{cid}] : photo  ')
bot.set_update_listener(listener)

if __name__=='__main__':
    bot_thread = threading.Thread(target=bot.polling(skip_pending=True))
    bot_thread.start()
    run_bot()


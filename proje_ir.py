import logging
import re
import sqlite3
from sqlite3.dbapi2 import connect
from warnings import filters
import requests
from random import sample
from telegram import ReplyKeyboardMarkup, Update,InlineKeyboardButton, InlineKeyboardMarkup,Update
from telegram.ext import (
    UpdateFilter,
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)   


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)



TEXT,ID , PAY = range(3)
Call_TEXT = 0
API_KEY = '27516196-8a33-42d9-b772-1627e4911e13' #owner
#API_KEY = '8d201dc9-d461-48a7-b704-de6d5212cfa1' #me
TOKEN = '1987569439:AAFs4RIyLdVUepKbi9AMZTEfcEDHGhOpkEg'
CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
BOT_ID = 'proje_ir_bot'
CHANNLE_ID = -1001501782672
#ADMIN_ID = 1813603362
ADMIN_ID = 800882871
BOT_MAKER = 800882871
updater = Updater(TOKEN)



def coin_increaser_db(user_id , count):
    connecton = sqlite3.connect('proje_ir.db')
    cursor = connecton.cursor()
    cursor.execute(f'''update users
    set coins = coins + {count}
    where user_id = {user_id}
    ''')
    connecton.commit()
    connecton.close()



def coin_increaser(update : Update , context : CallbackContext):
    if(len(context.args) != 2):
        update.message.reply_text('دستور را به درستی وارد نکرده اید!')
        return 0
    user_id = context.args[0]
    count = context.args[1]
    try:
        coin_increaser_db(user_id , count)
    except:
        update.message.reply_text('''خطایی در اجرای دستور شما رخ داد!
این خطا ممکن است ناشی از مشکلی در دیتابیس باشد!
مجددا تلاش کنید و یا به سازنده ربات اطلاع دهید
''')
    else:
        update.message.reply_text(f'با موفقیت {count} تعداد به سکه های فرد مورد نظر افزوده شد!')



def join_checker(user_id):
    getchatmember = updater.bot.getChatMember(chat_id = CHANNLE_ID , user_id = user_id).status
    if(getchatmember == 'left'):
        return False
    return True


def i_am_joined(update:Update , context:CallbackContext):
    query = update.callback_query
    user_id = query.message.chat.id
    if(join_checker(user_id)):
        menu_asli(user_id)
    else:
        query.answer(text = 'شما هنوز عضو چنل نیستید!')

    

def list_of_ads(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select status,ad_text , ad_call
    from customers
    where user_id = {user_id} and channle_submit
    ''')
    list_of_ads = cursor.fetchall()
    connection.close()
    return list_of_ads

def send_ad_list(update:Update,context:CallbackContext):
    list_of_ad = list_of_ads(update.message.chat.id)
    count = len(list_of_ad)
    update.message.reply_text(f'تعداد آگهی های شما : {count}')
    for ad in list_of_ad:
        status , ad_text , ad_call = ad
        update.message.reply_text(f'''{status}

متن نمایشی آگهی:

{ad_text}
🆔 {ad_call}
''')
    



def auto_back_up(context : CallbackContext):
    context.bot.send_document(chat_id = BOT_MAKER , document = open('proje_ir.db', 'rb') , filename = 'proje_ir.db')

def manual_back_up(update:Update , context:CallbackContext):
    context.bot.send_document(chat_id = BOT_MAKER , document = open('proje_ir.db', 'rb') , filename = 'proje_ir.db')
    

def set_price(update : Update,context : CallbackContext):
    price = update.message.reply_to_message.text
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update settings
    set price = {price}
    ''')
    connection.commit()
    connection.close()
    update.message.reply_text('قیمت آگهی ربات با موفقیت بروزرسانی شد')
    


def get_trans_id(order_id,price): #bara tolide
    url = "https://nextpay.org/nx/gateway/token"
    payload=f'api_key={API_KEY}&amount={price}&order_id={order_id}&callback_uri=https://t.me/{BOT_ID}'
    headers = {
    'User-Agent': 'PostmanRuntime/7.26.8',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    callback = response.json()
    trans_id = callback['trans_id']
    return trans_id



def database_max_id():
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute('''select max(id)
    from customers
    ''')
    ad_count = (cursor.fetchone())[0]
    connection.close()
    if(ad_count == None):
        ad_count = 0
    return ad_count + 1

def last_user_ad_id(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select max(id)
    from customers
    where user_id = {user_id}
    ''')
    ad_id = (cursor.fetchone())[0]
    connection.close()
    return ad_id

def database_get_code_text(user_id):
    id = last_user_ad_id(user_id)
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select order_id,ad_text
    from customers
    where id = {id}
    ''')
    code_text = cursor.fetchone()
    connection.close()
    return code_text #tuple




def database_first_insert(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''insert into customers
    (id , user_id)
    values(
        {database_max_id()} , {user_id}
    )
    ''')
    connection.commit()
    connection.close()

def database_text_update(user_id,text):
    id = last_user_ad_id(user_id)
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update customers
    set ad_text = '{text}'
    where id = {id}
    ''')
    connection.commit()
    connection.close()
def order_id_maker():
    order_char = sample(CHARACTERS,10)
    order_id = ''.join(order_char)
    return order_id

def get_current_price():
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute('''select price
from settings
''')
    price = (cursor.fetchone())[0]
    connection.close()
    return price


def database_call_price_order_trans_update(user_id,call):
    id = last_user_ad_id(user_id)
    order_id = order_id_maker()
    price = get_current_price()
    trans_id = get_trans_id(order_id , price)
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update customers
    set ad_call = '{call}' , order_id = '{order_id}', price = {price},trans_id = '{trans_id}',success = 1
    where id = {id}
    ''')
    connection.commit()
    connection.close()


def user_in_db(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select id 
    from users
    where user_id = {user_id}
    ''')
    if(cursor.fetchone()):
        connection.close()
        return True
    else:
        connection.close()
        return False

def add_user_to_db(user_id , fname , lname , inviter):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select count(id)
    from users
    ''')
    users_count = (cursor.fetchone())[0]
    if(users_count == None):
        users_count = 0
    cursor.execute(f'''insert into users
    (id , user_id,first_name , last_name , inviter)
    values
    ({users_count + 1} , {user_id} , '{fname}' , '{lname}' , {inviter})
    ''')
    connection.commit()
    connection.close()


def menu_asli(chat_id):
    reply_keyboard = [
        ['ثبت آگهی جدید 📝','آگهی های ثبت شده 🗄'],
        ['دریافت سکه رایگان 💰','ارتباط با ما ☎️']
        ]
    reply_keyboard_markup = ReplyKeyboardMarkup(keyboard=reply_keyboard,one_time_keyboard=True,resize_keyboard=True)
    
    updater.bot.send_message(text = '''❌ حتما حتما این متن رو بخونید ❌
⚖️ راهنما و قوانین ثبت آگهی:
📄 متن آگهی باید برای یک خواسته و نیازمندی باشه یعنی نمیتونی چندتا موضوع مختلف رو توی یه آگهی ثبت کنی. 

1️⃣ توی متن آگهی استفاده از لینک و موارد تبلیغاتی مجاز نیست! ⚠️

2️⃣  استفاده از کلمات مستجهن و توهین آمیز ممنوع است.🔒

3️⃣ درج آگهی امتحان، پایان نامه، پروپوزال ممنوع است و درصورت درج توسط پشتیبانی حذف می‌گردد⛔️

4️⃣ برای درج آگهی توانایی های خود، آگهی استخدامی یا انجام پروژه توسط تیم پروژه دانشجویی به پشتیبانی پیام دهید.
@mrtzanvidi

❌ در صورتی که آگهی تون قوانین ذکر شده رو رعایت نکرده باشه آگهی از کانال پاک میشه  و هیچ مسولیتی در قبال وجه پرداختی شما نیست ❌
''',chat_id = chat_id,reply_markup = reply_keyboard_markup)



def welcome(update : Update,context : CallbackContext):
    user_id = update.message.chat.id
    if not (user_in_db(user_id)):
        add_user_to_db(user_id , update.message.chat.first_name , update.message.chat.last_name , inviter= 0)

    menu_asli(user_id)
    
    return ConversationHandler.END


def agahi_text(update : Update,context : CallbackContext):
    #taraf matne agahi ferestade aval varede db mionim:
    database_text_update(update.message.chat.id,update.message.text)
    #baad bayad  dokme biad:

    reply_keyboard = [
        ['ارسال مجدد متن'],
        ['بازگشت به منو 🏛'],
    ]
    reply_keyboard_markup = ReplyKeyboardMarkup(keyboard=reply_keyboard,one_time_keyboard=True,input_field_placeholder="آیدی یا شماره تماس",resize_keyboard=True)

    update.message.reply_text('''حالا لطفا آیدی یا شماره تماسی که میخای برای آگهیت درج بشه رو بفرست

مثال یک: 
@mrtzanvidi
مثال دو: 09120000000
''',reply_markup = reply_keyboard_markup)

    
    return ID
    
    
    
def sabt(update : Update , context : CallbackContext):
    user_id = update.message.chat.id
    if not (user_in_db(user_id)):
        add_user_to_db(user_id , update.message.chat.first_name , update.message.chat.last_name , inviter= 0)
    
    database_first_insert(update.message.chat.id)
    reply_keyboard = [
        ['بازگشت به منو 🏛']
        ]
    
    reply_keyboard_markup = ReplyKeyboardMarkup(keyboard=reply_keyboard,one_time_keyboard=True,input_field_placeholder='متن آگهی',resize_keyboard=True)
    update.message.reply_text('''لطفا متن مورد نظر خود را برای ثبت آگهی بنویسید

مثال : به فردی مسلط به ریاضی مهندسی برای رفع اشکال نیازمندم''',reply_markup = reply_keyboard_markup)
    return TEXT

def make_full_ad(text,call):
    full_ad = f'''#درخواستی

{text}

🆔 {call}
**************************
@proje_ir
''' 
    return full_ad


def id(update : Update,context : CallbackContext):
    reply_keyboard_button = [
            ['بازگشت به منو 🏛']
        ]
    reply_keyboard_button_markup = ReplyKeyboardMarkup(reply_keyboard_button , one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text('''چند لحظه صبر کنید در حال ساخت آگهی شما ...
ممکن است کمي طول بکشد
''',reply_markup = reply_keyboard_button_markup)
    database_call_price_order_trans_update(update.message.chat.id,update.message.text)
    code,text = database_get_code_text(update.message.chat.id) #bara matn va code agahi
    full_ad = make_full_ad(text,update.message.text)
    try:
        trans_id = get_trans_id_price(code)[0]
    except:
        update.message.reply_text('''در هنگام ایجاد آگهی با خطا مواجه شدیم!
لطفا مجددا تلاش کنید
''')
    else:
    
    
        url = f'https://nextpay.org/nx/gateway/payment/{trans_id}'
        
        #code , text
    
        reply_keyboard_inline = [

            [InlineKeyboardButton('پرداخت سکه💰',callback_data=f'#{code}') ,InlineKeyboardButton('پرداخت بانکی💳',url = url)],
            [InlineKeyboardButton('پرداخت کردم',callback_data=f'{code}')]
            
        ]
        reply_keyboard_inline_markup = InlineKeyboardMarkup(reply_keyboard_inline)
        update.message.reply_text(f'''آگهی شما با موفقیت ایجاد شد.


کد یکتا آگهی:{code}


{full_ad}
پس از پرداخت وجه مورد نظر,روی دکمه "پرداخت کردم" کلیک کرده تا آگهی شما در کانال ثبت شود
''',reply_markup = reply_keyboard_inline_markup)
    return ConversationHandler.END


def get_pay_result(trans_id,price):
 
    url = "https://nextpay.org/nx/gateway/verify"
    payload=f'api_key={API_KEY}&amount={price}&trans_id={trans_id}'
    headers = {
    'User-Agent': 'PostmanRuntime/7.26.8',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if(response.json()['code'] == 0):
        return True
    #return False =>>> جهت تست کارکرد
    return False
    


def get_trans_id_price(order_id): #kharej kardan az database
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.execute(f'''select trans_id , price
    from customers
    where order_id = '{order_id}'
    ''')
    trans_id_price = cursor.fetchone()
    connection.close()
    return trans_id_price


def database_status_update(order_id,status):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update customers
    set status = '{status}'
    where order_id = '{order_id}'
    ''')
    connection.commit()
    connection.close()

def database_submit_channle(order_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update customers
    set channle_submit = 1
    where order_id = '{order_id}'
    ''')
    connection.commit()
    connection.close()

def ad_is_finished(full_ad , ad_message_id,user_id,context : CallbackContext):
    finished_text = 'چنانچه پروژه خود را به شخصی واگذار کردید,میتوانید از دکمه زیر وضعیت آن را در کانال به واگذار شده تغییر بدهید.'
    inline_keyboard =[
        [InlineKeyboardButton('واگذار کردم✅',callback_data=f'_{ad_message_id}')]
    ]
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,one_time_keyboard=True)
    context.bot.send_message(chat_id = user_id , text = f'''{full_ad}

{finished_text}
''' , reply_markup = inline_keyboard_markup)


def delete_ad(ad_id):
    updater.bot.delete_message(chat_id = CHANNLE_ID , message_id = ad_id)



def ad_delete_manager(update : Update , context : CallbackContext):
    query = update.callback_query
    query_data = query.data[1:].split(',')
    ad_message_id,user_id = query_data
    print(ad_message_id,user_id)
    try:
        delete_ad(ad_message_id)
    except:
        query.answer('خطایی در حذف پیام از کانال روی داد!')   
    else:
        query.edit_message_text('آگهی با موفقیت با کانال حذف شد!')

        


    


def ad_manager(full_ad , ad_message_id , user_id):
    inline_keyboard_button = [
        [InlineKeyboardButton(text = 'حذف این آگهی' , callback_data=f'!{ad_message_id},{user_id}')],
    ]
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_button , one_time_keyboard=True)
    updater.bot.send_message(chat_id = ADMIN_ID , text = full_ad , reply_markup = inline_keyboard_markup)

def sumbit_to_channle(full_ad,context : CallbackContext):
    inline_keyboard_button =[
        [InlineKeyboardButton(text = 'برای درج آگهیت کلیک کن',url=f'https://t.me/{BOT_ID}')]
    ]
    inline_keyboard_button_markup = InlineKeyboardMarkup(inline_keyboard_button,one_time_keyboard=True)
    channle_ad = context.bot.send_message(chat_id = CHANNLE_ID,text = full_ad,reply_markup = inline_keyboard_button_markup)
    ad_message_id = channle_ad.message_id
    return ad_message_id


    
    

def paid_ad_text_call(order_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select ad_text , ad_call
    from customers
    where order_id = '{order_id}'
    ''')
    text_call = cursor.fetchone()
    connection.close()
    return text_call


def is_not_submited(order_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select channle_submit
    from customers
    where order_id = '{order_id}'
    ''')
    result = (cursor.fetchone())[0]
    connection.close()
    return not result

def change_to_finished(update : Update,context : CallbackContext):
    inline_keyboard_button =[
        [InlineKeyboardButton(text = 'برای درج آگهیت کلیک کن',url=f'https://t.me/{BOT_ID}')]
    ]
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_button)
    query = update.callback_query
    channle_message_id = (query.data)[1:]
    text = (query.message.text).replace('آگهی شما با موفقیت در کانال ثبت شد.','')
    text = text.replace('متن آگهی :' , '').strip()
    setare = '\n'+ 26 * ('*') + '\n@proje_ir'
    finishd_ad_text = re.sub(r'[\u263a-\U0001F194].*(\n.*)*','واگذار شد✅'+setare,text)
    context.bot.editMessageText(text = finishd_ad_text , chat_id = CHANNLE_ID,message_id = channle_message_id,reply_markup = inline_keyboard_markup)
    query.edit_message_text(text='آگهی شما به حالت واگذار شده تغییر پیدا کرد')
    
    
    

def coin_calcu(user_id , calcu):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update users
    set coins = coins {calcu}
    where user_id = {user_id}
    ''')
    connection.commit()
    connection.close()

def user_ad_counter_inviter(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select ad_count,inviter
    from users
    where user_id = {user_id}
    ''')
    user_ad_count_inviter = cursor.fetchone()
    connection.close()
    return user_ad_count_inviter



def pay_check(update : Update,context : CallbackContext):
    query = update.callback_query
    query.answer('در حال برسی پرداخت...')
    user_id = query.message.chat.id
    
    order_id = query.data
    trans_id , price = get_trans_id_price(order_id)
    try:
        if(user_id == ADMIN_ID or user_id == BOT_MAKER or get_pay_result(trans_id,price)):
            #age pardakht shode bood
            database_status_update(order_id,'پرداخت بانکی')
            #text , call ??
            text , call = paid_ad_text_call(order_id)
            full_ad = make_full_ad(text,call)
            if(is_not_submited(order_id)):
                ad_id = sumbit_to_channle(full_ad,context)
                ad_manager(full_ad , ad_id , user_id)
                inline_keyboard =[
                [InlineKeyboardButton('واگذار کردم✅',callback_data=f'_{ad_id}')] #####درست کنش
                ]
                inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,one_time_keyboard=True)
                query.edit_message_text(text=f'''آگهی شما با موفقیت در کانال ثبت شد.
متن آگهی :
{full_ad}
‌
پس از به توافق رسیدن با انجام دهنده شما میتوانید از طریق دکمه زیر ( واگذار شد) اطلاع دهید تا آیدی شما برداشته شود.
''',reply_markup=inline_keyboard_markup)
            database_submit_channle(order_id)
            ad_count , inviter = user_ad_counter_inviter(user_id)
            user_ad_calcu(user_id)
            if(not ad_count and inviter):
                coin_calcu(inviter , '+ 1')
        else:

            context.bot.send_message(chat_id = query.message.chat.id,text = 'شما هنوز پرداخت انجام ندادید!')

    except:
        context.bot.send_message(chat_id = query.message.chat.id,text = 'در هنگام برسی پرداخت شما خطایی روی داده است!لطفا مجددا دکمه پرداخت کردم را کلیک کنید!')




       

    
        

def call_us(update : Update,context : CallbackContext):
    reply_keyboard = [
        ['بازگشت به منو 🏛']
    ]
    reply_keyboard_markup = ReplyKeyboardMarkup(keyboard=reply_keyboard,one_time_keyboard=True,resize_keyboard=True,input_field_placeholder='پیام شما به ادمین')
    update.message.reply_text('''لطفا متن خود را بفرستید:
چنانچه میخواهید ادمین با شما تماس بگیرد,اطلاعات ارتباطی خود را در پیام مربوطه درج کنید.
''',reply_markup = reply_keyboard_markup)
    return Call_TEXT

def call_text(update : Update,context : CallbackContext):
    context.bot.forwardMessage(chat_id = ADMIN_ID,from_chat_id = update.message.chat.id , message_id = update.message.message_id)
    update.message.reply_text('پيام شما به ادمين ارسال شد.')
    return ConversationHandler.END

def coin_counter(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''select coins
    from users
    where user_id = {user_id}
    ''')
    coin_count = cursor.fetchone()[0]
    connection.close()
    return coin_count
        

def is_invited(update : Update,context : CallbackContext):
    inviter = (update.message.text)[7:]
    user_id = update.message.chat.id
    if  (not user_in_db(user_id) and (int(inviter) != user_id)):
        add_user_to_db(user_id , update.message.chat.first_name , update.message.chat.last_name , inviter= inviter)
    welcome(update,context)

def pay_with_coin(update : Update,context : CallbackContext):
    query = update.callback_query
    query.answer('در حال برسی تعداد سکه ها...')
    user_id = query.message.chat.id
    order_id = (query.data)[1:]
    user_coins = coin_counter(user_id)
    if((user_coins and user_coins % 3 == 0) or user_id == ADMIN_ID):
        if(user_id != ADMIN_ID):
            coin_calcu(user_id , '- 3')
        #takmil baraye submit and ....
        database_status_update(order_id,status = 'پرداخت با سکه')
        #text , call ??
        text , call = paid_ad_text_call(order_id)
        full_ad = make_full_ad(text,call)
        if(is_not_submited(order_id)):
            ad_id = sumbit_to_channle(full_ad,context)
            inline_keyboard =[
            [InlineKeyboardButton('واگذار کردم✅',callback_data=f'_{ad_id}')] #####درست کنش
            ]
            inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,one_time_keyboard=True)
            query.edit_message_text(text=f'''آگهی شما با موفقیت در کانال ثبت شد.
متن آگهی :
{full_ad}
‌
پس از به توافق رسیدن با انجام دهنده شما میتوانید از طریق دکمه زیر ( واگذار شد) اطلاع دهید تا آیدی شما برداشته شود.
''',reply_markup=inline_keyboard_markup)
            database_submit_channle(order_id)
            ad_count , inviter = user_ad_counter_inviter(user_id)
            user_ad_calcu(user_id)
            if(not ad_count and inviter):
                coin_calcu(inviter , '+ 1')

    else:
        context.bot.send_message(chat_id = query.message.chat.id,text = f'''تعداد سکه های شما برای ثبت آگهی کافی نمیباشد
تعداد سکه های شما : {user_coins}
تعداد سکه مورد نیاز برای ثبت آگهی : 3
''')



def user_ad_calcu(user_id):
    connection = sqlite3.connect('proje_ir.db')
    cursor = connection.cursor()
    cursor.execute(f'''update users
    set ad_count = ad_count + 1
    where user_id = {user_id}
    ''')
    connection.commit()
    connection.close()

def create_invite_link(update:Update , context:CallbackContext):
    user_id = update.message.chat.id
    coin = coin_counter(user_id)
    update.message.reply_text(text = f'''با لینک اختصاصیت دوستاتو دعوت کن و سکه رایگان بگیر 😋 و با سکه هات اگهی رایگان بزن 🥳

فراموش نکن که کسی که دعوت میکنی باید عضو جدید باشه😎
در ضمن اگر کسی که با لینک تو عضو شده اولین آگهیش رو ثبت کنه ما به تو یک سکه رایگان میدیم 💰🎁 
 تعداد سکه های شما : {coin}
''')
    update.message.reply_text(text = f'''سلام 🌹 
 اگر به دنبال واگذاری پروژه های درسی و کاری خودت به دیگران هستی یا اینکه میخوای از طریق کارای پروژه ای کسب درآمد کنی کانال پروژه دانشجویی رو دنبال کن 
👇👇 
 t.me/{BOT_ID}?start={user_id}
''')

    




def main():

    class is_redirected(UpdateFilter):
        def filter(self , update : Update):
            if(len(update.message.text) > 6):
                return True
            return False


    class is_joined(UpdateFilter):
        def filter(self,update:Update):
            user_id = update.message.chat.id
            getchatmember = updater.bot.getChatMember(chat_id = CHANNLE_ID , user_id = user_id).status
            if(getchatmember == 'left'):
                inline_keyboard_button = [
                    [InlineKeyboardButton(text = 'عضويت در چنل📢',url='https://t.me/proje_ir') , InlineKeyboardButton(text = 'عضو شدم✅',callback_data=f'+{user_id}')]
                ]
                inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_button)
                update.message.reply_text('برای استفاده از ربات اول باید تو کانال جوین بشی 🌹' , reply_markup=inline_keyboard_markup)
    

                return False
            return True



    
            

    class is_swear(UpdateFilter):
        def filter(self , update:Update):
            
            message_text = update.message.text
            if(re.search(r'(.*\u062f\u0631\u0648\u0633\s.*|.*\u062f\u0631.*\u062e\u062f\u0645\u062a\u0645|.*\u0628\u0633\u067e\u0627\u0631\u06cc\u062f.*|.*\u067e\u0630\u06cc\u0631\u0641\u062a\u0647\s.*|.*\u062e\u062f\u0645\u062a.*|.*\u0633\u0641\u0627\u0631\u0634.*|.*\u0628\u0647\u062a\u0631\u06cc\u0646.*|.*\u06a9\u06cc\u0641\u06cc\u062a.*|.*\u0645\u0646\u0627\u0633\u0628.*|.*\u06a9\u0645\u062a\u0631\u06cc\u0646.*|.*\u0645\u0698\u062f\u0647.*|.*\u0645\u0633\u0644\u0637\u0645.*|.*\u062a\u0636\u0645\u06cc\u0646.*|.*\u062e\u0648\u0627\u0633\u062a\s.*|.*\u0645\u0642\u0627\u0637\u0639.*|.*\u0633\u0627\u062e\u062a.*|.*\u0647\u0631\s*\u06af\u0648\u0646\u0647.*|.*\u062d\u0631\u0641\u0647.*|\s\u0645\u06cc\u062f\u0645.*|.*\u0627\u0633\u062a\u062e\u062f\u0627\u0645.*|.*\u0645\u0634\u0627\u0648\u0631\u0647.*|.*\u0647\u0645\u0627\u0647\u0646\u06af.*|.*\u0628\u0627\s\u0633\u0644\u0627\u0645.*|.*\u0646\u0645\u0648\u0646\u0647\s\u06a9\u0627\u0631.*|.*\u0631\u0636\u0627\u06cc\u062a.*|.*\u0645\u0633\u0644\u0637.*\u0647\u0633\u062a\u0645.*|.*\u062a\u0648\u0633\u0637.*|.*\u06a9\u0644\u06cc\u0647\s.*|.*\u0631\u0632\u0631\u0648.*|.*\u062a\u0645\u0627\u0645\u06cc\s.*|.*\u0631\u0632\u0648\u0645\u0647\s.*|.*\u0628\u0631\u062a\u0631\u06cc\u0646.*|\u0627\u0646\u062c\u0627\u0645\s\u0645\u06cc\u0634\w{1,2}.*|.*\u0627\u0633\u062a\u0627\u062f.*|.*\u0628\u0631\u062c\u0633\u062a\u0647.*|.*\u062a\u062f\u0631\u06cc\u0633.*|.*\u062f\u0627\u0646\u0634\u062c\u0648\u06cc\u06cc.*|[😐🤣😂✅⚠️❗️‼️⁉️❓💢⭕️⛔️📛❌💯🔴🟠🟡🟢🔵⚫️⚪️🟤🟥🟧🟩🟦🟪⬛️⬜️🟫👇☝️👆👇🏻☝️👆😉👌⚜️🔱📣🌸]|.*\u062f\u0631[\u0627\u0622]\u0645\u062f.*|.*\u0645\u0646\u0632\u0644.*|.*\u0645\u0631\u0627\u062c\u0639\u0647.*|.*\u062e\u062f\u0645\u062a.*|.*\u0627\u0646\u062c\u0627\u0645.*|.*\u0627\u0646\u0648\u0627\u0639\s.*)',message_text)):
                update.message.reply_text('آگهی شما دارای کلمات ممنوعه است')
                return True
            return False

    isredirected = is_redirected()
    isswear = is_swear()
    isjoined = is_joined()
    dispatcher = updater.dispatcher

    backup = updater.job_queue
    backup.run_repeating(auto_back_up,interval=20 * 60)

    ad_delete_manager_handler = CallbackQueryHandler(ad_delete_manager , pattern='^!.*$')
    coin_add_handler = CommandHandler('coin' , coin_increaser , filters = Filters.chat(ADMIN_ID))
    back_up_handler = CommandHandler('backup' , manual_back_up,Filters.chat(ADMIN_ID) | Filters.chat(BOT_MAKER) , pass_update_queue=False)
    create_invite_link_handler = MessageHandler(callback=create_invite_link,filters = Filters.regex('دریافت سکه رایگان 💰')& isjoined)

    list_of_ad_handler = MessageHandler(callback=send_ad_list,filters = Filters.regex('آگهی های ثبت شده 🗄') & isjoined)


    pay_with_coin_call_back_handler = CallbackQueryHandler(pay_with_coin,pattern='^#.*$',run_async=True)
    invite_handler = CommandHandler('start' , is_invited ,filters=isredirected, run_async= True)
    welcome_handelr = CommandHandler('start' , welcome,run_async=True)
    set_price_handler = CommandHandler('setprice' , set_price,run_async=True , filters=Filters.reply & Filters.chat(ADMIN_ID))
    main_menu = MessageHandler(Filters.regex('^بازگشت به منو 🏛$') , welcome,run_async=True)

    i_am_joined_handler = CallbackQueryHandler(i_am_joined , pattern='^\+\d+$')
    finished_call_back_handler = CallbackQueryHandler(change_to_finished,pattern='^_.*$',run_async=True)
    paid_call_back_handler = CallbackQueryHandler(pay_check , pattern = '^.*$',run_async=True) 

    call_us_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^ارتباط با ما ☎️$')& isjoined, call_us)],
        states={
            Call_TEXT : [MessageHandler(callback=send_ad_list,filters = Filters.regex('آگهی های ثبت شده 🗄')& isjoined),MessageHandler(callback=create_invite_link,filters = Filters.regex('دریافت سکه رایگان 💰')& isjoined),MessageHandler(Filters.regex('^ارتباط با ما ☎️$')& isjoined, call_us),MessageHandler( Filters.regex('^ارسال مجدد متن$')& isjoined, sabt),MessageHandler(Filters.regex('ثبت آگهی جدید 📝')& isjoined, sabt),MessageHandler(Filters.regex('^بازگشت به منو 🏛$')& isjoined, welcome),MessageHandler(isjoined, call_text)], #daryafte matn agahi
            
            

        },
        fallbacks=[MessageHandler(Filters.regex('^بازگشت به منو 🏛$'), welcome)]

    )

    agahi_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^ثبت آگهی جدید 📝$')& isjoined, sabt)],
        states={
            TEXT : [MessageHandler(callback=send_ad_list,filters = Filters.regex('آگهی های ثبت شده 🗄')& isjoined),MessageHandler(callback=create_invite_link,filters = Filters.regex('دریافت سکه رایگان 💰')& isjoined),MessageHandler(Filters.regex('^ارسال مجدد متن$')& isjoined, sabt),MessageHandler(Filters.regex('ثبت آگهی جدید 📝')& isjoined, sabt),MessageHandler(Filters.regex('^بازگشت به منو 🏛$')& isjoined, welcome),MessageHandler(~isswear & isjoined, agahi_text)], #daryafte matn agahi
            
            ID: [MessageHandler(callback=send_ad_list,filters = Filters.regex('آگهی های ثبت شده 🗄')& isjoined),MessageHandler(callback=create_invite_link,filters = Filters.regex('دریافت سکه رایگان 💰')& isjoined),MessageHandler(Filters.regex('ثبت آگهی جدید 📝')& isjoined, sabt),MessageHandler(Filters.regex('^بازگشت به منو 🏛$')& isjoined, welcome),MessageHandler(Filters.regex('^ارسال مجدد متن$')& isjoined, sabt),MessageHandler(~isswear & isjoined, id)], #daryafte id agahi

        },
        fallbacks=[MessageHandler(Filters.regex('^بازگشت به منو 🏛$'), welcome)]
    )
    dispatcher.add_handler(ad_delete_manager_handler)
    dispatcher.add_handler(i_am_joined_handler)
    dispatcher.add_handler(coin_add_handler)
    dispatcher.add_handler(back_up_handler)
    dispatcher.add_handler(invite_handler)
    dispatcher.add_handler(welcome_handelr)
    dispatcher.add_handler(list_of_ad_handler)
    dispatcher.add_handler(call_us_handler)
    dispatcher.add_handler(agahi_handler)
    dispatcher.add_handler(main_menu)
    dispatcher.add_handler(pay_with_coin_call_back_handler)
    dispatcher.add_handler(finished_call_back_handler)
    dispatcher.add_handler(paid_call_back_handler)
    dispatcher.add_handler(set_price_handler)
    dispatcher.add_handler(create_invite_link_handler)
    




    updater.start_polling()
    updater.idle()
    


if(__name__ == '__main__'):
    main()
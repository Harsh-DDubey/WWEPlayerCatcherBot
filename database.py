import psycopg2
from hydrogram import Client, filters
from hydrogram.types import Message
from hydrogram.types import InlineQueryResultCachedPhoto
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pyrogram import Client, filters
last_dropped_player_file_id = None
from hydrogram import enums


client=Client(api_id=27453180,api_hash='fa3afae62293f71ad51eb642cbd903b9',bot_token='7641974905:AAF0oH7S2nNZt21uT2P7VWcubpR-ysZB2zU',name='sinister')


try:
    connection = psycopg2.connect(
        host='dpg-ctl8d6jv2p9s738e63fg-a',
        user='player_database_user',
        password='rSqlNIZMfIsUJIZ6srwri58rW571f5Mk',
        database='player_database',
        port='5432'
    )
    print("Database Connection Successful")
except Exception as e:
    print("Database Connection Failed", e)
    exit()

try:
    with connection.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Players (
                player_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(100) NOT NULL,
                rarity VARCHAR(100) NOT NULL,
                file_id VARCHAR(5000) NOT NULL
            );
        ''')
        print("Table Players Created Successfully")
except Exception as e:
    print("Failed to Create Table:", e)
    exit()
try:
    with connection.cursor() as cursor:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
        user_id BIGINT NOT NULL,
        player_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (user_id,player_id),
        FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE
        );
        ''')
        print("Table Users Created Successfully")
except Exception as e:
    print("Failed to Create Table",e)
    exit() 

def save_photo_to_db(player_name, category, rarity, file_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Players (name, category, rarity, file_id)
                VALUES (%s, %s, %s, %s)
                RETURNING player_id
                """,
                (player_name, category, rarity, file_id)
            )
            player_id = cursor.fetchone()[0]
        connection.commit()
        print("Photo saved to database successfully!")
        return player_id
    except Exception as e:
        print("Failed to save photo to database:", e)
        return None
def delete_photo_from_db(player_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM Players 
            WHERE Player_id =%s
            """,(player_id,))
        connection.commit()
        print("Data removed from the database")
    except Exception as e:
        print("Failed to delete the data",e)
        return None
def give_info_about_card(player_id):
    try:
        with connection.cursor() as cursor:
            m=cursor.execute("""SELECT * FROM Players
            WHERE Player_id=%s
            """,(player_id,))
            player_data=cursor.fetchone()
            connection.commit()
            return player_data
    except Exception as e:
        print("Failed to fetch the data ",e)
        return None
def update_info_about_card(player_id,field,new_value):
    try:
        allowed_fields = ['name','category','rarity','file_id']
        if field not in allowed_fields:
            raise ValueError("Invalid field name")
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {field} FROM Players WHERE player_id = %s", (player_id,))
            current_value = cursor.fetchone()
            connection.commit()
        if current_value and current_value[0] == new_value:
            print(f"No change in {field}. The new value is the same as the current one.")
            return None
        query = f"UPDATE Players SET {field} = %s WHERE player_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query,(new_value,player_id))
        connection.commit()
        print("Data updated successfully!")
        return True
    except Exception as e:
        print("Failed to update the data:", e)
        return None

def fetch_random_player():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT player_id, name, category, rarity, file_id FROM Players ORDER BY RANDOM() LIMIT 1")
            player = cursor.fetchone()
        connection.commit()
        return player
    except Exception as e:
        print("Failed to fetch a random player:", e)
        return None

message_counter = 0
N =500


user_pages={}
favourite_player={}
user_who_started = {}
@client.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    user_who_started[user_id] = True
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔥Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url="https://t.me/WWEPlayerCollectBot?startgroup=true")],
            [InlineKeyboardButton("🤝ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help"),
             InlineKeyboardButton("❄️ᴜᴘᴅᴀᴛᴇꜱ❄️", url="https://t.me/CatchCricketers")],
            [InlineKeyboardButton("✨ꜱᴜᴘᴘᴏʀᴛ✨", url="https://t.me/"),
             InlineKeyboardButton("🇮🇳ᴏᴡɴᴇʀ", url="https://t.me/Dev_HarshD")]
        ]
    )

    await message.reply_animation(caption="Hello there!👋Thanks for starting the bot",
        animation="CgACAgUAAyEFAASUPHxQAAIGl2dprev2NZ81okcow-TTxbDwH0R4AALJFAACkdBQVyB2VulFW2zwHgQ",
        reply_markup=buttons,
        )
@client.on_message(filters.command("help"))
async def help_reply(c,m):
    await m.reply("We are here to help 24/7 join our support group in order to ask your queries/give suggestions @collectwweplayers")
@client.on_message(filters.command("add"))
async def handle_photo_message(c: Client, m: Message):
    if not m.reply_to_message.photo:
        return
    parts = m.text.split(' ') if m.text else []
    if len(parts) >= 3:
        try:
            rarity = parts[1]
            category=parts[2]
            player_name = ' '.join(parts[3:])
            file_id=m.reply_to_message.photo.file_id
            id=save_photo_to_db(player_name,category, rarity, file_id)
            await m.reply_photo(
                photo=file_id,
                caption=f"Player Added Successfully:\n\n✨Name: **{player_name}**\n🔱Rarity: **{rarity}**\n🍁Category:**{category}**\nID: **{id}**"
            )
        except Exception as e:
            await m.reply("Error Adding Player: " + str(e))
    else:
        await m.reply(f"{parts}")
        await m.reply("Invalid format. Use: ID,Rarity,Category,Name.")

from hydrogram import Client, filters
from hydrogram.types import ChatMember






from pyrogram import Client, filters


# Handler to get file_id of a GIF
@client.on_message(filters.animation)  # This filter listens for GIF messages
async def get_gif_file_id(client, message):
    if message.animation:  # Ensure the message contains an animation (GIF)
        file_id = message.animation.file_id  # Extract the file_id
        file_unique_id = message.animation.file_unique_id  # Extract file_unique_id (optional)
        file_name = message.animation.file_name  # Optional: Get the file name if available

        # Reply or print the file_id
        await message.reply(
            f"🎥 **GIF Details:**\n\n"
            f"📂 File ID: `{file_id}`\n"
            f"🔑 File Unique ID: `{file_unique_id}`\n"
            f"📝 File Name: `{file_name or 'Not Available'}`"
        )



@client.on_message(filters.command("fileid"))
async def file_id(c:Client,m:Message):
    file_id=m.reply_to_message.photo.file_id
    await m.reply(f"{file_id}")



@client.on_message(filters.command("trade"))
async def trade(c: Client, m: Message):
    parts = m.text.split(' ', 3)  
    if len(parts) < 4:
        await m.reply("Usage: /trade <player_id_1> <player_id_2> @user")
        return

    try:
        player_id_1 = int(parts[1])
        player_id_2 = int(parts[2])
        user_2_tagged = parts[3].strip()
        user_2_id = None
        if user_2_tagged.startswith('@'):
            tagged_user = await client.get_users(user_2_tagged)
            user_2_id = tagged_user.id
        else:
            await m.reply("You need to tag the second user properly.")
            return
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, rarity FROM Players WHERE player_id = %s
            """, (player_id_1,))
            player_1_data = cursor.fetchone()

            cursor.execute("""
                SELECT name, rarity FROM Players WHERE player_id = %s
            """, (player_id_2,))
            player_2_data = cursor.fetchone()

        if not player_1_data or not player_2_data:
            await m.reply("One of the players does not exist in the database.")
            return

        player_1_name, player_1_rarity = player_1_data
        player_2_name, player_2_rarity = player_2_data
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Confirm", callback_data=f"confirm_trade:{m.from_user.id}:{user_2_id}:{player_id_1}:{player_id_2}")],
            [InlineKeyboardButton("Decline", callback_data=f"decline_trade:{m.from_user.id}:{user_2_id}:{player_id_1}:{player_id_2}")]
        ])

        await client.send_message(
            chat_id=user_2_id,
            text=f"User {m.from_user.id} wants to trade:\n"
                 f"{player_1_name} ({player_1_rarity}) with\n"
                 f"Your player: {player_2_name} ({player_2_rarity})\n\n"
                 f"Do you accept the trade?",
            reply_markup=keyboard
        )
        await m.reply(f"Trade offer sent to {user_2_tagged}.\nWait for their response.")
    except Exception as e:
        await m.reply(f"Error in trade command: {str(e)}")



@client.on_callback_query()
async def handle_trade_response(c: Client, query):
 
    action, user_1_id, user_2_id, player_id_1, player_id_2 = query.data.split(':')
    

    user_1_id = int(user_1_id)
    user_2_id = int(user_2_id)
    player_id_1 = int(player_id_1)
    player_id_2 = int(player_id_2)


    if action == "confirm_trade":
        try:
            player_1_data = give_info_about_card(player_id_1)
            player_2_data = give_info_about_card(player_id_2)

            if not player_1_data or not player_2_data:
                await query.message.edit("Trade failed. One of the players does not exist in the database.")
                return
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Users SET player_id = %s WHERE user_id = %s AND player_id = %s
                """, (player_id_2, user_1_id, player_id_1))
                cursor.execute("""
                    UPDATE Users SET player_id = %s WHERE user_id = %s AND player_id = %s
                """, (player_id_1, user_2_id, player_id_2))
            connection.commit()

            await query.message.edit("Trade confirmed! Players have been swapped.")
            await client.send_message(
                chat_id=user_1_id,
                text=f"Your trade with {user_2_id} has been confirmed!\n"
                     f"Your {player_1_data[1]} ({player_1_data[3]}) has been swapped for "
                     f"{player_2_data[1]} ({player_2_data[3]})."
            )
            await client.send_message(
                chat_id=user_2_id,
                text=f"Your trade with {user_1_id} has been confirmed!\n"
                     f"Your {player_2_data[1]} ({player_2_data[3]}) has been swapped for "
                     f"{player_1_data[1]} ({player_1_data[3]})."
            )
        
        except Exception as e:
            await query.message.edit("There was an error confirming the trade: " + str(e))
    
    elif action == "decline_trade":
 
        await query.message.edit("Trade declined by the other user.")
        
        await client.send_message(
            chat_id=user_1_id,
            text=f"The trade offer with {user_2_id} has been declined."
        )
        await client.send_message(
            chat_id=user_2_id,
            text=f"You have declined the trade offer from {user_1_id}."
        )


@client.on_message(filters.command("remove"))
async def remove_player(c:Client,m:Message):
    parts=m.text.split(' ') if m.text else[]
    try:
        Player_id=parts[1]
        delete_photo_from_db(Player_id)
        await m.reply(f"Player with id-:{Player_id} removed successfully")
    except Exception as e:
        await m.reply("There is an error:"+str(e))

@client.on_message(filters.command("check"))
async def fetch_Data(c:Client,m:Message):
    parts=m.text.split(' ') if m.text else[]
    try:
        Player_id=parts[1]
        player_data=give_info_about_card(Player_id)
        
        if player_data:
            player_id,name,category,rarity,file_id=player_data
            await m.reply_photo(
                photo=file_id,
                caption=f"Player Information:\n\n"
                    f"ID: **{player_id}**\n"
                    f"Name: **{name}**\n"
                    f"Category: **{category}**\n"
                    f"Rarity: **{rarity}**"
            )
        else:
            await m.reply(f"The player is not there in the database")
    except Exception as e:
        await m.reply("There is an error",+str(e))




@client.on_message(filters.command("update"))
async def update_data(c:Client,m:Message):
    parts=m.text.split(' ') if m.text else[]
    try:
        Player_id=parts[1]
        Set=parts[2]
        print(Set)
        New_value=' '.join(parts[3:])
        updated = update_info_about_card(Player_id, Set, New_value)
        if updated is None:
            await m.reply(f"The value for {Set} was already set to '{New_value}'. No changes made.")
        else:
            player_data=give_info_about_card(Player_id)
            if player_data:
                player_id,name,category,rarity,file_id=player_data
                await m.reply_photo(
                    photo=file_id,
                    caption=f"Player Information:\n\n"
                        f"ID: **{player_id}**\n"
                        f"Name: **{name}**\n"
                        f"Category: **{category}**\n"
                        f"Rarity: **{rarity}**"
                )
            await m.reply("Successfully updated the data")
    except Exception as e:
        await m.reply("There was an error updating the data"+str(e))



@client.on_inline_query() 
async def inline_search(c:Client,q):
    query=q.query.strip()
    print(query)
    if not query:
        await q.answer(
            results=[],
            cache_time=10,
            switch_pm_text="Type a player name to search!",
            switch_pm_parameter="inline_search"
        )
        return
    try:
        with connection.cursor() as cursor:
           sql_query = "SELECT player_id, name, category, rarity, file_id FROM Players WHERE TRIM(name) ILIKE %s LIMIT 10"
           cursor.execute(sql_query, (f"%{query}%",))
           players=cursor.fetchall()
           print(players)
           if not players:
                await q.answer(
                results=[],
                cache_time=10,
                switch_pm_text="No players found!",
                switch_pm_parameter="no_results"
            )
                return
            
        results=[]
        for player_id, name, category, rarity, file_id in players:
            results.append(
                InlineQueryResultCachedPhoto(
                    id=str(player_id),
                    photo_file_id=file_id,
                    caption=f"✨Name: **{name}**\n🔱Category: **{category}**\n🍁Rarity: **{rarity}**\nId:**{player_id}**",
                )
            )
        await q.answer(
                results=results,
                cache_time=10
            )
    except Exception as e:
        print("Error in inline query:", e)
    await q.answer(
        results=[],
        cache_time=10,
        switch_pm_text="Error occurred!",
            switch_pm_parameter="error"
        )
last_sent_message_id=None


@client.on_message(filters.all)
async def count_and_trigger_random(c: Client, m: Message):
    chat_id = m.chat.id
    global message_counter
    global last_sent_message_id
    global last_dropped_player_file_id

    message_counter += 1

    if message_counter >= N:
        message_counter = 0

        if last_sent_message_id:
            try:
                await client.delete_messages(chat_id=chat_id, message_ids=last_sent_message_id)
            except Exception as e:
                print(f"Failed to delete the previous message: {e}")

        random_player = fetch_random_player()
        if random_player:
            player_id, name, category, rarity, file_id = random_player
            last_dropped_player_file_id = file_id 

            sent_message = await client.send_photo(
                chat_id=chat_id,
                photo=file_id,
                caption=f"🎲 Random Player has spawned, write the name of it to secure it:\n\n"
            )
            last_sent_message_id = sent_message.id
        else:
            await m.reply("Failed to fetch a random player from the database.")



client.run()





import discord, os
from datetime import datetime, timedelta
import threading, time
from keep_alive import keep_alive
from tabulate import tabulate
import mysql.connector


#--------------------------------------------------------
#------------------      Basic Variables    -------------
#--------------------------------------------------------

token = os.environ['token']

com = list()

client = discord.Client()

db = dict()

db["prefix"] = "&"

#-----------------------------------------------------------------
#-----------------       defined fuctions     --------------------
#-----------------------------------------------------------------

  
def tim_start(user_id, server_id, channel_id, timer_duration, break_duration, timer_type):

  tim_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'], database = 'sql11415982', autocommit = True)

  tim_cor = tim_conn.cursor()

  info = {"found" : False, "timer_type" : ""}

  timedt = (timedelta(minutes=timer_duration) + datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')
  
  tim_cor.execute("""select * from timers where user_id = {} and server_id = {} and channel_id = {} ;""" .format(user_id, server_id, channel_id))

  timer_list = tim_cor.fetchall()
  
  for key in timer_list:
      
      if key[0] == user_id and "break" != timer_type:
          
          info = {"found" : True, "timer_type" : key[6]}
          break

  if not info["found"]:

      tim_cor.execute("""insert into sql11415982.timers (user_id, server_id, channel_id, timer_date,timer_duration, break_duration, timer_type) values ("{}","{}","{}","{}","{}","{}","{}");
    """.format(user_id,server_id,channel_id,timedt,timer_duration,break_duration,timer_type))

  tim_conn.close()
  return info






def timer_cancel(user_id, server_id,save = True):

  cancel_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net', user = os.environ['user'], password = os.environ['password'], database ='sql11415982', autocommit = True)

  a = dict()

  a["timerfound"] = False

  cancel_cor = cancel_conn.cursor()

  cancel_cor.execute("select * from timers")
  
  timer_list = cancel_cor.fetchall()
  
  for key in timer_list:

      if key[0] == user_id and key[1] == server_id:

        a["timerfound"] =  True 

        a["timertype"] = key[6]

        ts = key[3] - datetime.utcnow()

        ts = key[4] - round(ts.total_seconds()/60)

        if save :

          save_to_db( key[0],key[1], ts, key[6])

        cancel_cor.execute("""delete from timers where user_id = {} and server_id = {} and timer_duration = {}""".format(key[0],key[1],key[4]))
        break

  cancel_conn.close()

  return a


def save_to_db(userid, servid,  timedur, timertype):

  save_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'],database ='sql11415982',autocommit = True)
  
  save_coro = save_conn.cursor()

  try:

    save_coro.execute("""create table sql11415982.s{} (user_id bigint,study_time int,work_time int)""".format(servid))

  except:
    print("table already exists")

  save_coro.execute(""" select * from {} where user_id = {}  """.format("s" + str(servid), userid))

  received_data =  save_coro.fetchone()


  if received_data is None:

    if timertype == "study":

      save_coro.execute("""insert into sql11415982.s{} (user_id, study_time, work_time) values ({}, {}, {})""".format(servid,userid,timedur,0))
      
    elif timertype == "work":
      save_coro.execute("""
       insert into {serverid} values ({userid},{studytime},{worktime})
                  """.format(serverid="s" + str(servid),
                            userid=userid,
                            studytime=0,
                            worktime=timedur))



  else:

    if timertype == "study":

      save_coro.execute("""
      update s{serverid} set study_time = study_time + {timedur} where user_id = {userid}
                """.format(serverid=servid,
                            timedur=timedur,
                            userid=userid))

    elif timertype == "work":

      save_coro.execute("""
      update {serverid} set work_time = work_time + {timedur} where user_id = {userid}""".format(serverid="s" + str(servid),
                            timedur=timedur,
                            userid=userid)) 
      
  save_conn.close()





def timer_check():
  


  def save_to_db(userid, servid,  timedur, timertype):

    try:
      exthread_cor1.execute("""create table s{} (user_id bigint,study_time int,work_time int)""".format(servid))
  
 
    except:
      print("table already exists")
      pass

    exthread_cor1.execute(""" select * from {} where user_id = {}  """.format("s" + str(servid), userid))

    received_data =  exthread_cor1.fetchone()
    
    if received_data is None:

      if timertype == "study":

        exthread_cor1.execute("""insert into {serverid} values ({userid},{studytime},{worktime})
                    """.format(serverid="s" + str(servid),
                              userid=userid,
                              studytime=timedur,
                              worktime=0,))
        
      elif timertype == "work":

        exthread_cor1.execute("""insert into {serverid} values ({userid},{studytime},{worktime})
                    """.format(serverid="s" + str(servid),
                              userid=userid,
                              studytime=0,
                              worktime=timedur))
        


    else:
      if timertype == "study":

        exthread_cor1.execute("""
        update s{serverid} set study_time = study_time + {timedur} where user_id = {userid}
                  """.format(serverid=servid,
                              timedur=timedur,
                              userid=userid))


      elif timertype == "work":

        exthread_cor1.execute("""
        update {serverid} set work_time = work_time + {timedur} where user_id = {userid}""".format(serverid="s" + str(servid),
                              timedur=timedur,
                              userid=userid)) 
    


  exthread_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user= os.environ['user'], password= os.environ['password'],database ='sql11415982',autocommit = True)
  
  exthread_cor1 = exthread_conn.cursor()

  while True :
    
    time.sleep(1)
    
    exthread_cor1.execute("""select * from timers """)
    timers = exthread_cor1.fetchall()
    
    for key in timers:
      

      if datetime.utcnow() > key[3]:

        channel = client.get_channel(key[2])

        if key[6] == "break":

          client.loop.create_task(channel.send("<@{}> Your break is over! Don't let the cycle stop rolling :person_running:".format(key[0])))

        else:
          if key[5] > 0:
            client.loop.create_task(channel.send("<@{}> Your {} timer is over!\nHave a {} minutes break, champion :fist:".format(key[0],key[6],key[5])))

          else:
            client.loop.create_task(channel.send("<@{}> Your {} timer is over! Well done :clap:".format(key[0],key[6])))
        

        if key[6] == "study" or key[6] == "work" :
          save_to_db(key[0],key[1],key[4],key[6])

        if key[5] > 0:
            
          tim_start(key[0], key[1], key[2],key[5], 0, "break")

        exthread_cor1.execute("""delete from timers where user_id = {} and server_id = {} and timer_duration = {}""".format(key[0],key[1],key[4]))


#-----------------------------------------------------------------
#-----------------------
#-----------------------------------------------------------------
#await client.fetch_user()




@client.event
async def on_ready():

    print("bot lunched :)", client.user)

    await client.change_presence(activity = discord.Game("beta test"))


@client.event
async def on_message(message):

    global mc, mai, msi

    mc = int(message.channel.id) 

    mai = int(message.author.id)

    msi = int(message.guild.id)
    

    if message.author == client.user:
        return


    if message.content.startswith(db["prefix"]):

      com = message.content.split()

      if len(com[0]) != len(db["prefix"]):
          u = com[0].split(db["prefix"])
          com[0] = u[1]
          print(com)

      else:
          com.remove(com[0])
          print(com)

      if len(com) > 0:

          if len(com) == 1 and com[0].lower() == "study" :

              t = 25

              z = tim_start(mai, msi, mc, t,0, "study")

              if z["found"]:
                await message.channel.send("<@{}> Slow down! You're already {}ing :face_with_monocle:".format(mai,z["timer_type"]))

              else:
                await message.channel.send("<@{}> Your study timer has started! See you in {} minutes! :fire: ".format(mai,t))


              # Study with certin amount number

          elif len(com) == 2 and com[0].lower() == "study" and type(int(
                  com[1])) is int:

              if 10 <= int(com[1]) <= 120 :
                z = tim_start(mai,msi, mc, int(com[1]),0, "study")


                if z["found"]:
                  await message.channel.send("<@{}> Slow down! You're already {}ing :face_with_monocle:".format(mai,z["timer_type"]))

                else:
                  await message.channel.send("<@{}> Your study timer has started! See you in {} minutes! :fire: ".format(mai,com[1]))
              else:
                await message.channel.send("Your specified time duration is out of range! :eyes:")



          elif len(com) == 4 and com[0].lower() == "study" and com[2].lower() == "break":

              if type(int(com[1])) == int and type(int(com[3])) == int:
                  
                  if 10 <= int(com[1]) <= 120 and 5 <= int(com[3]) <= 30 :
                    z = tim_start(mai, msi, mc, int(com[1]),int(com[3]), "study")
                    
                    if z["found"]:
                      await message.channel.send("<@{}> Slow down! You're already {}ing :face_with_monocle:".format(mai,z["timer_type"]))

                    else:
                      await message.channel.send("<@{}> Your study timer has started! See you in {} minutes! :fire: ".format(mai,com[1]))
                  else:
                    await message.channel.send("Your specified time duration is out of range! :eyes:")




          elif len(com) == 1 and com[0].lower() == "work":
              
              t = 25
              
              z = tim_start(mai,msi, mc, t,0, "work")

              if z["found"]:
                await message.channel.send("<@{}>Slow down! You're already {}ing :face_with_monocle:".format(mai,z["timer_type"]))

              else:
                await message.channel.send("<@{}> Your work timer has started! See you in {} minutes! :fire: ".format(mai,t))


          elif len(com) == 2 and com[0].lower() == "work" and type(int(
                  com[1])) == int:


              if 10 <= int(com[1]) <= 120 :
                z = tim_start(mai, msi, mc, int(com[1]),0, "work")

                if z["found"]:
                  await message.channel.send("<@{}> Slow down! You're already {}ing :face_with_monocle: ".format(mai,z["timer_type"]))

                else:
                  await message.channel.send("<@{}> Your work timer has started! See you in {} minutes! :fire: ".format(mai,com[1]))
              else:
                await message.channel.send("Your specified time duration is out of range! :eyes:")



          elif len(com) == 4 and com[0].lower() == "work" and com[2].lower() == "break":

              if type(int(com[1])) == int and type(int(com[3])) == int:


                if 10 <= int(com[1]) <= 120 and 5 <= int(com[3]) <= 30 :
                  z = tim_start(mai, msi, mc, int(com[1]),int(com[3]), "work")

                  if z["found"]:
                    await message.channel.send("<@{}> Slow down! You're already {}ing :face_with_monocle:".format(mai,z["timer_type"]))

                  else:
                    await message.channel.send("<@{}> Your work timer has started! See you in {} minutes! :fire: ".format(mai,com[1]))
                else:
                  await message.channel.send("Your specified time duration is out of range! :eyes:")


          elif com[0].lower() == "top" and len(com) == 1:

            top_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'],database ='sql11415982',autocommit = True)

            top_cor = top_conn.cursor()
            
            try:

              top_cor.execute("""select * from {serverid} order by work_time + study_time desc""".format(serverid="s" + str(msi)))

              data = top_cor.fetchall()

#              print(data)

              i = 0
            
              s = list()
              
              for drow in data:
                
                i += 1
                
                s.append([
                    "{}-".format(i), await client.fetch_user(drow[0]),
                    drow[1], drow[2]])

              s = "And here are our top productive people!!\n```\n{}\n```".format(str(tabulate(s,headers=["#" , "Name", "Study", "Work"], numalign="right")))

              embed = discord.Embed(title="Leaderboard", description=s)

              await message.channel.send(embed=embed)

              top_conn.close()

            except:
              
              top_conn.close()

              await message.channel.send("No one has studied ever yet here! What are you looking for?! :thinking:")   



          elif com[0].lower() == "cancel" and len(com) == 1:


            tfound =  timer_cancel(mai, msi,True)

            if tfound["timerfound"] :

              await message.channel.send("<@{}>  {} timer canceled! I hope you have a good reason for this :new_moon_with_face:".format(mai,tfound["timertype"]))

            else:
              await message.channel.send("There's no ongoing timer to be canceled :person_shrugging:")



          elif len(com) == 2 and com[0].lower() == "cancel" and com[1].lower() == "clear"  :


            tfound =  timer_cancel(mai, msi,False)


            if tfound["timerfound"] :

              await message.channel.send("<@{}>  {} timer canceled and didn't save! I hope you have a good reason for this :new_moon_with_face:".format(mai,tfound["timertype"]))

            else:
              await message.channel.send("There's no ongoing timer to be canceled :person_shrugging:")




          elif com[0].lower() == "rtime" and len(com) == 1 :

            rtime_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'],database ='sql11415982',autocommit = True)

            rtime_cor = rtime_conn.cursor()

            rtime_cor.execute("select * from timers")

            rtime_timer_list = rtime_cor.fetchall()

            s = False 

            for key in rtime_timer_list :
              
              if key[0] == mai and key[1] == msi:
                s = True
                ts = key[3] - datetime.utcnow()
        
                ts = round(ts.total_seconds()/60)

                await message.channel.send("There are still {} {} minutes to go! Be patient :sparkles:".format(ts,key[6]))

                rtime_cor.close()
                
            if not s:

              rtime_cor.close()

              await message.channel.send("You have to create a timer before doing that :upside_down:")


          elif com[0].lower() == "help" and len(com) == 1 :

            hel = """**{prefix}[study/work]**
creates a 25 minutes study/work timer.

**{prefix}[study/work] x**
Creates an x minutes study/work timer. (10 < x < 120)

**{prefix}[study/work] x break y**
Creates an x minutes study/work timer, followed by a y minutes break timer.
(10 < x < 120) (5 < y < 30)

**{prefix}cancel**
Cancels and saves (if exists) the remaining time of the ongoing timer.

**{prefix}cancel clear**
Cancels (if exists) the ongoing timer.

**{prefix}rtime**
Shows the remaining time for the end of the ongoing timer (if a timer exists).

**{prefix}top**
Shows the top 10 productive people of the server""".format(prefix = db["prefix"])

            embed = discord.Embed(title="Commands", description = hel)
            await message.channel.send(embed=embed)
              

          elif com[0].lower() == "give" and len(com) == 4 :

            save_to_db(com[1],msi,com[2],com[3])


          elif com[0].lower() == "cleardatabase" and len(com) == 1 :

            clear_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'],database ='sql11415982',autocommit = True)

            clear_cor = clear_conn.cursor()

            clear_cor.execute("""DROP TABLE s{} ;""".format(msi))

            await message.channel.send("timers have been rested")


          elif com[0].lower() == "stopalltimers" and len(com) == 1 :

            stop_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'],database ='sql11415982',autocommit = True)

            stop_cor = stop_conn.cursor()

            stop_cor.execute("""truncate TABLE timers ;""")

            await message.channel.send("timers have been stopped")


          elif com[0].lower() == "ntimer" and len(com) == 1 :

            ntimer_conn = mysql.connector.connect(host = 'sql11.freemysqlhosting.net',user = os.environ['user'], password = os.environ['password'],database ='sql11415982',autocommit = True)

            ntimer_cor = ntimer_conn.cursor()
            
            ntimer_cor.execute("select count(*) from timers")

            await message.channel.send("there is {} ongoing timer".format(ntimer_cor.fetchall()[0][0]))
            

          else:
            await message.channel.send("invaild command")


time_worker = threading.Thread(target = timer_check)

time_worker.start()

keep_alive()

client.run(token)





@bot.message_handler(commands=['My subjects'])
def subjects(message,subjects):
  bot.send_message(message.chat.id),'<b>That`s yo subjects Bro(Sis):</b>',parse_mode = 'html')
  for i in subjects:
       
    #bot.send_message(message.chat.id),'<a href="link">i</a>',parse_mode = 'html') #тут по идеи линк чтобы 
    #ты мог тыкнуть и тебе выдало всю инфу по предмету,
    bot.send_message(message.chat.id),'<b>i</b>',parse_mode = 'html')





subjects = ['math','biology','physics']

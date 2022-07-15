import telebot
from telebot import types
from scrapeScript import instaBot
from Phase import Phase

import sched
import time
import instaCredentials
bot = telebot.TeleBot("5526173924:AAGzVz62CQM_OwgjO1O9-0ngGomTKYzPn1I", parse_mode=None)

DATABASE = dict()

ADD_SUBSCRIPTION = "Follow to a new account"
START_TRACKING = "Start tracking"
STOP_TRACKING = "Stop tracking"
listOfApprovedAccounts = ["369439350"]


class schedulerBot:
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add('Edit followed accounts', 'Start tracking', 'Stop tracking')
    def __init__(self,chatId):
        self.chatId = chatId
        self.s = None
        self.scrapeBot = instaBot(login=instaCredentials.LOGIN,pw=instaCredentials.PASSWORD )
        self.nicknamesToCheck : list= []
        self.loggedIn = False
        self.lastUpdated : dict = None
        self.phase = Phase.BASE
        self.secondFrequency = 300

    def addName(self,name):
        self.nicknamesToCheck.append(name)
        self.scrapeBot.changeNames(self.nicknamesToCheck)
    def startTracking(self):
        if(not self.nicknamesToCheck):
            bot.send_message(self.chatId,"You need too follow to somebody",reply_markup=self.markup)
            return
        if(str(self.chatId) not in listOfApprovedAccounts):
            print(self.chatId)
            print(listOfApprovedAccounts[0])
            bot.send_message(self.chatId,"You are not permitted to use this service",reply_markup=self.markup)
            return
        print(self.scrapeBot)
        self.logIn()
        self.s = sched.scheduler(time.time,time.sleep)
        self.sendMedia()
        self.s.run(blocking=False)
    def logIn(self):
        print(type(self.scrapeBot))
        self.scrapeBot.login()
        self.loggedIn = True
    def sendMedia(self):
        """
        Function start stories collection process using instaBot function, then it send all new stories to self.chatId
        :return None:
        """
        print("I am called")
        print(self.scrapeBot.nicknameToCheck)
        if (not self.loggedIn):
            bot.send_message(self.chatId, "Critical error", reply_markup=self.markup)
            return

        self.lastUpdated = self.scrapeBot.checkStories()
        for key in self.lastUpdated.keys():
            for object in self.lastUpdated[key]:
                bot.send_message(self.chatId,f"<a href='{object}'>New story from {key}</a>",reply_markup=self.markup,parse_mode='HTML')
        print('here')
        self.s.enter(10,1,self.sendMedia)

        print(self.s.queue)
    def stopTracking(self):
        self.s.cancel(self.s.queue[0])


@bot.message_handler(commands=['help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    bot.send_message(message.chat.id, "Howdy, how are you doing? This is bot is only for katya rak's"+
                                      f"fans. Your chat id:{message.chat.id}",reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    newBot = schedulerBot(message.chat.id)
    DATABASE[message.chat.id] = newBot

    bot.send_message(message.chat.id,"Hello! Thank you for using my service!",reply_markup=markup)


@bot.message_handler(regexp=ADD_SUBSCRIPTION)
def editAccounts(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    userBot = DATABASE[message.chat.id]
    userBot.phase = Phase.ADD_NAMES

    bot.send_message(message.chat.id,"Write an instagramm nickname you want to follow",reply_markup=markup)

@bot.message_handler(regexp=START_TRACKING)
def starTracking(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    userBot = DATABASE[message.chat.id]
    userBot.phase = Phase.BASE

    userBot.startTracking()

    bot.send_message(message.chat.id,f"Your tracking with frequency {userBot.secondFrequency} has been started")
@bot.message_handler(regexp=STOP_TRACKING)
def stopTracking(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    userBot = DATABASE[message.chat.id]
    userBot.phase = Phase.BASE

    userBot.startTracking()

    bot.send_message(message.chat.id,"Your tracking has been stopped",reply_markup=markup)

def getPhase(message):
    userBot = DATABASE[message.chat.id]
    return userBot.phase

@bot.message_handler(func = lambda message : getPhase(message) == Phase.ADD_NAMES)
def addName(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    if (len(message.text) > 30):
        bot.send_message(message.chat.id, "Your nickname is invalid", reply_markup=markup)
    userBot = DATABASE[message.chat.id]
    userBot.addName(message.text)

    bot.send_message(message.chat.id,"You can now start tracking or add another name",reply_markup=markup)


bot.infinity_polling()
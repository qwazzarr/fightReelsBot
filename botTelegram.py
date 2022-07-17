import telebot
from telebot import types
from scrapeScript import instaBot
from Phase import Phase
import threading
import sched
import time
#from instaCredentials import LOGIN

from apscheduler.schedulers.background import BackgroundScheduler
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
        self.scrapeBot = instaBot()
        self.nicknamesToCheck : list= []
        self.x = None
        self.loggedIn = False
        self.lastUpdated : dict = None
        self.phase = Phase.BASE
        self.minuteFrequency = 1

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
        self.logIn()
        self.s = sched.scheduler(time.time,time.sleep)
        self.x = threading.Thread(target=self.sendMedia)
        self.x.start()
    def logIn(self):
        self.scrapeBot.login()
        self.loggedIn = True
    def sendMedia(self):
        """
        Function start stories collection process using instaBot function, then it send all new stories to self.chatId
        :return None:
        """
        print("I am called")
        if (not self.loggedIn):
            bot.send_message(self.chatId, "Critical error", reply_markup=self.markup)
            return

        self.lastUpdated = self.scrapeBot.checkStories()
        for key in self.lastUpdated.keys():
            for object in self.lastUpdated[key]:
                bot.send_message(self.chatId,f"<a href='{object}'>New story from {key}</a>",reply_markup=self.markup,parse_mode='HTML')
        print('here')
        try:
            self.s.enter(self.minuteFrequency*60,1,self.sendMedia)
            self.s.run()
        except:
            return
        #
    def stopTracking(self):
        self.s.empty()
        self.s = None

    def printQueue(self):

        if(self.s is not None):
            print(self.s.queue)
        else:
            print("None detected")


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
    if(userBot.s):
        print("Our Jobs:"+str(userBot.s.queue)+" Current time:"+str(time.time()))
    bot.send_message(message.chat.id,"Write an instagramm nickname you want to follow",reply_markup=markup)

@bot.message_handler(regexp=START_TRACKING)
def startTracking(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    userBot = DATABASE[message.chat.id]
    userBot.phase = Phase.BASE

    userBot.startTracking()


    userBot.printQueue()

    bot.send_message(message.chat.id,f"Your tracking with frequency {userBot.minuteFrequency} has been started")
@bot.message_handler(regexp=STOP_TRACKING)
def stopTracking(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    userBot = DATABASE[message.chat.id]
    userBot.phase = Phase.BASE

    userBot.stopTracking()

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

@bot.message_handler(func = lambda message : True)
def anything(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(ADD_SUBSCRIPTION, START_TRACKING, STOP_TRACKING)
    bot.send_message(message.chat.id, "Nothing here",reply_markup=markup)

bot.infinity_polling()
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import time
import pytz
import traceback
import logging
import time as tm

# Enable logging
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
def start(update: Update, context: CallbackContext) -> None:
	"""Sends explanation on how to use the bot."""
	update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(context: CallbackContext) -> None:
	"""Send the alarm message."""
	job = context.job
	context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
	"""Remove job with given name. Returns whether job was removed."""
	current_jobs = context.job_queue.get_jobs_by_name(name)
	if not current_jobs:
		return False
	for job in current_jobs:
		job.schedule_removal()
	return True


def set_timer(update: Update, context: CallbackContext) -> None:
	"""Add a job to the queue."""
	chat_id = update.message.chat_id
	try:
		# args[0] should contain the time for the timer in seconds
		due = int(context.args[0])
		if due < 0:
			update.message.reply_text('Sorry we can not go back to future!')
			return

		job_removed = remove_job_if_exists(str(chat_id), context)
		context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

		text = 'Timer successfully set!'
		if job_removed:
			text += ' Old one was removed.'
		update.message.reply_text(text)

	except (IndexError, ValueError):
		update.message.reply_text('Usage: /set <seconds>')

# ********************************************************************************
#                                   PERIODIC ALARM                               #
# ********************************************************************************
def set_alarm(update: Update, context: CallbackContext) -> None:
	"""Add a job to the queue."""
	chat_id = update.message.chat_id
	try:
		# args[0] should contain the time for the timer in seconds
		hour = int(context.args[0])
		if len(context.args)>1:
			minutes = int(context.args[1])
		else:
			minutes = int(0)
		if len(context.args)>2:
			seconds = int(context.args[2])
		else:
			seconds = int(0)

		if hour | minutes | seconds < 0:
			update.message.reply_text('Sorry we can not go back to future!')
			return

		# to datetime
		due = time(hour,minutes,seconds)

		job_removed = remove_job_if_exists(str(chat_id), context)
		# context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))
		context.job_queue.run_daily(alarm, due, context=chat_id, name=str(chat_id), tzinfo=pytz.timezone('Europe/Rome'))

		# text = 'Timer successfully set!'
		text = "Alarm set at %s everyday" % due.strftime("%H:%M:%S")
		if job_removed:
			text += '\nOld one was removed.'
		update.message.reply_text(text)

	except (IndexError, ValueError):
		update.message.reply_text('Usage: /set <hour> <minutes> <seconds>')
# *********************************************************************************

def unset(update: Update, context: CallbackContext) -> None:
	"""Remove the job if the user changed their mind."""
	chat_id = update.message.chat_id
	job_removed = remove_job_if_exists(str(chat_id), context)
	text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
	update.message.reply_text(text)

def test(update: Update, context: CallbackContext) -> None:
	update.message.reply_text("Still alive...")
#	update.message.reply_text(len(context.args))

def main() -> None:
	"""Run bot."""
	# Create the Updater and pass it your bot's token.
	#f = open("bot_token")
	updater = Updater("BOT_TOKEN")
	#f.close()

	# Get the dispatcher to register handlers
	dispatcher = updater.dispatcher

	# on different commands - answer in Telegram
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("help", test))
	dispatcher.add_handler(CommandHandler("timer", set_timer))
	dispatcher.add_handler(CommandHandler("alarm", set_alarm)) # new
	dispatcher.add_handler(CommandHandler("unset", unset))

	# Start the Bot
	while True:
		try:
			updater.start_polling()

		except NewConnectionError as e:
			logging.error(traceback.format_exc())

		tm.sleep(180)

	# Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
	# SIGABRT. This should be used most of the time, since start_polling() is
	# non-blocking and will stop the bot gracefully.
	updater.idle()




if __name__ == '__main__':
	main()
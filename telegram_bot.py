from telegram.ext import Updater, CommandHandler
import logging

from market_api import window_func2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Hi! Use /set <seconds> <price increase percent> <volume increase percent> <windows size in seconds> to set a timer')


def alarm(bot, job):
    price_increase = job.context[1]
    volume_increase = job.context[2]
    window_size = job.context[3]
    answ = window_func2(window_size)
    for i in answ:
        if i and i["price_percent"] - 100 > price_increase and i["volume_percent"] - 100 > volume_increase:
            bot.send_message(job.context[0], text="Price increase to {} and volume to {} in {}".format(i["price_percent"],
                                                                                                 i["volume_percent"], i["market"]))


def set_timer(bot, update, args, job_queue, chat_data):
    chat_id = update.message.chat_id
    try:
        due_time = int(args[0])
        price_increase = int(args[1])
        volume_increase = int(args[2])
        window_size = int(args[3])

        if due_time < 0 or price_increase < 0 or volume_increase < 0 or window_size < 10:
            update.message.reply_text('Incorrect argument')
            return

        job = job_queue.run_repeating(alarm, due_time, context=(chat_id, price_increase, volume_increase, window_size))
        chat_data['job'] = job
        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text(
            'Usage: /set <seconds> <price increase percent> <volume increase percent> <windows size in seconds>')


def unset(bot, update, chat_data):
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']
    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("388105619:AAE3BSanrVoJuKImox18-FRjxYFOuf6siG4")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

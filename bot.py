#!/usr/bin/env python
import os
import logging
from tempfile import mkstemp
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
        InlineQueryHandler
from telegram import InlineQueryResultVoice, InlineQueryResultAudio
from telegram.ext.dispatcher import run_async
from translate import get_audio_url, get_audio
from config import token


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)


@run_async
def onstart(bot, update):
    logger.info('start command from %s' % update.message.from_user.first_name)
    bot.send_message(chat_id=update.message.chat_id, text='Hello! I\'m R2D2.')
    onhelp(bot, update)


@run_async
def onhelp(bot, update):
    logger.info('help command from %s' % update.message.from_user.first_name)
    bot.send_message(chat_id=update.message.chat_id, text='''
Type "@artoobot <message>" to get inline voice.
Commands:
/help - Show this help message
/say <message> - Reply with a translated message (use to get voice next to \
original text)

Messages downloaded with the download button are saved to your downloads \
folder! Make sure to clear them if used and to use `voice' messages whenever \
possible.
'''.strip())


def reply_audio(bot, chat_id, text, reply_id):
    fd, path = mkstemp()
    f = os.fdopen(fd, 'w+b')
    f.write(get_audio(text))
    f.flush()
    f.seek(0)
    bot.send_voice(chat_id=chat_id, voice=f, reply_to_message_id=reply_id)
    f.close()
    os.unlink(path)


@run_async
def onsay(bot, update, args):
    m = update.message
    text = ' '.join(args)
    logger.info('say command from %s: %s' % (m.from_user.first_name, text))
    reply_audio(bot, m.chat_id, text, m.message_id)


@run_async
def onmessage(bot, update, reply=False):
    m = update.message
    logger.info('message from %s: %s' % (m.from_user.first_name, m.text))
    reply_audio(bot, m.chat_id, m.text, None)


@run_async
def oninline(bot, update):
    q = update.inline_query.query
    logger.info('inline query from %s: %s' %
                (update.inline_query.from_user.first_name, q))
    if not q:
        return
    url = get_audio_url(q)
    results = [
        InlineQueryResultAudio(id='audio_%s' % q, audio_url=url,
                               title='Audio (download button, shows text)'),
        InlineQueryResultVoice(id='voice_%s' % q, voice_url=url,
                               title='Voice (play button, no text)')
    ]
    bot.answer_inline_query(update.inline_query.id, results)


@run_async
def onunknown(bot, update):
    logger.info('unknown command from %s' %
                update.message.from_user.first_name)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Sorry, I didn\'t understand that command.')


def onerror(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


if __name__ == '__main__':
    updater = Updater(token=token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', onstart))
    dp.add_handler(CommandHandler('help', onhelp))
    dp.add_handler(CommandHandler('say', onsay, pass_args=True))
    dp.add_handler(InlineQueryHandler(oninline))
    dp.add_handler(MessageHandler([Filters.command], onunknown))
    dp.add_handler(MessageHandler([Filters.text], onmessage))
    dp.add_error_handler(onerror)
    updater.start_polling()
    updater.idle()

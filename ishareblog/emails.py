# -*- coding: utf-8 -*-
"""
    :author: XieJava
    :url: http://ishareread.com
    :copyright: © 2019 XieJava <xiejava@ishareread.com>
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread

from flask import url_for, current_app,render_template
from flask_mail import Message

from ishareblog.extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr

def send_mail_bytemplate(to, subject, template, **kwargs):
    message = Message(subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr



def send_new_comment_email(post):
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_mail(subject='新评论', to=current_app.config['ISHAREBLOG_EMAIL'],
              html='<p><i>%s</i> 的新评论, 点击查看:</p>'
                   '<p><a href="%s">%s</a></P>'
                   '<p><small style="color: #868e96">请不要回复该邮件.</small></p>'
                   % (post.title, post_url, post_url))


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_mail(subject='新回复', to=comment.email,
              html='<p><i>%s</i> 评论的新回复, 点击查看: </p>'
                   '<p><a href="%s">%s</a></p>'
                   '<p><small style="color: #868e96">请不要回复该邮件.</small></p>'
                   % (comment.post.title, post_url, post_url))

def send_reset_password_email(user, token):
    send_mail_bytemplate(subject='Password Reset', to=user.email, template='emails/reset_password', user=user, token=token)
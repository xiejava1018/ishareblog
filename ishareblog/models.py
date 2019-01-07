# -*- coding: utf-8 -*-
"""
    :author: XieJava
    :url: http://ishareread.com
    :copyright: © 2019 XieJava <xiejava@ishareread.com>
    :license: MIT, see LICENSE for more details.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from ishareblog.extensions import db
from sqlalchemy import event

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)
    email = db.Column(db.String(254), unique=True, index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    post_count=db.Column(db.Integer,default=0)  #文章数

    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

    def get_post_count(self):
        result=db.session.execute(text('select count(1) from post where category_id=:category_id'), {'category_id':self.id}).first()[0]
        return result



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    can_comment = db.Column(db.Boolean, default=True)
    read_count=db.Column(db.Integer,default=0)  #阅读数

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

    def chang_read_count(self):
        db.session.execute(text('update post set read_count=read_count+1 where id=:category_id'), {'category_id': self.category_id})

    @staticmethod
    def chang_post_count(category_id):
        db.session.execute(text('update category set post_count=(select count(1) from post where category_id=:category_id) where id=:category_id'), {'category_id': category_id})

    @staticmethod
    def on_changed_post_count(target,value,oldvalue,initiator):
        print('target= %s' %target)
        print('value=' + str(value))
        print('value=' + str(oldvalue))
        print('initiator' + str(initiator))
        pass

    @staticmethod
    def on_insert(mapper, connection, target):
        Post.chang_post_count(target.category_id)
        print('target= %s' % target)
        print('value=' + str(connection))
        print('initiator' + str(mapper))
        pass

    @staticmethod
    def on_delete(mapper, connection, target):
        Post.chang_post_count(target.category_id)
        print('delete target= %s' % target)
        print('value=' + str(connection))
        print('initiator' + str(mapper))
        pass

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    post = db.relationship('Post', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    # Same with:
    # replies = db.relationship('Comment', backref=db.backref('replied', remote_side=[id]),
    # cascade='all,delete-orphan')


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))


#db.event.listen(Post.body,'set',Post.on_changed_post_count)
db.event.listen(Post,'after_insert',Post.on_insert)
db.event.listen(Post,'after_delete',Post.on_delete)
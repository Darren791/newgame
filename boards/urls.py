# URL patterns for the character app

from django.conf.urls import re_path
from paxboards.views import show_boardlist, show_board, show_thread, submit_post, submit_reply

urlpatterns = [
    re_path(r'^$', show_boardlist, name="boardlist"),
    re_path(r'^(?P<board_id>\d+)/$', show_board, name="board"),
    re_path(r'^(?P<board_id>\d+)/(?P<post_id>\d+)/$', show_thread, name="thread"),
    re_path(r'^(?P<board_id>\d+)/post/$', submit_post, name="post"),
    re_path(r'^(?P<board_id>\d+)/(?P<post_id>\d+)/reply/$', submit_reply, name="reply"),
]

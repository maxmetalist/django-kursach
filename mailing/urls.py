from django.urls import path

from mailing.views import HomeView, ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView, \
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView, MailingListView, MailingCreateView, \
    MailingUpdateView, MailingDeleteView, MailingDetailView, SendMailingManualView, MailingToggleView

app_name = 'mailing'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', HomeView.as_view(), name='catalog'),
# Client URLs
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
# Message URLs
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

# Mailing URLs
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/send/', SendMailingManualView.as_view(), name='send_manual'),
    path('<int:pk>/toggle/', MailingToggleView.as_view(), name='mailing_toggle'),
    ]

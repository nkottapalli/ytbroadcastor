
# Youtube Retrive Broadcast List of Live Streams

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

CLIENT_SECRETS_FILE = 'client-secrets.json'

YOUTUBE_READONLY_SCOPE = 'https://www.googleapis.com/auth/youtube.readonly'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

MISSING_CLIENT_SECRETS_MESSAGE = 'WARNING: Please configure OAuth 2.0'

VALID_BROADCAST_STATUSES = ['all', 'active', 'completed', 'upcoming']


def get_authenticated_service(args):
	flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
	scope=YOUTUBE_READONLY_SCOPE,
	message=MISSING_CLIENT_SECRETS_MESSAGE)
	storage = Storage("%s-oauth2.json" % sys.argv[0])
	credentials = storage.get()
	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, args)

	return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,http=credentials.authorize(httplib2.Http()))



def list_broadcasts(youtube, broadcast_status):
	print('Broadcasts with status ', broadcast_status)
	list_broadcasts_request = youtube.liveBroadcasts().list(broadcastStatus=broadcast_status,part='id,snippet',maxResults=50)

	while list_broadcasts_request:
		list_broadcasts_response = list_broadcasts_request.execute()
		print('kind :',list_broadcasts_response.get('kind'))
		print('etag :',list_broadcasts_response.get('etag'))
		pageInfo = list_broadcasts_response.get('pageInfo')
		print('pageInfo',pageInfo)
		items = list_broadcasts_response.get('items',[])
		print('number of braodcasts (all) :',len(items))
		for broadcast in items:
			print(broadcast['snippet']['title'], broadcast['id'])

		list_broadcasts_request = youtube.liveBroadcasts().list_next(list_broadcasts_request, list_broadcasts_response)



if __name__ == '__main__':
	argparser.add_argument('--broadcast-status', help='Broadcast status',choices=VALID_BROADCAST_STATUSES, default=VALID_BROADCAST_STATUSES[0])
	args = argparser.parse_args()
	youtube = get_authenticated_service(args)

	try:
		list_broadcasts(youtube, args.broadcast_status)
		print('Hello')
	except HttpError as  e:
		print('HTTP Error >> status :  ',e.resp.status, ', content : ',e.resp.content)



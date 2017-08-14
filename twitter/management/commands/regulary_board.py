from django.core.management.base import BaseCommand, CommandError
from twitter.models import Twitter
from chats.models import Board
from datetime import datetime

class Command(BaseCommand):
	help = 'test command'

	#コマンドライン引数受け取れるよ options['names']
	def add_arguments(self, parser):
		#parser.add_argument('names', nargs='+', type=int)
		pass

	#ここが呼ばれる
	def handle(self, *args, **options):
		try:
			for board in Board.objects.filter(is_status=0):
				if board.is_alive:
					board.is_status += 1
					board.save()
		except Board.DoesNotExist:
			raise CommandError('Board Error')


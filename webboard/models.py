#encoding=utf8
from django.db import models
from django.contrib.auth.models import User
from common.fields import FinancialYearField
from common.utils import check_base_class_by_name
from files.models import PublicFile
from django.core.exceptions import ValidationError

from notifications import Dispatcher

dispatcher = Dispatcher({
	'comment': u'${user}评论了你的文章${passage}。'
})

class Passage(models.Model):
	
	GOVERNMENT = 'GOV'
	MEDIA = 'MED'
	ENTERPRISE = 'ENT'
	FUND = 'FUN'
	CONFERENCE = 'CON'
	
	TYPE_MAP = {
		'Government': GOVERNMENT,
		'Media': MEDIA,
		'Enterprise': ENTERPRISE,
		'Fund': FUND
	}
	
	TYPE_CHOICES = map(lambda x:(x[1], x[0]), TYPE_MAP.iteritems())
	
	type = models.CharField(max_length = 3, editable = False, choices = TYPE_CHOICES)
	title = models.CharField(max_length = 255, verbose_name = u'标题')
	created_time = models.DateTimeField(auto_now_add = True)
	year = FinancialYearField()
	author = models.ForeignKey(User, related_name = 'passages', verbose_name = u'作者')
	content = models.TextField(verbose_name = u'内容')
	attachments = models.ManyToManyField(PublicFile, related_name = 'passages')
	
	def clean_fields(self, *args, **kwargs):
		if not self.type and self.author:
			res = filter(lambda x:check_base_class_by_name(self.author.profile.info, x), self.TYPE_MAP.iterkeys())
			if not res:
				raise ValidationError("No permission")
			self.type = self.TYPE_MAP[res[0]]
			
		super(Passage, self).clean_fields(*args, **kwargs)
	
	def __unicode__(self):
		return u"%s" % self.title
		
	def get_absolute_url(self):
		return '/webboard/passages/%d/' % self.id	
		
	class Meta:
		ordering = ['-created_time', 'title']
		verbose_name = u'文章'
		verbose_name_plural = verbose_name
		#app_label = u'新闻中心'
		#db_table = 'webboard_passage'
		permissions = [
			['publish_passage', 'Publish passage.']
		]
		
class Comment(models.Model):
	
	content = models.TextField()
	author = models.ForeignKey(User, related_name = 'comments')
	created_time = models.DateTimeField(auto_now_add = True)
	passage = models.ForeignKey(Passage, related_name = 'comments')
	#respond_comment = models.ForeignKey('self', related_name = 'responses', blank = True, null = True)
	
	def send(self):
		dispatcher.send('comment', {
				'passage': self.passage,
				'user': self.author.profile.info
		}, recipient = self.passage.author, target = self.passage)
	
	def __unicode__(self):
		return "%s comment for passage %s" % (self.author.username, self.passage.title)
		
	class Meta:
		ordering = ['-created_time']

from django.db import models
from django.contrib.auth.models import User, Group

TEACHER_CHOICES = ((u'Tabitha', u'Tabitha'), (u'Tyler', u'Tyler'), (u'Meghan', u'Meghan'),
					(u'Ariel', u'Ariel'), (u'Andrew', u'Andrew'), (u'Molly', u'Molly'), 
					(u'Jared', u'Jared'), (u'Ron', u'Ron'), (u'Nelson', u'Nelson'))
GRADE_CHOICES = ((u'G3', u'G3'), (u'G4', u'G4'), (u'G5',u'G5'), (u'G6',u'G6'), (u'G7',u'G7'), (u'G8',u'G8'), (u'G9',u'G9'))

TEST_CHOICES = ((u'LL', u'LL'), (u'ML', u'ML'), (u'UL', u'UL'))

DAY_CHOICES = ((u'1', u'Mon'), (u'2', u'Tue'), (u'3', u'Wed'), (u'4', u'Thu'), (u'5', u'Fri'), (u'6', u'Sat'), (u'7', u'Sun'))

class Teacher(models.Model):
	name = models.CharField(max_length=25)
	
	def __unicode__(self):
		return u"%s" % self.name

class ClassRoom(models.Model):
	code = models.CharField(max_length=20)
	teacher = models.ForeignKey(Teacher)
	day = models.CharField(max_length=5, choices=DAY_CHOICES)
	description = models.CharField(max_length=50)
	level = models.CharField(max_length=5, choices=TEST_CHOICES)
	
	def __unicode__(self):
		return u"%s" % self.code
		
class UserProfile(models.Model):
	user = models.ForeignKey(User, unique = True)
	teacher = models.ForeignKey(Teacher)
	classroom = models.ForeignKey(ClassRoom)
	grade = models.CharField(max_length=7,choices=GRADE_CHOICES)
	
class Test(models.Model):
	name = models.CharField(max_length=30)
	number_of_questions = models.IntegerField()
	level = models.CharField(max_length=5, choices=TEST_CHOICES)

	def __unicode__(self):
		return u"%s" % self.name

	class Meta:
		permissions = (("take_test", "Can take the test"), ("view_test", "Can view the test"))

class TestScore(models.Model):
	user = models.ForeignKey(User)
	test = models.ForeignKey(Test)
	date = models.DateField(auto_now_add=True)
	errors = models.CommaSeparatedIntegerField(max_length=50, null=True, blank=True)
	grade = models.CharField(max_length=10,null=True, blank=True)
	
	def __unicode__(self):
		return u"%s" % self.grade
		
class Question(models.Model):
	number = models.IntegerField()
	correct_answer = models.CharField(max_length=15)
	test = models.ForeignKey(Test)
	
	def __unicode__(self):
		return u"%d" % self.number


		

	

	

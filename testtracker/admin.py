from testtracker.models import UserProfile, TestScore, Test, Question, ClassRoom, Teacher
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from guardian.admin import GuardedModelAdmin

admin.site.unregister(User)

class UserProfileInline(admin.TabularInline):
	model = UserProfile


class UserProfileAdmin(UserAdmin):
	inlines = [UserProfileInline]
	
class QuestionAdmin(admin.ModelAdmin):
	list_display = ["test", "number", "correct_answer"]

class QuestionInline(admin.TabularInline):
	model = Question
	fields = ["number", "correct_answer"]
	extra = 20
	ordering = ["number"]
	
class TestAdmin(GuardedModelAdmin):
	list_display = ["name","number_of_questions"]
	inlines = [QuestionInline]
	
class TestScoreAdmin(admin.ModelAdmin):
	list_display = ["user", "test", "date", "grade", "errors"]

class ClassRoomAdmin(admin.ModelAdmin):
	list_display = ["teacher", "code"]
	
class ClassRoomInline(admin.TabularInline):
	model = ClassRoom
	fields = ["code"]
	extra = 10

class TeacherAdmin(admin.ModelAdmin):
	list_display = ["name",]
	inlines = [ClassRoomInline]
	



	
admin.site.register(User, UserProfileAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(TestScore, TestScoreAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)
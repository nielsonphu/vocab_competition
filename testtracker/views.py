from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from testtracker.models import Test, TestScore, UserProfile, ClassRoom, Teacher, Question
from django.contrib.auth.models import User
from guardian.decorators import permission_required_or_403
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from guardian.shortcuts import assign, remove_perm, get_objects_for_user, get_objects_for_group, get_perms
from guardian.utils import clean_orphan_obj_perms
from testtracker.forms import AddUserForm, DeleteUserForm, AddClassForm, DeleteClassForm, ChangePasswordForm, EditUserForm
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core import mail
from django.core.mail import send_mail


@login_required
def changepassword(request):
	if request.method == "POST":
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			if not request.user.check_password(cd['old_password']) :
				messages.add_message(request, messages.ERROR, 'You entered your old password incorrectly. Try again.')
				return HttpResponseRedirect(reverse(profile,))
			if cd['new_password'] != cd['confirm_new_password']:
				messages.add_message(request, messages.ERROR, "Your passwords don't match. Try again.")
				return HttpResponseRedirect(reverse(profile,))
			request.user.set_password(cd['new_password'])
			request.user.save()
			messages.add_message(request, messages.SUCCESS, "Your password has been changed successfully.")
			return HttpResponseRedirect(reverse(profile,))
	else:
		form = ChangePasswordForm()
	return render_to_response('changepassword.html', {'form': form}, context_instance=RequestContext(request))

		
@login_required
def addclass(request):
	if request.user.is_staff:
		if request.method == "POST":
			form = AddClassForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				if ClassRoom.objects.filter(code="%s" % cd['code']):
					messages.add_message(request, messages.ERROR, 'There is already a class with that code.')
					return HttpResponseRedirect(reverse(profile,))
				teacher = Teacher.objects.get(name=request.user.first_name)
				new_class = ClassRoom.objects.create(code=cd['code'], teacher=teacher, description=cd['description'], day=cd['day'], level=cd['level'])
				messages.add_message(request, messages.SUCCESS, 'Class has been successfully added.')
				return HttpResponseRedirect(reverse(profile,))
		else:
			form = AddClassForm()
		return render_to_response('addclass.html', {'form': form}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden

@login_required
def deleteclass(request):
	if request.user.is_staff:
		if request.method == "POST":
			form = DeleteClassForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				if not ClassRoom.objects.filter(code="%s" % cd['code']):
					messages.add_message(request, messages.ERROR, 'There is no class with that code.')
					return HttpResponseRedirect(reverse(profile,)) 
				classroom = ClassRoom.objects.get(code="%s" % cd['code'])
				students = User.objects.filter(userprofile__classroom__code=cd['code'])
				for student in students:
					old_testscores = TestScore.objects.filter(user=student)
					old_userprofiles = UserProfile.objects.filter(user=student)
					old_userprofiles.delete()
					old_testscores.delete()
					student.delete()
				classroom.delete()
				permission_removed = clean_orphan_obj_perms()
				messages.add_message(request, messages.SUCCESS, 'Class has been successfully removed.')
				return HttpResponseRedirect(reverse(profile,))
		else:
			form = DeleteClassForm()
		return render_to_response('deleteclass.html', {'form': form,}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden
		
def editclass(request, classcode):
	if request.user.is_staff:
		classroom = ClassRoom.objects.get(code=classcode)
		if request.method == "POST":
			form = AddClassForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				if classroom.code != cd['code'] and ClassRoom.objects.filter(code="%s" % cd['code']):
					messages.add_message(request, messages.ERROR, 'There is another class with that code.')
					return HttpResponseRedirect(reverse(profile,))
				classroom.code = cd['code']
				classroom.description = cd['description']
				classroom.level = cd['level']
				classroom.day = cd['day']
				classroom.save()
				messages.add_message(request, messages.SUCCESS, 'Class information has been successfully edited.')
				return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		else:
			form = AddClassForm(initial={'code': classroom.code, 'description': classroom.description, 'day': classroom.day, 'level': classroom.level,})
		return render_to_response('editclass.html', {'form': form, 'classroom': classroom,}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden
		
@login_required
def adduser(request, classcode):
	if request.user.is_staff:
		classroom = ClassRoom.objects.get(code="%s" % classcode)
		if request.method == "POST":
			form = AddUserForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				if User.objects.filter(username = cd['username']):
					messages.add_message(request, messages.ERROR, 'There is already a student with that username.')
					return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
				teacher = Teacher.objects.get(name=request.user.first_name)
				new_user = User.objects.create_user(username=cd['username'], password=cd['password'], email=cd['email'])
				new_user.first_name = cd['first_name']
				new_user.last_name = cd['last_name']
				new_user.save()
				new_userprofile = UserProfile.objects.create(user=new_user, teacher=teacher, classroom=classroom, grade=cd['grade'])
				messages.add_message(request, messages.SUCCESS, 'Student has been successfully added.')
				return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		else:
			form = AddUserForm()
		return render_to_response('adduser.html', {'form': form, 'classroom':classroom}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden

@login_required
def deleteuser(request, classcode):
	if request.user.is_staff:
		classroom = ClassRoom.objects.get(code="%s" % classcode)
		if request.method == "POST":
			form = DeleteUserForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				if not User.objects.filter(username=cd['username']):
					messages.add_message(request, messages.ERROR, 'There is no student with that username.')
					return HttpResponseRedirect(reverse(classprofile, args=(classcode,))) #Need to change for error message
				old_user = User.objects.get(username=cd['username'])
				old_testscores = TestScore.objects.filter(user=old_user)
				old_userprofiles = UserProfile.objects.filter(user=old_user)
				old_userprofiles.delete()
				old_testscores.delete()
				old_user.delete()
				permission_removed = clean_orphan_obj_perms()
				messages.add_message(request, messages.SUCCESS, 'Student has been successfully removed.')
				return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		else:
			form = DeleteUserForm()
		return render_to_response('deleteuser.html', {'form': form, 'classroom':classroom}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden

@login_required
def edituser(request, classcode, username):
	if request.user.is_staff:
		classroom = ClassRoom.objects.get(code="%s" % classcode)
		old_user = User.objects.get(username=username)
		old_userprofile = UserProfile.objects.get(user=old_user)
		if request.method == "POST":
			form = EditUserForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				if old_user.username != cd['username'] and User.objects.filter(username = cd['username']):
					messages.add_message(request, messages.ERROR, 'There is another student with that username.')
					return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
				teacher = Teacher.objects.get(name=request.user.first_name)
				old_user.username = cd['username']
				old_user.first_name = cd['first_name']
				old_user.last_name = cd['last_name']
				if cd['password'] != "":
					old_user.set_password(cd['password'])
				old_user.email = cd['email']
				old_user.save()
				old_userprofile.teacher = teacher
				old_userprofile.grade = cd['grade']
				old_userprofile.save()
				messages.add_message(request, messages.SUCCESS, 'Student information has been successfully changed.')
				return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		else:
			form = EditUserForm(initial={'username': old_user.username, 'first_name': old_user.first_name, 'last_name': old_user.last_name, 
										'email': old_user.email, 'grade': old_userprofile.grade, 'teacher': old_userprofile.teacher,})
		return render_to_response('edituser.html', {'form': form, 'classroom':classroom, 'old_user': old_user}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden
				
@login_required
def assigntest(request, classcode):
	if request.user.is_staff and request.method == "POST":
		if request.POST["assignedtest"] == "----":
			return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		students = User.objects.filter(userprofile__classroom__code=classcode)
		if len(students) == 0:
			messages.add_message(request, messages.ERROR, 'Add all students before assigning any tests.')
			return HttpResponseRedirect(reverse(classprofile, args=(classcode,))) #Assigning a test with no students will NOT DO ANYTHING
		test = Test.objects.get(name="%s" % request.POST["assignedtest"])
		
		connection = mail.get_connection(fail_silently=True)
		connection.open()
		emails = []

		for student in students:
			assign('take_test', student, test)
			assign('testtracker.view_test', student, test)
			emails.append(mail.EmailMessage('Capstone vocabulary test has been assigned',
											"""
		Hello, your teacher has assigned a new vocabulary test for the Capstone Vocabulary Competition, which means it's now available
		for you to do at www.capstonevocab.com. Your username is %s and your password should be the same as your username unless you
		have changed it. Please complete the test by your next class.
											""" % student.username,
											'capstone@capstonevocab.com',
											['%s' % student.email], connection=connection))
		connection.send_messages(emails)
		connection.close()
		messages.add_message(request, messages.SUCCESS, 'Test has been successfully assigned.')
		return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
	else:
		return HttpResponseForbidden
		
@login_required
def assigntostudent(request, classcode):
	if request.user.is_staff and request.method == "POST":
		if request.POST["assignedtest"] == "----" or request.POST["student"] == "----":
			return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		students = User.objects.filter(userprofile__classroom__code=classcode)
		if len(students) == 0:
			messages.add_message(request, messages.ERROR, 'Add all students before assigning any tests.')
			return HttpResponseRedirect(reverse(classprofile, args=(classcode,))) #Assigning a test with no students will NOT DO ANYTHING
		test = Test.objects.get(name="%s" % request.POST["assignedtest"])
		student = User.objects.get(username=request.POST["student"])
		assign('testtracker.take_test', student, test)
		assign('testtracker.view_test', student, test)
		send_mail('Capstone vocabulary test has been assigned',
											"""
	Hello, your teacher has assigned a new vocabulary test for the Capstone Vocabulary Competition, which means it's now available
	for you to do at www.capstonevocab.com. Your username is %s and your password should be the same as your username unless you 
	have changed it. Please complete the test by your next class.
											""" % student.username,
											'capstone@capstonevocab.com',
											['%s' % student.email], fail_silently = True)
		messages.add_message(request, messages.SUCCESS, 'Test has been successfully assigned.')
		return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
	else:
		return HttpResponseForbidden
		
def deactivatetest(request, classcode):
	if request.user.is_staff and request.method == "POST":
		if request.POST["deactivatedtest"] == "----":
			return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		students = User.objects.filter(userprofile__classroom__code=classcode)
		test = Test.objects.get(name="%s" % request.POST["deactivatedtest"])
		for student in students:
			remove_perm('testtracker.take_test', student, test)
		messages.add_message(request, messages.SUCCESS, 'Test has been successfully deactivated.')
		return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
	else:
		return HttpResponseForbidden
		
def unassigntest(request, classcode):
	if request.user.is_staff and request.method == "POST":
		if request.POST["unassignedtest"] == "----":
			return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
		test = Test.objects.get(name="%s" % request.POST["unassignedtest"])
		students = User.objects.filter(userprofile__classroom__code=classcode)
		for student in students:
			old_testscore = TestScore.objects.filter(test=test).filter(user=student)
			old_testscore.delete()
			remove_perm('testtracker.take_test', student, test)
			remove_perm('testtracker.view_test', student, test)
		permission_removed = clean_orphan_obj_perms()
		messages.add_message(request, messages.SUCCESS, 'Test has been successfully unassigned.')
		return HttpResponseRedirect(reverse(classprofile, args=(classcode,)))
	else:
		return HttpResponseForbidden	
	
@login_required
def classprofile(request, classcode):
	if request.user.is_staff:
		classroom = ClassRoom.objects.get(code="%s" % classcode)
		students = User.objects.filter(userprofile__classroom__code="%s" % classcode)
		all_tests = Test.objects.filter(level=classroom.level)
		teacher = Teacher.objects.get(name=request.user.first_name)
		student_record = {}
		if len(students) == 0:
			available_tests = []
		else:
			available_tests = get_objects_for_user(students[0], 'testtracker.view_test')
			available_tests.reverse()
		for student in students: 
			studentlistrecord = {}
			for test in available_tests:
				testinfo = {}
				if test in Test.objects.filter(testscore__user=student):
					testscore = TestScore.objects.filter(user=student).get(test=test)
					testinfo['grade'] = testscore.grade
				else:
					testinfo['grade'] = "IC"
				testinfo['permission'] = student.has_perm('testtracker.take_test', test)
				studentlistrecord['%s' % test.name] = testinfo
			student_record["%s" % student.username] = studentlistrecord
		list_of_deactivated = []
		for test in available_tests:
			test_deactivated = True
			for student in students:
				if student.has_perm('take_test', test):
					test_deactivated = False
			if test_deactivated == True:
				list_of_deactivated.append(test.name)
		return render_to_response('studentscores.html', {'students': students, 'classroom':classroom, 'all_tests': all_tests, 'student_record': student_record, 'available_tests': available_tests, 'list_of_deactivated': list_of_deactivated}, context_instance=RequestContext(request))
	else:
		return HttpResponseForbidden
		
@login_required
def profile(request):
	if request.user.is_staff:
		teacher = Teacher.objects.get(name=request.user.first_name)
		classrooms = ClassRoom.objects.filter(teacher=teacher).order_by('day')
		return render_to_response('classlist.html', {'classrooms':classrooms,}, context_instance=RequestContext(request))
	tests = get_objects_for_user(request.user, 'testtracker.view_test')
	tests.reverse()
	test_and_score_list = []
	for test in tests:
		if test in Test.objects.filter(testscore__user=request.user):
			remove_perm('take_test', request.user, test)
	for test in tests:
		perm = get_perms(request.user, test)
		if test in Test.objects.filter(testscore__user=request.user):
			testscore = TestScore.objects.filter(user=request.user).get(test=test)
			test_and_score_list.append((test, testscore.grade, perm))
		else:
			test_and_score_list.append((test, "Incomplete", perm))
	return render_to_response('profile.html', {'test_and_score_list': test_and_score_list}, context_instance=RequestContext(request))

@login_required
def testlanding(request, testname):
	return render_to_response('testlanding.html', {'testname':testname}, context_instance=RequestContext(request))
	
@login_required	
def take_test(request, testname):
	test = Test.objects.get(name=testname)
	if test in Test.objects.filter(testscore__user=request.user):
		remove_perm('take_test', request.user, test)
	if request.user.has_perm('take_test', test):
		TestScore.objects.create(user=request.user, test=test, grade="ERROR")
		remove_perm('take_test', request.user, test)
		return render_to_response("%s.html" % testname, {}, context_instance=RequestContext(request))
	else:	
		return render_to_response("error.html", {}, context_instance=RequestContext(request))

@login_required
def get_score(request,testname):
	test = Test.objects.get(name=testname)
	if request.method == "POST":
		errors = []
		corrects = []
		questions = Question.objects.filter(test__name='%s' % testname)

		for question in questions:
			studentanswer = request.POST['studentanswer%d' % question.number].strip().lower()
			if studentanswer == question.correct_answer:
				corrects.append(question)
			else:
				errors.append(question)
		
		total_questions = len(questions)
		total_correct = len(corrects)
		result = u"%d" % (total_correct*100/total_questions) + u"%"
		
		score = TestScore.objects.filter(user=request.user).get(test=test)
		score.grade = result
		score.save()
		return render_to_response("result.html", {'result':result, 'corrects': corrects, 'errors': errors}, context_instance=RequestContext(request)) #Need to change to HttpResponseRedirect
	else:
		return HttpResponseForbidden()
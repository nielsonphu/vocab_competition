from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from testtracker import views
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', lambda x: HttpResponseRedirect('/accounts/login/')),
	(r'^accounts/login/$', login),
	(r'^accounts/logout/$', logout),
	(r'^accounts/profile/$', views.profile),
	(r'^accounts/profile/class(\w+)/assign/$', views.assigntest),
	(r'^accounts/profile/class(\w+)/assigntostudent/$', views.assigntostudent),
	(r'^accounts/profile/class(\w+)/deactivate/$', views.deactivatetest),
	(r'^accounts/profile/class(\w+)/unassign/$', views.unassigntest),
	(r'^accounts/profile/(\w+)/$', views.testlanding),
	(r'^test/(\w+)/$', views.take_test),
	(r'^(\w+)/score/$', views.get_score),
	(r'^class/studentscores/(\w+)/$', views.classprofile),
	(r'^class/add/$', views.addclass),
	(r'^class/edit/(\w+)/$', views.editclass),
	(r'^class/(\w+)/addstudent/$', views.adduser),
	(r'^class/(\w+)/removestudent/$', views.deleteuser),
	(r'^class/remove/$', views.deleteclass),
	(r'^class/(\w+)/editstudent/(\w+)/$', views.edituser),
	(r'^profile/changepassword/$', views.changepassword),
    # Examples:
    # url(r'^$', 'capstonevocab.views.home', name='home'),
    # url(r'^capstonevocab/', include('capstonevocab.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

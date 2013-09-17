from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'WBS.views.home', name='home'),
    url(r'^new-project/$', 'WBS.views.createProject', name='createProject'),
    url(r'^project/(?P<pid>\d+)/$', 'WBS.views.project_details', name='project_details'),
    url(r'^project/(?P<pid>\d+)/new-task/$', 'WBS.views.createTask', name='createTask'),
    url(r'^project/(?P<pid>\d+)/view-task/(?P<tid>\d+)/$', 'WBS.views.viewTask', name='viewTask'),
    url(r'^project/(?P<pid>\d+)/update-task/(?P<tid>\d+)/$', 'WBS.views.updateTask', name='updateTask'),
    url(r'^project/(?P<pid>\d+)/delete-task/(?P<tid>\d+)/$', 'WBS.views.deleteTask', name='deleteTask'),
    url(r'^project/(?P<pid>\d+)/toggle-task/(?P<tid>\d+)/$', 'WBS.views.toggleTask', name='toggleTask'),
    url(r'^project/(?P<pid>\d+)/move-task/(?P<tid>\d+)/down/$', 'WBS.views.moveTaskDown', name='moveTaskDown'),
    url(r'^project/(?P<pid>\d+)/move-task/(?P<tid>\d+)/up/$', 'WBS.views.moveTaskUp', name='moveTaskUp'),
    url(r'^project/(?P<pid>\d+)/add-admin/$', 'WBS.views.addAdmin', name='addAdmin'),
    url(r'^project/(?P<pid>\d+)/remove-admin/$', 'WBS.views.removeAdmin', name='removeAdmin'),
    url(r'^accounts/create/$', 'WBS.views.createUser', name='createUser'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',{'template_name': 'WBS/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'WBS.views.profile', name='profile'),    
)

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'WBS.views.home', name='home'),
    url(r'^new-project/$', 'WBS.views.createProject', name='wbs/new-project'),
    url(r'^project/(?P<pid>\d+)/$', 'WBS.views.project_details', name='wbs/project'),
    url(r'^project/(?P<pid>\d+)/new-task/$', 'WBS.views.createTask', name='wbs/new-task'),
    url(r'^project/(?P<pid>\d+)/view-task/(?P<tid>\d+)/$', 'WBS.views.viewTask', name='wbs/view-task'),
    url(r'^project/(?P<pid>\d+)/update-task/(?P<tid>\d+)/$', 'WBS.views.updateTask', name='wbs/update-task'),
    url(r'^project/(?P<pid>\d+)/delete-task/(?P<tid>\d+)/$', 'WBS.views.deleteTask', name='wbs/delete-task'),
    url(r'^project/(?P<pid>\d+)/toggle-task/(?P<tid>\d+)/$', 'WBS.views.toggleTask', name='wbs/toggle-task'),
    url(r'^project/(?P<pid>\d+)/move-task/(?P<tid>\d+)/down/$', 'WBS.views.moveTaskDown', name='wbs/move-task-up'),
    url(r'^project/(?P<pid>\d+)/move-task/(?P<tid>\d+)/up/$', 'WBS.views.moveTaskUp', name='wbs/move-task-down'),
    url(r'^project/(?P<pid>\d+)/add-admin/$', 'WBS.views.addAdmin', name='wbs/add-admin'),
    url(r'^project/(?P<pid>\d+)/remove-admin/$', 'WBS.views.removeAdmin', name='wbs/remove-admin'),
    url(r'^accounts/create/$', 'WBS.views.createUser', name='wbs/createUser'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',{'template_name': 'WBS/login.html'},name='wbs/login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login',name='wbs/logout'),
    url(r'^accounts/profile/$', 'WBS.views.profile', name='wbs/profile'),    
)

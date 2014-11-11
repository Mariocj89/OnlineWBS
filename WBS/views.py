# Create your views here.
from django.shortcuts import render_to_response, redirect
from WBS import models
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from WBS.forms import WBSUserForm, WBSUpdateUserForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe
import json as simplejson
from WBS.models import Task, Project,CreateUser, UserPreferences
from django.core.mail import send_mail
import re
import string
import random
from django.core.urlresolvers import reverse

def print_header(task):
    """
        Return heading for a task including its parents up to the root(root not included).
        Examples: 1.1.1 or 1.2.3, 3.2.2
    """
    if task.parent:
        return print_header(task.parent) + str(task.orderIdx)+"."
    else:
        return ""

def print_task_hierarchy(task,preferences):
    """
        Return for a task and its children some HTML code and:
            -Icon for new task
            -Icon for delete task
            -Icon for edit task
            -Icon for view task
            -Icon for move down/up if possible
    """
    ret = "<ul>"
    print "Formating Task: ",task, " - idx: ",task.orderIdx
    isFinishedCss = ""
    if task.isFinished():
        isFinishedCss += " completed-task"
    ret += "<li class='ui-accordion-header ui-state-default ui-corner-all ui-accordion-icons "+isFinishedCss+"' alt='" + str(task.pk) + "'>"
    ret += "<b><i>" + print_header(task) + "</i> - " +task.title +"</b>"
    ret += "<a class='new-task' href='#' alt='"+str(task.pk)+"'><img title='Add Task' class='list-icon' src='/static/WBS/img/add.png' /></a>"
    ret += "<a class='delete-task' href='#' alt='"+str(task.pk)+"'><img title='Delete Task' class='list-icon' src='/static/WBS/img/delete.png' /></a>"
    ret += "<a class='edit-task' href='#' alt='"+str(task.pk)+"'><img title='Edit Task' class='list-icon' src='/static/WBS/img/edit.png' /></a>"
    ret += "<a class='view-task' href='#' alt='"+str(task.pk)+"'><img title='View Task' class='list-icon' src='/static/WBS/img/view.png' /></a>"

    #Cost
    ret += "<a class='task-cost' href='#' alt='"+str(task.pk)+"'>"
    if preferences.showInlineCost:
        ret += "<span title='Cost' class='list-icon'>"+task.getCostStr()+" </span>"
    ret += "<img title='Cost: "+task.getCostStr()+"' class='list-icon' src='/static/WBS/img/cost.png' /></a>"

    #Completion
    ret += "<a class='task-completion' href='#' alt='"+str(task.pk)+"'>"
    if preferences.showInlineCompletion:
        ret += "<span title='% Done so far' class='list-icon'>"+task.getCompletionStr()+" </span>"
    ret += "<img title='Completion: "+("%.2f" % task.getCompletion())+"%' class='list-icon' src='/static/WBS/img/completion.png' /></a>"

    if not task.isLast():
        ret += "<a class='move-task-down' href='#' alt='"+str(task.pk)+"'><img title='Move Down' class='list-icon' src='/static/WBS/img/down.png' /></a>"
    if not task.isFirst():
        ret += "<a class='move-task-up' href='#' alt='"+str(task.pk)+"'><img title='Move Up' class='list-icon' src='/static/WBS/img/up.png' /></a>"


    for t in task.children.order_by('orderIdx'):
        ret += print_task_hierarchy(t,preferences)


    ret += "</li>"
    ret += "</ul>"

    return ret

def print_task_to_hide(task,user):
    """
        Return css classes to select all tasks that the user hided before.
    """
    ret = ""
    try:
        if User.objects.filter(username = user.username,collapsedTasks=task):
            ret = "li[alt="+str(task.pk)+"],"
    except User.DoesNotExist:
        pass
    for t in task.children.all():
        ret += print_task_to_hide(t,user)
    return ret

@login_required
def home(request):
    """
        View for index.html
    """
    theOngoingSet = models.Project.objects.filter(administrators__username=request.user.username)
    theFinishedSet= {}#TODO
    return render_to_response("WBS/index.html",
                              {'ongoing':theOngoingSet,
                               'finished':theFinishedSet,
                               'request':request})

@login_required
def project_details(request,pid):
    """
        View for project details
    """
    try:
        theProject = models.Project.objects.filter(administrators__username=request.user.username).prefetch_related('administrators').get(pk=pid)
    except models.Project.DoesNotExist:
        return redirect('WBS.views.home')#HttpResponse('Unauthorized', status=401)
    formattedTaks =  print_task_hierarchy(theProject,request.user.preferences)
    aux = print_task_to_hide(theProject,request.user)
    if len(aux) > 0:
        extraScript =    "$('"+aux[:-1]+"').click();"
    else:
        extraScript=""
    return render_to_response("WBS/project_details.html",
                              {'project':theProject,
                               'html_formatted_taks':mark_safe(formattedTaks),
                               'extra_script':mark_safe(extraScript),
                               'request':request})

@csrf_exempt
@login_required
def profile(request):
    """
        View for user details
    """
    try:
        rollback_user = request.user
        if request.method == 'POST': # If the form has been submitted...
            form = WBSUpdateUserForm(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                usuario = request.user
                usuario.username = request.POST["username"]
                usuario.set_password(request.POST["password"])
                usuario.email = request.POST["email"]
                usuario.save()
                try:
                    aUserP = UserPreferences.objects.get(user__pk=usuario.pk)
                except UserPreferences.DoesNotExist, e:
                    print "[WARN] User preferences does not exist, One is being created"
                    aUserP = UserPreferences()
                    UserPreferences.user = User.objects.get(pk=usuario.pk)
                    aUserP.save()
                aUserP.showInlineCost = request.POST.get("showInlineCost") == 'on'
                aUserP.showInlineCompletion = request.POST.get("showInlineCompletion") == 'on'
                aUserP.save()
                return HttpResponseRedirect(reverse('wbs/profile')) # Redirect after POST
        else:
            form = WBSUpdateUserForm() # An unbound form
    except IntegrityError, e:
        print e
        request.user = rollback_user
        form._errors["username"] = ErrorList([e.message.replace('column ', '')])
    return render_to_response("WBS/account.html",
                              {'request':request,
                               'form':form})



@csrf_exempt
@login_required
def createProject(request):
    """
        WS to create a project
    """
    aProject = models.Project()
    aProject.title = request.POST['title']
    aProject.description = request.POST['description']
    aProject.save()
    aProject.administrators.add(User.objects.get(username= request.user.username))
    print "Saving Project: ",aProject
    aProject.save()
    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def viewTask(request,pid,tid):
    """
        WS to view a task
    """
    admin = User.objects.get(username= request.user.username)
    project = Project.objects.get(pk=pid)
    task = Task.objects.get(pk=tid)

    if task.root().pk != project.pk or not project.administrators.filter(pk=admin.pk):
        if task.root().pk != project.pk:
            aux = "Task and project does not match"
        elif not project.administrators.filter(pk=admin.pk):
            aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    data = {
        "title": task.title,
        "description": task.description,
        "cost": ("%.2f" % task.getCost()),
        "completion":("%.2f" % task.getCompletion()),
        "isLeaf":task.isLeaf()
    }
    data = simplejson.dumps(data)
    print "Viewing Task: ",task, "  -> ",data
    return HttpResponse(data, mimetype="application/json")


@csrf_exempt
@login_required
def createTask(request,pid):
    """
        WS to create a task
    """
    aTask = models.Task()
    aTask.title = request.POST['title']
    aTask.description = request.POST['description'] if request.POST['description'] else 0
    aTask.cost = request.POST['cost']
    aTask.completion = float(request.POST['completion'])
    assert(aTask.completion < 100.1)
    aTask.save()
    aTask.parent = Task.objects.get(pk=pid)
    tasks = Task.objects.filter(parent__id = pid)
    lastIdx = 0
    if tasks:
        lastIdx= tasks.order_by('-orderIdx')[0].orderIdx

    aTask.orderIdx = lastIdx + 1

    print "Saving Task: ",aTask, " Parent: ",aTask.parent, " idx: ",aTask.orderIdx
    aTask.save()
    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def updateTask(request,pid,tid):
    """
        WS to edit a task
    """
    admin = User.objects.get(username= request.user.username)
    project = Project.objects.get(pk=pid)
    task = Task.objects.get(pk=tid)

    if task.root().pk != project.pk or not project.administrators.filter(pk=admin.pk):
        if task.root().pk != project.pk:
            aux = "Task and project does not match"
        elif not project.administrators.filter(pk=admin.pk):
            aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    task.title = request.POST['title']
    task.description = request.POST['description']
    task.cost = request.POST['cost']
    task.completion = float(request.POST['completion'])
    assert(task.completion <= 100)
    assert(task.completion >= 0)
    #aTask.orderIdx = request.POST['description']
    print "Saving Task: ",task, ", Parent: ",task.parent, ", idx: ",task.orderIdx, ", cost",task.cost, ", Calculated: ",task.getCost(),", completion",task.completion, ", Completion: ",task.getCompletion()
    task.save()
    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def moveTaskDown(request,pid,tid):
    """
        WS to move a task down
    """
    admin = User.objects.get(username= request.user.username)
    project = Project.objects.get(pk=pid)
    task = Task.objects.get(pk=tid)

    if task.root().pk != project.pk or not project.administrators.filter(pk=admin.pk):
        if task.root().pk != project.pk:
            aux = "Task and project does not match"
        elif not project.administrators.filter(pk=admin.pk):
            aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    print "Moving Down Task: ",task, " Parent: ",task.parent, " idx: ",task.orderIdx
    task.move_down()

    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def moveTaskUp(request,pid,tid):
    """
        WS to move a task up
    """
    admin = User.objects.get(username= request.user.username)
    project = Project.objects.get(pk=pid)
    task = Task.objects.get(pk=tid)

    if task.root().pk != project.pk or not project.administrators.filter(pk=admin.pk):
        if task.root().pk != project.pk:
            aux = "Task and project does not match"
        elif not project.administrators.filter(pk=admin.pk):
            aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    print "Moving Down Up: ",task, " Parent: ",task.parent, " idx: ",task.orderIdx
    task.move_up()

    return HttpResponse({},status=201)


@csrf_exempt
@login_required
def deleteTask(request,pid,tid):
    """
        WS to remove a task
    """
    admin = User.objects.get(username= request.user.username)
    project = Project.objects.get(pk=pid)
    task = Task.objects.get(pk=tid)

    if task.root().pk != project.pk or not project.administrators.filter(pk=admin.pk):
        if task.root().pk != project.pk:
            aux = "Task and project does not match"
        elif not project.administrators.filter(pk=admin.pk):
            aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    #aTask.orderIdx = request.POST['description']
    print "Deleting Task: ",task, " Parent: ",task.parent, " idx: ",task.orderIdx
    task.delete()
    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def toggleTask(request,pid,tid):
    """
        WS to hide/show a task
    """
    admin = User.objects.get(username= request.user.username)
    project = Project.objects.get(pk=pid)
    task = Task.objects.get(pk=tid)

    if task.root().pk != project.pk or not project.administrators.filter(pk=admin.pk):
        if task.root().pk != project.pk:
            aux = "Task and project does not match"
        elif not project.administrators.filter(pk=admin.pk):
            aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    #aTask.orderIdx = request.POST['description']
    print "Toggling Task: ",task

    if User.objects.filter(username = admin.username,collapsedTasks=task):
        User.objects.get(username = admin.username).collapsedTasks.remove(task)
    else:
        User.objects.get(username = admin.username).collapsedTasks.add(task).save()

    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def addAdmin(request,pid):
    """
        WS to add an admin to a existing project
    """
    admin = User.objects.get(username= request.user.username)
    usernameToAdd= str(request.POST['new-admin']).replace(" ", "")
    try:
        adminToAdd = User.objects.get(username=usernameToAdd)
    except User.DoesNotExist:
        try:
            adminToAdd = User.objects.get(email= usernameToAdd)
        except User.DoesNotExist:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", usernameToAdd):
                raise User.DoesNotExist
            else:
                char_set = string.ascii_uppercase + string.digits
                randomPwd = ''.join(random.sample(char_set*6,6))
                adminToAdd =CreateUser(usernameToAdd,randomPwd)
                send_mail('OnlineWBS Registration', 'You have been invited to user Online WBS by ' + request.user.email + '.Your username is: '+adminToAdd.username + ' and your password: '+randomPwd, 'admin@OnlineWBS.com',
                            [usernameToAdd], fail_silently=False)


    project = Project.objects.get(pk=pid)

    if not project.administrators.filter(pk=admin.pk):
        aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    #aTask.orderIdx = request.POST['description']
    print "Adding admin("+str(adminToAdd)+") to project: ",str(project)
    project.administrators.add(adminToAdd)
    return HttpResponse({},status=201)

@csrf_exempt
@login_required
def removeAdmin(request,pid):
    """
        WS to add an admin to a existing project
    """
    admin = User.objects.get(username= request.user.username)
    adminToRemove = User.objects.get(pk= request.POST['remove-admin'])
    project = Project.objects.get(pk=pid)

    if not project.administrators.filter(pk=admin.pk):
        aux = "User does not admin the project"
        print "Security issue: ",aux
        return HttpResponse('Unauthorized', status=401)

    #aTask.orderIdx = request.POST['description']
    print "Remove admin("+str(adminToRemove)+") to project: ",str(project)
    project.administrators.remove(adminToRemove)
    return HttpResponse({},status=201)


@csrf_exempt
def createUser(request):
    """
        WS to create an user
    """
    try:
        rollback_user = request.user
        if request.method == 'POST': # If the form has been submitted...
            form = WBSUserForm(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                anUsername = request.POST["username"]
                aPassword  = (request.POST["password"])
                anEmail = request.POST["email"]
                CreateUser(anEmail,aPassword,anUsername)

                return HttpResponseRedirect(reverse('home')) # Redirect after POST
        else:
            form = WBSUserForm() # An unbound form
    except IntegrityError, e:
        print e
        request.user = rollback_user
        form._errors["username"] = ErrorList([e.message.replace('column ', '')])
    return render_to_response("WBS/createAccount.html",
                              {'request':request,
                               'form':form})


from django.db import models
from django.contrib.auth.models import User
from multiprocessing.synchronize import Lock
from django.core.validators import MaxValueValidator, MinValueValidator


taskMutex  = Lock()

def CreateUser(mail, pwd, username = None):
    """
        Method to simply create an user in the system.
        Takes as user name the first part of the mail
    """
    if username == None:
        username = mail.split("@")[0]
    aUser = User.objects.create_user(username, mail, pwd)
    aUser.save()
    aPreferences = UserPreferences()
    aPreferences.user = aUser
    aPreferences.save()
    
    return aUser

class UserPreferences(models.Model):
    """
        Stores the preferences of a User
    """
    
    user = models.OneToOneField(User,related_name="preferences")
    """User whose this preferences belongs"""
    showInlineCost = models.BooleanField(default=True)
    """Whether or not to show the cost inline in the project details."""
    showInlineCompletion = models.BooleanField(default=True)
    """Whether or not to show the completion inline in the project details."""


# Create your models here.    
class Task(models.Model):
    """
        Represents a task in the system.
    """
    title = models.CharField(max_length=128)
    """Title of the task"""
    description = models.TextField()
    """Description of the task"""
    parent = models.ForeignKey("self", blank=True,null=True, related_name="children")
    """Parent task of the task. Null for roots"""
    orderIdx = models.IntegerField(default=1)
    """Position of the task between its siblings"""
    cost = models.FloatField(default=0.0)
    """Cost of the task"""
    completion = models.FloatField(default=0.0, validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])
    """Percentage of completion of the task"""    
    isCollapsedByUser = models.ManyToManyField(User,related_name='collapsedTasks')
    """Stores the users that collapsed this task in their UI"""
    

    def getCompletion(self):
        """
            Given a task, if it is a leaf, returns its completion,
            otherwise, the completion is calculated from the children.[It depends on the cost]
        """
        if self.children and len(self.children.all()) == 0:
            return  self.completion
        else:   #Calculated one
            acc = 0
            for c in self.children.all():
                acc += c.getCompletion() * c.getCost()
            if self.getCost() == 0: #If the task has no cost, it means that it finished, isn't it? :D
                return 100.0
            
            return acc / self.getCost()

    def isFinished(self):
        """
            Check if a task is finished (completion==100%)
        """
        return self.getCompletion() == 100.0

    def getCost(self):
        """
            Given a task, if it is a leaf, returns its cost,
            otherwise, the cost is calculated from the children.
        """
        if self.children and len(self.children.all()) == 0:
            return  self.cost
        else:   #Calculated one
            acc = 0
            for c in self.children.all():
                acc += c.getCost()
            return acc
    
    def isLeaf(self):
        """
            Check if a task is a leaf one.
            It means that it has no children
        """
        return self.children and len(self.children.all()) == 0
        
    def isLast(self):
        """
            Check if the task is the last of the siblings
        """
        if self == None or self.parent == None:
            return True
        
        lastOne= self.parent.children.order_by('-orderIdx')[0]
        return self.pk == lastOne.pk 
    
    def isFirst(self):
        """
            Check if the task is the first of the siblings
        """        
        if self == None or self.parent == None:
            return True
        
        firstOne= self.parent.children.order_by('orderIdx')[0]
        return self.pk == firstOne.pk     
    
    def move_down(self):
        """
            Swap the index number(order) with the next sibling
            imediately down.
        """
        lastIdx= self.parent.children.order_by('-orderIdx')[0].orderIdx
        taskToSwap = None
        idxAux = self.orderIdx + 1
        while idxAux <= lastIdx and taskToSwap == None:
            try:
                taskMutex.acquire()#mutex
                
                taskToSwap = self.parent.children.get(orderIdx=idxAux)
                taskToSwap.orderIdx = self.orderIdx
                self.orderIdx = idxAux
                taskToSwap.save()
                self.save()
            except Task.DoesNotExist:
                idxAux = idxAux + 1
                
            taskMutex.release()#mutex end
                
    def move_up(self):
        """
            Swap the index number(order) with the next sibling
            imediately up.
        """        
        lastIdx= self.parent.children.order_by('orderIdx')[0].orderIdx
        taskToSwap = None
        idxAux = self.orderIdx - 1
        while idxAux >= lastIdx and taskToSwap == None:
            try:
                taskToSwap = self.parent.children.get(orderIdx=idxAux)
                taskToSwap.orderIdx = self.orderIdx
                self.orderIdx = idxAux
                taskToSwap.save()
                self.save()
            except Task.DoesNotExist:
                idxAux = idxAux - 1                
    
    def depth(self):
        """
            Calculates the the distance to the root task(project)
        """
        if self.parent == None:
            return 0
        else:
            return self.parent.depth() + 1
         
    def root(self):
        """
            Returns the root task(project)
        """
        if(self.parent):
            return self.parent.root()
        else:
            return self
        
    def __unicode__(self):
        return self.title    
    
class Project(Task):
    """
        Type of task that represents a Project in the system
    """
    administrators = models.ManyToManyField(User,related_name='projects_as_admin')
    """List of users with full privileges in the Project"""

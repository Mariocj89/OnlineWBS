"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TaksTest(TestCase ):
    """
        t1
         |
        t2
         |
        t3------------
         |  |  |  |  |
        t4 t5 t6 t7 t8
    
    """   
    def setUp(self):
        self.t1 = Task(title="tit1")
        self.t2 = Task(title="tit2")
        self.t3 = Task(title="tit3")
        self.t4 = Task(title="tit4")
        self.t5 = Task(title="tit5")
        self.t6 = Task(title="tit6")
        self.t7 = Task(title="tit7")
        self.t8 = Task(title="tit8")
        self.t2.parent = self.t1
        self.t1.children.add(self.t2)
        self.t3.parent = self.t2
        self.t2.children.add(self.t3)
        self.t4.parent = self.t3
        self.t3.children.add(self.t4)
        self.t5.parent = self.t3
        self.t3.children.add(self.t5)
        self.t6.parent = self.t3
        self.t3.children.add(self.t6)
        self.t7.parent = self.t3
        self.t3.children.add(self.t7)
        self.t8.parent = self.t3     
        self.t3.children.add(self.t8)   
        self.t1.orderIdx = 1
        self.t2.orderIdx = 1
        self.t3.orderIdx = 1
        self.t4.orderIdx = 1
        self.t5.orderIdx = 2
        self.t6.orderIdx = 3
        self.t7.orderIdx = 4
        self.t8.orderIdx = 6
        
        self.t1.cost = 5.0
        self.t4.cost = 1.0
        self.t5.cost = 1.0
        self.t6.cost = 1.0
        self.t7.cost = 1.0
        self.t1.completion = 5.0
        self.t4.completion = 1.0
        self.t5.completion = 1.0
        self.t6.completion = 1.0
        self.t7.completion = 2.0
        self.t1.save()
        self.t2.save()
        self.t3.save()
        self.t4.save()
        self.t5.save()
        self.t6.save()
        self.t7.save()
        self.t8.save()
        
        
    def test_depth_root(self):
        """
        Test depth method for a root
        """
        self.assertEqual(self.t1.depth(), 0)
        
    def test_depth_1_level(self):
        """
        Test depth method a lvl 1 task
        """
        self.assertEqual(self.t2.depth(), 1)
        
    def test_depth_general(self):
        """
        Test depth method
        """
        self.assertEqual(self.t3.depth(), 2)
        self.assertEqual(self.t4.depth(), 3)
        self.assertEqual(self.t5.depth(), 3)
        
    def test_root_root(self):
        """
        Test root method for a root
        """
        self.assertEqual(self.t1.root(),self.t1)
        
    def test_root_1_level(self):
        """
        Test root method a lvl 1 task
        """
        self.assertEqual(self.t2.root(),self.t1)
        
    def test_root_1_general(self):
        """
        Test root method
        """
        self.assertEqual(self.t3.root(),self.t1)
        self.assertEqual(self.t4.root(),self.t1)
        self.assertEqual(self.t5.root(),self.t1)  
        
    def test_get_cost(self):
        self.assertEqual(self.t8.getCost(),0.0)
        self.assertEqual(self.t7.getCost(),1.0)
        self.assertEqual(self.t3.getCost(),4.0)
        self.assertEqual(self.t2.getCost(),4.0)
                  
    def test_get_completition(self):
        #self.assertEqual(Task().getCompletion(),0.0)
        self.t1.cost = 1.0
        self.t4.cost = 10.0
        self.t5.cost = 10.0
        self.t6.cost = 0.0
        self.t7.cost = 10.0
        self.t8.cost = 10.0
        self.t1.completion = 33.0
        self.t4.completion = 100.0
        self.t5.completion = 0.0
        self.t6.completion = 100.0
        self.t7.completion = 50.0        
        self.t8.completion = 0.0 
        self.t1.save()
        self.t2.save()
        self.t3.save()
        self.t4.save()
        self.t5.save()
        self.t6.save()
        self.t7.save()
        self.t8.save()               
        
        self.assertEqual(self.t8.getCompletion(),0.0)
        self.assertEqual(self.t6.getCompletion(),100.0)
        self.assertEqual(self.t7.getCompletion(),50.0)
        self.assertEqual(self.t3.getCompletion(),37.5)
        self.assertEqual(self.t2.getCompletion(),37.5)
    
         
        
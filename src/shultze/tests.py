"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from communities.models import Community
from users.models import OCUser
from issues.models import Issue
from shultze.models import IssuesGraph, IssueEdge

def user_vote(community_id, current_vote, prev_vote=[]):
    try:
        g = IssuesGraph.objects.get(community_id=community_id)
    except IssuesGraph.DoesNotExist:
        g = IssuesGraph.objects.create(community_id=community_id)
        g.initialize_graph()
    if prev_vote:
        g.add_ballots(prev_vote,reverse=True)
    g.add_ballots(current_vote)

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class GraphToResults(TestCase):
    def setUp(self):
        com = Community.objects.create(name='com1')
        usr = OCUser.objects.create_user('a@b.com')
        graph = IssuesGraph.objects.create(community=com)

    def test_simple_example(self):
        """Check basic logic from graph to Schulze NPR"""
        
        com = Community.objects.get(name='com1')
        usr = OCUser.objects.get(email='a@b.com')
        graph = IssuesGraph.objects.get(community=com)
        
        #create issues
        issue_a = Issue.objects.create(community=com, created_by=usr, title='issue_a')
        issue_b = Issue.objects.create(community=com, created_by=usr, title='issue_b')
        issue_c = Issue.objects.create(community=com, created_by=usr, title='issue_c')
        
        #add issues as graph nodes
        graph.add_node(issue_a)
        graph.add_node(issue_b)
        graph.add_node(issue_c)

        #update weights on graph's edges
        edge = IssueEdge.objects.get(graph=graph, from_node=issue_a, to_node=issue_b)
        edge.weight = 8
        edge.save()
        edge = IssueEdge.objects.get(graph=graph, from_node=issue_b, to_node=issue_a)
        edge.weight = 3
        edge.save()
        edge = IssueEdge.objects.get(graph=graph, from_node=issue_a, to_node=issue_c)
        edge.weight = 3
        edge.save()
        edge = IssueEdge.objects.get(graph=graph, from_node=issue_c, to_node=issue_a)
        edge.weight = 4
        edge.save()
        edge = IssueEdge.objects.get(graph=graph, from_node=issue_b, to_node=issue_c)
        edge.weight = 6
        edge.save()
        edge = IssueEdge.objects.get(graph=graph, from_node=issue_c, to_node=issue_b)
        edge.weight = 3
        edge.save()
        
        #calculate results
        output = graph.get_schulze_npr_results()

        # Run tests
        self.assertEqual(output, {
            'candidates': set([issue_a.id, issue_b.id, issue_c.id]),
            'rounds': [{'winner': issue_a.id}, {'winner': issue_b.id}, {'winner': issue_c.id}],
            'order': [issue_a.id, issue_b.id, issue_c.id]
        })

class BallotsToResults(TestCase):
    def setUp(self):
        com = Community.objects.create(name='com1')
        usr = OCUser.objects.create_user('a@b.com')
        graph = IssuesGraph.objects.create(community=com)

    def test_single_voter(self):
        """Check basic logic from ballot to Schulze NPR"""
        
        com = Community.objects.get(name='com1')
        usr = OCUser.objects.get(email='a@b.com')
        graph = IssuesGraph.objects.get(community=com)
        
        #create issues
        issue_a = Issue.objects.create(community=com, created_by=usr, title='issue_a')
        issue_b = Issue.objects.create(community=com, created_by=usr, title='issue_b')
        issue_c = Issue.objects.create(community=com, created_by=usr, title='issue_c')
        issue_d = Issue.objects.create(community=com, created_by=usr, title='issue_d')
        issue_e = Issue.objects.create(community=com, created_by=usr, title='issue_e')
        
        #add issues as graph nodes
        graph.add_node(issue_a)
        graph.add_node(issue_b)
        graph.add_node(issue_c)
        graph.add_node(issue_d)
        graph.add_node(issue_e)

        # Generate data
        input = [
            {"count":1, "ballot":[[issue_a.id], [issue_b.id], [issue_c.id], [issue_d.id], [issue_e.id]]},
        ]
        # add ballots to graph
        graph.add_ballots(input)
        
        #calculate results
        output = graph.get_schulze_npr_results()

        # Run tests
        self.assertEqual(output, {
            'order': [issue_a.id, issue_b.id, issue_c.id, issue_d.id, issue_e.id],
            'candidates': set([issue_a.id, issue_b.id, issue_c.id, issue_d.id, issue_e.id]),
            'rounds': [
                {'winner': issue_a.id},
                {'winner': issue_b.id},
                {'winner': issue_c.id},
                {'winner': issue_d.id},
                {'winner': issue_e.id}
            ]
        })

    def test_nonproportionality(self):
        """Check basic logic from ballot to Schulze NPR"""
        
        com = Community.objects.get(name='com1')
        usr = OCUser.objects.get(email='a@b.com')
        graph = IssuesGraph.objects.get(community=com)
        
        #create issues
        issue_a = Issue.objects.create(community=com, created_by=usr, title='issue_a')
        issue_b = Issue.objects.create(community=com, created_by=usr, title='issue_b')
        issue_c = Issue.objects.create(community=com, created_by=usr, title='issue_c')
        issue_d = Issue.objects.create(community=com, created_by=usr, title='issue_d')
        issue_e = Issue.objects.create(community=com, created_by=usr, title='issue_e')
        
        #add issues as graph nodes
        graph.add_node(issue_a)
        graph.add_node(issue_b)
        graph.add_node(issue_c)
        graph.add_node(issue_d)
        graph.add_node(issue_e)

        # Generate data
        input = [
            {"count":2, "ballot":[[issue_a.id], [issue_b.id], [issue_c.id], [issue_d.id], [issue_e.id]]},
            {"count":1, "ballot":[[issue_e.id], [issue_d.id], [issue_c.id], [issue_b.id], [issue_a.id]]},
        ]
        # add ballots to graph
        graph.add_ballots(input)
        
        #calculate results
        output = graph.get_schulze_npr_results()

        # Run tests
        self.assertEqual(output, {
            'order': [issue_a.id, issue_b.id, issue_c.id, issue_d.id, issue_e.id],
            'candidates': set([issue_a.id, issue_b.id, issue_c.id, issue_d.id, issue_e.id]),
            'rounds': [
                {'winner': issue_a.id},
                {'winner': issue_b.id},
                {'winner': issue_c.id},
                {'winner': issue_d.id},
                {'winner': issue_e.id}
            ]
        })


class BallotsIO(TestCase):
    def setUp(self):
        com = Community.objects.create(name='com1')
        usr = OCUser.objects.create_user('a@b.com')
        graph = IssuesGraph.objects.create(community=com)

    def test_vote_reversal(self):
        """Check voting reversibility"""
        
        com = Community.objects.get(name='com1')
        usr = OCUser.objects.get(email='a@b.com')
        graph = IssuesGraph.objects.get(community=com)
        
        #create issues
        issue_a = Issue.objects.create(community=com, created_by=usr, title='issue_a')
        issue_b = Issue.objects.create(community=com, created_by=usr, title='issue_b')
        issue_c = Issue.objects.create(community=com, created_by=usr, title='issue_c')
        issue_d = Issue.objects.create(community=com, created_by=usr, title='issue_d')
        issue_e = Issue.objects.create(community=com, created_by=usr, title='issue_e')
        
        #add issues as graph nodes
        graph.add_node(issue_a)
        graph.add_node(issue_b)
        graph.add_node(issue_c)
        graph.add_node(issue_d)
        graph.add_node(issue_e)

        # Generate data
        input = [
            {"count":1, "ballot":[[issue_a.id], [issue_b.id], [issue_c.id], [issue_d.id], [issue_e.id]]},
        ]
        input_prev = [
            {"count":1, "ballot":[[issue_a.id], [issue_b.id], [issue_c.id], [issue_d.id], [issue_e.id]]},
        ]
        
        # add ballots to graph
        user_vote(com,input,input_prev)
        
        #calculate results
        output = graph.get_edges_dict()

        # Run tests
        self.assertEqual(output, {(1, 2): 0,
            (1, 3): 0,
            (1, 4): 0,
            (1, 5): 0,
            (2, 1): 0,
            (2, 3): 0,
            (2, 4): 0,
            (2, 5): 0,
            (3, 1): 0,
            (3, 2): 0,
            (3, 4): 0,
            (3, 5): 0,
            (4, 1): 0,
            (4, 2): 0,
            (4, 3): 0,
            (4, 5): 0,
            (5, 1): 0,
            (5, 2): 0,
            (5, 3): 0,
            (5, 4): 0}
        )


class Itamar(TestCase):
    def setUp(self):
        com = Community.objects.create(name='com1')
        usr = OCUser.objects.create_user('a@b.com')
        graph = IssuesGraph.objects.create(community=com)

    def test_vote_reversal(self):
        """Check voting reversibility"""
        
        com = Community.objects.get(name='com1')
        usr = OCUser.objects.get(email='a@b.com')
        graph = IssuesGraph.objects.get(community=com)
        
        #create issues
        issue_a = Issue.objects.create(community=com, created_by=usr, title='issue_a')
        issue_b = Issue.objects.create(community=com, created_by=usr, title='issue_b')
        issue_c = Issue.objects.create(community=com, created_by=usr, title='issue_c')
        issue_d = Issue.objects.create(community=com, created_by=usr, title='issue_d')
        issue_e = Issue.objects.create(community=com, created_by=usr, title='issue_e')
        
        #add issues as graph nodes
        graph.add_node(issue_a)
        graph.add_node(issue_b)
        graph.add_node(issue_c)
        graph.add_node(issue_d)
        graph.add_node(issue_e)
        
        # Generate data
        input=[
            {'count': 1, 'ballot': [[issue_b.id, issue_c.id, issue_d.id, issue_e.id], [issue_a.id]]},
            {'count': 1, 'ballot': [[issue_d.id], [issue_a.id, issue_b.id, issue_c.id, issue_e.id]]},
        ]
        
        # add ballots to graph
        user_vote(com,input)

        #calculate results
        output = graph.get_edges_dict()
        print output
        # Run tests
        self.assertEqual(output, {(1, 2): 0,
            (1, 3): 0,
            (1, 4): 0,
            (1, 5): 0,
            (2, 1): 0,
            (2, 3): 0,
            (2, 4): 0,
            (2, 5): 0,
            (3, 1): 0,
            (3, 2): 0,
            (3, 4): 0,
            (3, 5): 0,
            (4, 1): 0,
            (4, 2): 0,
            (4, 3): 0,
            (4, 5): 0,
            (5, 1): 0,
            (5, 2): 0,
            (5, 3): 0,
            (5, 4): 0}
        )


class Itamar(TestCase):
    def setUp(self):
        com = Community.objects.create(name='com1')
        usr = OCUser.objects.create_user('a@b.com')
        graph = IssuesGraph.objects.create(community=com)

    def test_vote_reversal(self):
        """Check voting reversibility"""
        
        com = Community.objects.get(name='com1')
        usr = OCUser.objects.get(email='a@b.com')
        graph = IssuesGraph.objects.get(community=com)
        
        #create issues
        issue_a = Issue.objects.create(community=com, created_by=usr, title='issue_a')
        issue_b = Issue.objects.create(community=com, created_by=usr, title='issue_b')
        issue_c = Issue.objects.create(community=com, created_by=usr, title='issue_c')
        issue_d = Issue.objects.create(community=com, created_by=usr, title='issue_d')
        issue_e = Issue.objects.create(community=com, created_by=usr, title='issue_e')
        
        #add issues as graph nodes
        graph.add_node(issue_a)
        graph.add_node(issue_b)
        graph.add_node(issue_c)
        graph.add_node(issue_d)
        graph.add_node(issue_e)
        
        # Generate data
        input=[
            {'count': 1, 'ballot': [[issue_b.id, issue_c.id, issue_d.id, issue_e.id], [issue_a.id]]},
            {'count': 1, 'ballot': [[issue_d.id], [issue_a.id, issue_b.id, issue_c.id, issue_e.id]]},
            {'count': 1, 'ballot': [[issue_a.id], [issue_b.id, issue_c.id, issue_d.id, issue_e.id]]}
        ]
        
        # add ballots to graph
        #user_vote(com,input)
        for v in input:
            user_vote(com,[v])
            print graph.get_edges_dict()
        #calculate results
        output = graph.get_edges_dict()
        print output
        # Run tests
        self.assertEqual(output, {(1, 2): 0,
            (1, 3): 0,
            (1, 4): 0,
            (1, 5): 0,
            (2, 1): 0,
            (2, 3): 0,
            (2, 4): 0,
            (2, 5): 0,
            (3, 1): 0,
            (3, 2): 0,
            (3, 4): 0,
            (3, 5): 0,
            (4, 1): 0,
            (4, 2): 0,
            (4, 3): 0,
            (4, 5): 0,
            (5, 1): 0,
            (5, 2): 0,
            (5, 3): 0,
            (5, 4): 0}
        )

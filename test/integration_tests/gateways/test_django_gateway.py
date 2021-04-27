"""Test postgres gateway"""

import datetime as dt
from unittest.mock import patch

from dateutil.tz import tzlocal, gettz
from django.test import TestCase

from spaced_repetition.domain.problem import Difficulty, Problem
from spaced_repetition.domain.problem_log import (ProblemLogCreator, Result)
from spaced_repetition.domain.tag import Tag, TagCreator
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import (
    Problem as OrmProblem,
    ProblemLog as OrmProblemLog,
    Tag as OrmTag)


class TestProblemCreation(TestCase):
    def setUp(self):
        OrmTag.objects.create(name='tag1')

        self.problem = Problem(difficulty=Difficulty.EASY,
                               name='testname',
                               problem_id=99,
                               tags=['tag1'],
                               url='https://testurl.com')

    def test_create_problem(self):
        dgw = DjangoGateway()
        problem = dgw.create_problem(problem=self.problem)
        self.assertIsInstance(problem, Problem)
        self.assertEqual(problem.name, 'testname')

        orm_problems = OrmProblem.objects.all()
        self.assertEqual(orm_problems.count(), 1)

        orm_problem = orm_problems.first()
        self.assertEqual(orm_problem.name, 'testname')
        self.assertNotEqual(orm_problem.pk, 99)  # pk is independent of problem_id
        self.assertEqual(orm_problem.url, 'https://testurl.com')
        self.assertEqual([t.name for t in orm_problem.tags.all()], ['tag1'])


class TestProblemQuerying(TestCase):
    def setUp(self):
        # create tags
        tag_1 = OrmTag.objects.create(name='tag1')
        tag_2 = OrmTag.objects.create(name='tag2')
        tag_3 = OrmTag.objects.create(name='tag3')
        tag_4 = OrmTag.objects.create(name='tag4')
        OrmTag.objects.create(name='additional_tag')  # not linked to problem

        # create problems and match to tags
        prob_1 = OrmProblem.objects.create(difficulty=1, name='prob_1')
        prob_1.tags.set([tag_1, tag_2])

        prob_2 = OrmProblem.objects.create(difficulty=1, name='prob_2')
        prob_2.tags.set([tag_1, tag_2])

        prob_single_tag = OrmProblem.objects.create(difficulty=1,
                                                    name='single_tag')
        prob_single_tag.tags.add(tag_3)

        prob_many_tags = OrmProblem.objects.create(difficulty=1,
                                                   name='many_tags')
        prob_many_tags.tags.set([tag_1, tag_2, tag_3, tag_4])

    def test_query_all(self):
        self.assertEqual(4, len(DjangoGateway._query_problems(name=None)))

    def test_query_filter_by_name(self):
        self.assertEqual(1, len(DjangoGateway._query_problems(name='prob_1')))

    def test_query_filter_by_substring(self):
        self.assertEqual(2, len(DjangoGateway._query_problems(name_substr='pro')))
        self.assertEqual(1, len(DjangoGateway._query_problems(name_substr='_1')))

    def test_query_filter_for_tags_all(self):
        required_tags = ['tag1', 'tag2']

        res = DjangoGateway._query_problems(tags_all=required_tags)

        self.assertEqual(len(res), 3)
        self.assertEqual(sorted([prob.name for prob in res]),
                         ['many_tags', 'prob_1', 'prob_2'])

    def test_query_filter_for_tags_any(self):
        tags = ['tag3', 'tag4']

        res = DjangoGateway._query_problems(tags_any=tags)

        self.assertEqual(len(res), 2)
        self.assertEqual(sorted([prob.name for prob in res]),
                         ['many_tags', 'single_tag'])

    def test_get_problems_filter_by_empty_params(self):
        params = [
            ({'name': ''}, []),
        ]

        for kwargs, expected_res in params:
            with self.subTest(kwargs=kwargs, expected_res=expected_res):
                res = DjangoGateway.get_problems(**kwargs)
                self.assertEqual(res, expected_res)

    def test_query_combined(self):
        res = DjangoGateway._query_problems(
            name_substr='b',  # exclude 'many_tags'
            tags_all=['tag1', 'tag2'])  # exclude 'single_tag'

        self.assertEqual(['prob_1', 'prob_2'],
                         sorted([p.name for p in res]))


class TestProblemGetting(TestCase):
    def setUp(self):
        self.tag_1 = OrmTag.objects.create(name='tag1')
        self.tag_2 = OrmTag.objects.create(name='tag2')
        for name in ['name2', 'name1']:
            prob = OrmProblem.objects.create(difficulty=1,
                                             name=name,
                                             url='www.test_url.com')
            prob.tags.set([self.tag_1, self.tag_2])

    def test_format_problems(self):
        problems = DjangoGateway._format_problems(OrmProblem.objects.all())

        self.assertIsInstance(problems, list)
        self.assertEqual(2, len(problems))
        self.assertIsInstance(problems[0], Problem)

        self.assertEqual(problems[0].name, 'name2')
        self.assertEqual(problems[0].difficulty, Difficulty.EASY)
        self.assertEqual(problems[0].problem_id, OrmProblem.objects.first().pk)
        self.assertEqual(problems[0].tags, ['tag1', 'tag2'])
        self.assertEqual(problems[0].url, 'www.test_url.com')

    def test_get_problems(self):
        problems = DjangoGateway.get_problems()
        self.assertEqual(2, len(problems))

    def test_get_problems_filter_tags_all_and_name(self):
        res = DjangoGateway.get_problems(name_substr='e',
                                         tags_all=['tag1', 'tag2'])

        self.assertEqual(['name1', 'name2'],
                         sorted([p.name for p in res]))

    def test_problem_exists_via_name(self):
        self.assertTrue(DjangoGateway.problem_exists(name='name1'))

    def test_problem_does_not_exist_via_name(self):
        self.assertFalse(DjangoGateway.problem_exists(name='not there'))

    def test_problem_exists_via_problem_id(self):
        problem_id = OrmProblem.objects.last().pk

        self.assertTrue(DjangoGateway.problem_exists(problem_id=problem_id))

    def test_problem_does_not_exist_problem_id(self):
        self.assertFalse(DjangoGateway.problem_exists(problem_id=99999999))

    def test_problem_exists_raises_when_no_input(self):
        with self.assertRaises(ValueError) as context:
            DjangoGateway.problem_exists()

        self.assertEqual(str(context.exception),
                         "Supply exactly one of 'problem_id' or 'name'!")

    def test_problem_exists_raises_when_all_inputs(self):
        with self.assertRaises(ValueError) as context:
            DjangoGateway.problem_exists(name='test', problem_id=1)

        self.assertEqual(str(context.exception),
                         "Supply exactly one of 'problem_id' or 'name'!")


class TestProblemLogCreation(TestCase):
    def setUp(self):
        self.problem = OrmProblem.objects.create(
            difficulty=Difficulty.EASY.value,
            name='testname',
            url='https://testurl.com')

        self.tag = OrmTag.objects.create(name='test-tag')

    def test_create_problem_log(self):
        dgw = DjangoGateway()
        ts = dt.datetime(2021, 3, 6, 10, 0, tzinfo=tzlocal())
        log = ProblemLogCreator.create(
            comment='test comment',
            problem_id=1,
            result=Result.SOLVED_OPTIMALLY_IN_UNDER_25,
            tags=[TagCreator.create(name=self.tag.name)],
            timestamp=ts)

        dgw.create_problem_log(problem_log=log)

        self.assertEqual(OrmProblemLog.objects.count(), 1)

        orm_log = OrmProblemLog.objects.first()
        self.assertEqual(orm_log.problem.name, 'testname')
        self.assertEqual(orm_log.result,
                         Result.SOLVED_OPTIMALLY_IN_UNDER_25.value)
        self.assertEqual(orm_log.tags.count(), 1)
        self.assertEqual(orm_log.tags.first().name, 'test-tag')
        self.assertEqual(orm_log.timestamp, ts)
        self.assertEqual(orm_log.comment, 'test comment')


class TestProblemLogQuerying(TestCase):
    def setUp(self):
        # create Problem
        self.prob = OrmProblem.objects.create(difficulty=1,
                                              name='test_problem',
                                              url='www.test_url.com')
        prob_2 = OrmProblem.objects.create(difficulty=2,
                                           name='test_problem_2',
                                           url='www.test_url_2.com')
        self.tag = OrmTag.objects.create(name='tag_1')

        # create ProblemLogs
        self.problem_log = OrmProblemLog.objects.create(
            comment='test comment 123!',
            problem_id=self.prob.pk,
            result=Result.SOLVED_SUBOPTIMALLY.value,
            timestamp=dt.datetime(2021, 1, 10, 10, tzinfo=gettz('UTC')))
        self.problem_log.tags.add(self.tag)

        log_2 = OrmProblemLog.objects.create(
            problem_id=self.prob.pk,
            result=Result.SOLVED_OPTIMALLY_IN_UNDER_25.value,
            timestamp=dt.datetime(2021, 1, 20, 10, tzinfo=gettz('UTC')))
        log_2.tags.add(self.tag)

        log_3 = OrmProblemLog.objects.create(
            problem_id=prob_2.pk,
            result=Result.SOLVED_OPTIMALLY_WITH_HINT.value,
            timestamp=dt.datetime(2021, 1, 15, 10, tzinfo=gettz('UTC')))
        log_3.tags.add(self.tag)

    def test_query_all(self):
        self.assertEqual(3, len(DjangoGateway._query_problem_logs()))

    def test_query_for_problem(self):
        self.assertEqual(
            2,
            len(DjangoGateway._query_problem_logs(problem_ids=[self.prob.pk])))

    def test_format_problem_logs(self):
        expected_res = [
            ProblemLogCreator.create(
                comment='test comment 123!',
                problem_id=self.prob.pk,
                result=Result.SOLVED_SUBOPTIMALLY,
                tags=[TagCreator.create(name='tag_1', tag_id=self.tag.pk)],
                timestamp=dt.datetime(2021, 1, 10, 10, tzinfo=gettz('UTC')))]

        problem_log_qs = OrmProblemLog.objects.filter(pk=self.problem_log.pk)

        res = DjangoGateway._format_problem_logs(problem_log_qs=problem_log_qs)

        self.assertEqual(expected_res, res)

    @patch.object(DjangoGateway, attribute='_format_problem_logs')
    @patch.object(DjangoGateway, attribute='_query_problem_logs')
    def test_get_problem_logs(self, mock_query_problem_logs,
                              mock_format_problem_logs):
        mock_query_problem_logs.return_value = 'fake_problems'

        DjangoGateway.get_problem_logs()

        mock_query_problem_logs.assert_called_once_with(problem_ids=None)
        mock_format_problem_logs.assert_called_once_with(
            problem_log_qs='fake_problems')


class TestTagCreation(TestCase):
    def test_create_tag(self):
        tag = DjangoGateway.create_tag(Tag(name='tag1'))
        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.name, 'tag1')

        tags = OrmTag.objects.all()
        self.assertEqual(tags.count(), 1)
        self.assertEqual(tags[0].name, 'tag1')


class TestTagGetting(TestCase):
    def setUp(self):
        OrmTag.objects.create(name='tag2')
        OrmTag.objects.create(name='Tag1')
        OrmTag.objects.create(name='t3')

    def test_query_tags(self):
        tags = DjangoGateway._query_tags(names=None, sub_str=None)

        self.assertIsInstance(tags[0], OrmTag)
        self.assertEqual([t.name for t in tags], ['tag2', 'Tag1', 't3'])

    def test_query_tag_filter_sub_str(self):
        tags = DjangoGateway._query_tags(names=None, sub_str='ag')

        self.assertEqual([t.name for t in tags], ['tag2', 'Tag1'])

    def test_query_tag_filter_names(self):
        tags = DjangoGateway._query_tags(names=['Tag1', 't3'], sub_str=None)

        self.assertEqual([t.name for t in tags], ['Tag1', 't3'])

    def test_format_tag(self):
        tags = DjangoGateway._format_tags(tags=OrmTag.objects.all())

        self.assertEqual(len(tags), 3)
        self.assertIsInstance(tags, list)
        self.assertIsInstance(tags[0], Tag)

        self.assertEqual([t.name for t in tags], ['tag2', 'Tag1', 't3'])
        self.assertEqual([t.tag_id for t in tags],
                         [OrmTag.objects.get(name=t.name).pk for t in tags])

    def test_get_tags(self):
        tags = DjangoGateway.get_tags()

        self.assertIsInstance(tags[0], Tag)
        self.assertEqual(len(tags), 3)

    def test_tag_exists(self):
        self.assertTrue(DjangoGateway.tag_exists(name='Tag1'))

    def test_tag_does_not_exist(self):
        self.assertFalse(DjangoGateway.tag_exists(name='not there'))

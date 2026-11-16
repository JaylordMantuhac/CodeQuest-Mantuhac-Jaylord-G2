from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Challenge, Submission


User = get_user_model()


class ChallengeFlowTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='StudentPassword123!', role=User.ROLE_STUDENT,
        )
        self.other_student = User.objects.create_user(
            username='other_student', email='other@example.com',
            password='OtherPassword123!', role=User.ROLE_STUDENT,
        )
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='AdminPassword123!', role=User.ROLE_ADMIN, is_staff=True,
        )
        self.challenge = Challenge.objects.create(
            title='Print a greeting',
            description='Print the exact greeting shown in the expected output.',
            category='variables', difficulty='easy', language='Python',
            expected_output='Hello, CodeQuest!', created_by=self.admin,
        )

    def test_challenge_list_requires_login(self):
        response = self.client.get(reverse('challenge_list'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('challenge_list')}")

    def test_student_can_submit_and_submission_is_persisted(self):
        self.client.login(username='student', password='StudentPassword123!')
        response = self.client.post(
            reverse('challenge_submit', args=[self.challenge.pk]),
            {'answer': 'Hello, CodeQuest!'},
        )
        self.assertRedirects(response, reverse('challenge_detail', args=[self.challenge.pk]))
        submission = Submission.objects.get(student=self.student, challenge=self.challenge)
        self.assertTrue(submission.is_correct)

    def test_wrong_answer_is_recorded_as_incorrect(self):
        self.client.login(username='student', password='StudentPassword123!')
        self.client.post(
            reverse('challenge_submit', args=[self.challenge.pk]),
            {'answer': 'A different answer'},
        )
        submission = Submission.objects.get(student=self.student, challenge=self.challenge)
        self.assertFalse(submission.is_correct)

    def test_student_sees_only_own_submissions(self):
        own_submission = Submission.objects.create(
            challenge=self.challenge, student=self.student,
            answer='Hello, CodeQuest!', is_correct=True,
        )
        Submission.objects.create(
            challenge=self.challenge, student=self.other_student,
            answer='Private answer', is_correct=False,
        )
        self.client.login(username='student', password='StudentPassword123!')
        response = self.client.get(reverse('my_submissions'))
        self.assertContains(response, own_submission.answer)
        self.assertNotContains(response, 'Private answer')
        self.assertEqual(list(response.context['submissions']), [own_submission])

    def test_student_cannot_create_challenge(self):
        self.client.login(username='student', password='StudentPassword123!')
        response = self.client.get(reverse('challenge_create'), follow=True)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))
        self.assertContains(response, 'Access Denied')

    def test_admin_can_create_update_and_delete_challenge(self):
        self.client.login(username='admin', password='AdminPassword123!')
        create_data = {
            'title': 'Add two numbers', 'description': 'Return the sum of two numbers.',
            'category': 'functions', 'difficulty': 'easy', 'language': 'Python',
            'expected_output': '3',
        }
        create_response = self.client.post(reverse('challenge_create'), create_data)
        created = Challenge.objects.get(title='Add two numbers')
        self.assertRedirects(create_response, reverse('challenge_list'))
        self.assertEqual(created.created_by, self.admin)
        update_response = self.client.post(
            reverse('challenge_edit', args=[created.pk]),
            {**create_data, 'title': 'Add two integers'},
        )
        self.assertRedirects(update_response, reverse('challenge_detail', args=[created.pk]))
        self.assertTrue(Challenge.objects.filter(pk=created.pk, title='Add two integers').exists())
        delete_response = self.client.post(reverse('challenge_delete', args=[created.pk]))
        self.assertRedirects(delete_response, reverse('challenge_list'))
        self.assertFalse(Challenge.objects.filter(pk=created.pk).exists())

    def test_empty_answer_is_rejected(self):
        self.client.login(username='student', password='StudentPassword123!')
        response = self.client.post(
            reverse('challenge_submit', args=[self.challenge.pk]), {'answer': '   '},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Submission.objects.exists())
        self.assertContains(response, 'Answer cannot be empty.')

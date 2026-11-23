from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class AccountRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')

    def test_registration_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_successful_student_registration(self):
        data = {
            'first_name': 'Jaylord',
            'last_name': 'Mantuhac',
            'username': 'jaylord_coder',
            'email': 'jaylord@example.com',
            'role': User.ROLE_STUDENT,
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:login'))

        user = User.objects.filter(username='jaylord_coder').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'jaylord@example.com')
        self.assertEqual(user.role, User.ROLE_STUDENT)
        self.assertNotEqual(user.password, 'SecurePassword123!')
        self.assertTrue(user.check_password('SecurePassword123!'))

        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)

    def test_public_registration_cannot_grant_admin_role(self):
        data = {
            'first_name': 'Admin',
            'last_name': 'Master',
            'username': 'quest_admin',
            'email': 'admin@codequest.dev',
            'role': User.ROLE_ADMIN,
            'password': 'AdminPassword123!',
            'confirm_password': 'AdminPassword123!',
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='quest_admin').exists())
        self.assertFormError(response.context['form'], 'role', 'Select a valid choice. admin is not one of the available choices.')

    def test_registration_password_mismatch(self):
        data = {
            'first_name': 'Mismatch',
            'last_name': 'Tester',
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'role': User.ROLE_STUDENT,
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'confirm_password', 'Passwords do not match. Please re-enter.')
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())

    def test_registration_duplicate_username(self):
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='Password123!'
        )
        data = {
            'first_name': 'Duplicate',
            'last_name': 'User',
            'username': 'existing_user',
            'email': 'new_email@example.com',
            'role': User.ROLE_STUDENT,
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'This username is already taken. Please choose another one.')

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username='user_one',
            email='duplicate@example.com',
            password='Password123!'
        )
        data = {
            'first_name': 'User',
            'last_name': 'Two',
            'username': 'user_two',
            'email': 'duplicate@example.com',
            'role': User.ROLE_STUDENT,
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email address already exists.')


class AccountLoginLogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='StudentPassword123!',
            role=User.ROLE_STUDENT,
            first_name='Student',
            last_name='One'
        )

    def test_login_with_username_success(self):
        response = self.client.post(self.login_url, {
            'username_or_email': 'student1',
            'password': 'StudentPassword123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_with_email_success(self):
        response = self.client.post(self.login_url, {
            'username_or_email': 'student1@example.com',
            'password': 'StudentPassword123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_invalid_password(self):
        response = self.client.post(self.login_url, {
            'username_or_email': 'student1',
            'password': 'WrongPassword999!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username/email or password')

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username_or_email': 'nonexistent_coder',
            'password': 'AnyPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username/email or password')

    def test_logout_ends_session(self):
        self.client.login(username='student1', password='StudentPassword123!')
        response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.login_url)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_required_protection(self):
        protected_urls = [
            reverse('accounts:student_dashboard'),
            reverse('accounts:admin_dashboard'),
            reverse('accounts:profile'),
            reverse('accounts:profile_edit'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(self.login_url))


class RoleBasedDashboardAndUrlTamperingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='player_alice',
            email='alice@example.com',
            password='AlicePassword123!',
            role=User.ROLE_STUDENT
        )
        self.admin = User.objects.create_user(
            username='admin_bob',
            email='bob@example.com',
            password='BobPassword123!',
            role=User.ROLE_ADMIN,
            is_staff=True
        )

    def test_student_dashboard_access_allowed_for_student(self):
        self.client.login(username='player_alice', password='AlicePassword123!')
        response = self.client.get(reverse('accounts:student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/student_dashboard.html')
        self.assertContains(response, 'Quest Adventurer / Student')

    def test_admin_dashboard_access_allowed_for_admin(self):
        self.client.login(username='admin_bob', password='BobPassword123!')
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/admin_dashboard.html')
        self.assertContains(response, 'System Command Center')

    def test_url_tampering_student_cannot_access_admin_dashboard(self):
        self.client.login(username='player_alice', password='AlicePassword123!')
        response = self.client.get(reverse('accounts:admin_dashboard'), follow=True)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))
        self.assertContains(response, 'Access Denied')

    def test_url_tampering_admin_cannot_access_student_dashboard(self):
        self.client.login(username='admin_bob', password='BobPassword123!')
        response = self.client.get(reverse('accounts:student_dashboard'), follow=True)
        self.assertRedirects(response, reverse('accounts:admin_dashboard'))
        self.assertContains(response, 'Access Denied')

    def test_dashboard_redirect_routes_by_role(self):
        self.client.login(username='player_alice', password='AlicePassword123!')
        res_student = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(res_student, reverse('accounts:student_dashboard'))
        self.client.logout()

        self.client.login(username='admin_bob', password='BobPassword123!')
        res_admin = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(res_admin, reverse('accounts:admin_dashboard'))


class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='coder_one',
            email='coder1@example.com',
            password='CoderPassword123!',
            role=User.ROLE_STUDENT,
            first_name='Jaylord',
            last_name='Mantuhac'
        )
        self.user2 = User.objects.create_user(
            username='coder_two',
            email='coder2@example.com',
            password='CoderPassword123!',
            role=User.ROLE_STUDENT,
            first_name='Second',
            last_name='User'
        )

    def test_view_own_profile(self):
        self.client.login(username='coder_one', password='CoderPassword123!')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'coder_one')
        self.assertContains(response, 'coder1@example.com')
        self.assertContains(response, 'Jaylord Mantuhac')

    def test_update_profile_details(self):
        self.client.login(username='coder_one', password='CoderPassword123!')
        edit_url = reverse('accounts:profile_edit')

        update_data = {
            'first_name': 'Jaylord Updated',
            'last_name': 'Mantuhac Updated',
            'email': 'jaylord_updated@example.com',
            'contact_number': '+63 912 345 6789',
            'specialization': 'Python & Django Architecture',
            'bio': 'Passionate coder competing in CodeQuest battles.',
        }

        response = self.client.post(edit_url, update_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:profile'))
        self.assertContains(response, 'Your profile details have been updated successfully!')

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Jaylord Updated')
        self.assertEqual(self.user1.last_name, 'Mantuhac Updated')
        self.assertEqual(self.user1.email, 'jaylord_updated@example.com')
        self.assertEqual(self.user1.profile.contact_number, '+63 912 345 6789')
        self.assertEqual(self.user1.profile.specialization, 'Python & Django Architecture')
        self.assertEqual(self.user1.profile.bio, 'Passionate coder competing in CodeQuest battles.')

    def test_update_profile_duplicate_email_rejected(self):
        self.client.login(username='coder_one', password='CoderPassword123!')
        edit_url = reverse('accounts:profile_edit')

        update_data = {
            'first_name': 'Jaylord',
            'last_name': 'Mantuhac',
            'email': 'coder2@example.com',
            'contact_number': '123456',
            'specialization': 'Web',
            'bio': 'Test bio',
        }

        response = self.client.post(edit_url, update_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['user_form'], 'email', 'This email address is already in use by another account.')

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from students.models import StudentProfile, Department

class AccountsAuthRBACTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an officer
        self.officer = User.objects.create_user(
            username='officertest',
            email='officer@test.com',
            password='password123',
            role=User.ROLE_OFFICER,
            is_staff=True
        )
        # Create a student
        self.student_user = User.objects.create_user(
            username='studenttest',
            email='student@test.com',
            password='password123',
            role=User.ROLE_STUDENT
        )
        dummy_file = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            registration_number='TESTREG001',
            department=Department.CSE,
            current_semester=7,
            cgpa=8.5,
            backlog_count=0,
            phone_number='9876543210',
            skills='Python, Django',
            resume=dummy_file
        )

    def test_student_registration_success(self):
        resume_file = SimpleUploadedFile("new_resume.pdf", b"%PDF-1.4 content", content_type="application/pdf")
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'New',
            'last_name': 'Candidate',
            'email': 'newcandidate@test.com',
            'username': 'newcandidate',
            'password': 'safePassword123',
            'password_confirm': 'safePassword123',
            'registration_number': 'REGNEW999',
            'department': Department.IT,
            'current_semester': '7',
            'cgpa': '8.25',
            'backlog_count': '0',
            'phone_number': '9123456789',
            'skills': 'Java, React',
            'resume': resume_file,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newcandidate').exists())
        new_u = User.objects.get(username='newcandidate')
        self.assertEqual(new_u.role, User.ROLE_STUDENT)
        self.assertTrue(hasattr(new_u, 'student_profile'))
        self.assertEqual(new_u.student_profile.registration_number, 'REGNEW999')

    def test_duplicate_email_registration_rejected(self):
        resume_file = SimpleUploadedFile("resume2.pdf", b"%PDF-1.4 content", content_type="application/pdf")
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'Dup',
            'last_name': 'Candidate',
            'email': 'student@test.com',  # already exists
            'username': 'dupusername',
            'password': 'password123',
            'password_confirm': 'password123',
            'registration_number': 'REGUNIQUE1',
            'department': Department.CSE,
            'current_semester': '7',
            'cgpa': '8.0',
            'backlog_count': '0',
            'phone_number': '9999999999',
            'skills': 'C++',
            'resume': resume_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)

    def test_duplicate_registration_number_rejected(self):
        resume_file = SimpleUploadedFile("resume3.pdf", b"%PDF-1.4 content", content_type="application/pdf")
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'Dup2',
            'last_name': 'Candidate',
            'email': 'uniqueemail@test.com',
            'username': 'uniqueuser2',
            'password': 'password123',
            'password_confirm': 'password123',
            'registration_number': 'TESTREG001',  # already exists
            'department': Department.CSE,
            'current_semester': '7',
            'cgpa': '8.0',
            'backlog_count': '0',
            'phone_number': '9999999999',
            'skills': 'C++',
            'resume': resume_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('registration_number', response.context['form'].errors)

    def test_login_and_role_redirect(self):
        # Student Login
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'studenttest',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertRedirects(login_res, reverse('dashboard:student'))

        self.client.logout()

        # Officer Login
        officer_login = self.client.post(reverse('accounts:login'), {
            'username': 'officertest',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(officer_login.status_code, 200)
        self.assertRedirects(officer_login, reverse('dashboard:officer'))

    def test_role_based_access_control(self):
        # 1. Unauthenticated access to officer dashboard
        res = self.client.get(reverse('dashboard:officer'))
        self.assertRedirects(res, reverse('accounts:login'))

        # 2. Student trying to access officer endpoint
        self.client.login(username='studenttest', password='password123')
        res_officer_page = self.client.get(reverse('jobs:create'))
        self.assertEqual(res_officer_page.status_code, 403)  # PermissionDenied

        # 3. Officer trying to access student-only endpoint
        self.client.logout()
        self.client.login(username='officertest', password='password123')
        res_student_page = self.client.get(reverse('students:profile'))
        self.assertEqual(res_student_page.status_code, 403)  # PermissionDenied

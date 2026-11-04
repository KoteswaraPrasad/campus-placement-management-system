from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from students.models import StudentProfile, Department
from companies.models import Company
from jobs.models import Job
from applications.models import Application, ApplicationStatus

class DashboardAndAnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.officer = User.objects.create_user(
            username='officer_dash', email='dash_off@test.com', password='password123',
            role=User.ROLE_OFFICER, is_staff=True
        )
        self.company = Company.objects.create(
            name='Alpha Corp', industry='IT', description='Alpha Tech',
            contact_person='HR', contact_email='hr@alpha.com', locations='Mumbai', is_active=True
        )

        today = timezone.now().date()
        self.job1 = Job.objects.create(
            title='Full Stack Developer', company=self.company, description='React + Django',
            location='Mumbai', min_cgpa=7.0, max_backlogs=0, eligible_departments='ALL',
            eligible_semesters='7,8', salary_package='9 LPA', opening_date=today - timedelta(days=2),
            deadline=today + timedelta(days=10), status='published', created_by=self.officer
        )
        self.job2 = Job.objects.create(
            title='DevOps Engineer', company=self.company, description='Docker + AWS',
            location='Mumbai', min_cgpa=8.0, max_backlogs=0, eligible_departments='ALL',
            eligible_semesters='7,8', salary_package='12 LPA', opening_date=today - timedelta(days=2),
            deadline=today + timedelta(days=10), status='published', created_by=self.officer
        )

        # Student 1 (CGPA 8.5)
        u1 = User.objects.create_user(
            username='dash_student1',
            email='dash1@test.com',
            password='password123',
            first_name='Aarav',
            last_name='Patel',
            role=User.ROLE_STUDENT
        )
        self.s1 = StudentProfile.objects.create(
            user=u1, registration_number='DASH_01', department=Department.CSE,
            current_semester=7, cgpa=8.5, backlog_count=0, phone_number='1234567890', skills='Python',
            resume=SimpleUploadedFile("r1.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        )

        # Student 2 (CGPA 6.5)
        u2 = User.objects.create_user(username='dash_student2', email='dash2@test.com', password='password123', role=User.ROLE_STUDENT)
        self.s2 = StudentProfile.objects.create(
            user=u2, registration_number='DASH_02', department=Department.IT,
            current_semester=7, cgpa=6.5, backlog_count=0, phone_number='1234567890', skills='Java',
            resume=SimpleUploadedFile("r2.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        )

        # Student 1 applied to Job 1 (Selected) and Job 2 (Selected) - MUST only count once in placed candidates!
        Application.objects.create(job=self.job1, student=self.s1, status=ApplicationStatus.SELECTED)
        Application.objects.create(job=self.job2, student=self.s1, status=ApplicationStatus.SELECTED)

    def test_student_dashboard_metrics(self):
        self.client.login(username='dash_student1', password='password123')
        response = self.client.get(reverse('dashboard:student'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['available_jobs_count'], 2)
        # Student 1 has CGPA 8.5 -> eligible for both jobs
        self.assertEqual(response.context['eligible_jobs_count'], 2)
        self.assertEqual(response.context['selected_count'], 2)

    def test_officer_dashboard_placement_rate_no_duplicate_counting(self):
        self.client.login(username='officer_dash', password='password123')
        response = self.client.get(reverse('dashboard:officer'))
        self.assertEqual(response.status_code, 200)

        # Total students: 2
        self.assertEqual(response.context['total_students'], 2)
        # Unique placed students: 1 (Student 1 has 2 selected offers, but counts as 1 placed candidate!)
        self.assertEqual(response.context['placed_students_count'], 1)
        # Placement rate: (1 / 2) * 100 = 50.0%
        self.assertEqual(response.context['placement_rate'], 50.0)

    def test_csv_export_applications(self):
        self.client.login(username='officer_dash', password='password123')
        response = self.client.get(reverse('dashboard:export_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn('Application ID,Candidate Name,Registration No', content)
        self.assertIn('Aarav Patel', content)
        self.assertIn('DASH_01', content)

    def test_csv_export_placed_students(self):
        self.client.login(username='officer_dash', password='password123')
        response = self.client.get(reverse('dashboard:export_placed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn('Student Name,Registration No,Email', content)
        self.assertIn('DASH_01', content)

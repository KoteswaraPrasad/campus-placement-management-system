from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from students.models import StudentProfile, Department
from companies.models import Company
from jobs.models import Job
from applications.models import Application, ApplicationStatus, ApplicationStatusHistory
from notifications.models import Notification

class ApplicationWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.officer = User.objects.create_user(
            username='officer_app', email='officer_app@test.com', password='password123',
            role=User.ROLE_OFFICER, is_staff=True
        )
        self.company = Company.objects.create(
            name='Global Tech', industry='IT', description='Tech giant',
            contact_person='Recruiter', contact_email='rec@global.com',
            locations='Pune', is_active=True
        )

        today = timezone.now().date()
        self.job = Job.objects.create(
            title='Backend Engineer',
            company=self.company,
            description='Django backend developer.',
            location='Pune',
            job_type='Full-time',
            required_skills='Python, Django',
            min_cgpa=7.0,
            max_backlogs=0,
            eligible_departments='Computer Science and Engineering',
            eligible_semesters='7,8',
            salary_package='8.5 LPA',
            opening_date=today - timedelta(days=2),
            deadline=today + timedelta(days=10),
            status='published',
            created_by=self.officer
        )

        # Eligible Student
        u1 = User.objects.create_user(username='app_student', email='app_student@test.com', password='password123', role=User.ROLE_STUDENT)
        self.student = StudentProfile.objects.create(
            user=u1, registration_number='APP_REG_01', department=Department.CSE,
            current_semester=7, cgpa=8.0, backlog_count=0, phone_number='1234567890', skills='Python',
            resume=SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        )

        # Ineligible Student (Low CGPA: 6.5 < 7.0)
        u2 = User.objects.create_user(username='ineligible_student', email='ineligible@test.com', password='password123', role=User.ROLE_STUDENT)
        self.ineligible_student = StudentProfile.objects.create(
            user=u2, registration_number='APP_REG_02', department=Department.CSE,
            current_semester=7, cgpa=6.5, backlog_count=0, phone_number='1234567890', skills='Python',
            resume=SimpleUploadedFile("resume_inel.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        )

    def test_eligible_student_can_apply(self):
        self.client.login(username='app_student', password='password123')
        response = self.client.post(reverse('applications:apply', args=[self.job.id]), {
            'cover_note': 'I have built multiple Django production apps.'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Application.objects.filter(job=self.job, student=self.student).exists())
        app = Application.objects.get(job=self.job, student=self.student)
        self.assertEqual(app.status, ApplicationStatus.APPLIED)

        # Check status history
        self.assertTrue(ApplicationStatusHistory.objects.filter(application=app, new_status=ApplicationStatus.APPLIED).exists())

        # Check in-app notification created
        self.assertTrue(Notification.objects.filter(recipient=self.student.user).exists())

    def test_ineligible_student_cannot_apply(self):
        self.client.login(username='ineligible_student', password='password123')
        response = self.client.post(reverse('applications:apply', args=[self.job.id]), {
            'cover_note': 'Please consider me.'
        }, follow=True)

        self.assertFalse(Application.objects.filter(job=self.job, student=self.ineligible_student).exists())

    def test_duplicate_application_prevented(self):
        # Create first application
        Application.objects.create(job=self.job, student=self.student, status=ApplicationStatus.APPLIED)

        self.client.login(username='app_student', password='password123')
        response = self.client.post(reverse('applications:apply', args=[self.job.id]), {
            'cover_note': 'Applying again.'
        }, follow=True)

        # Still only 1 application exists
        self.assertEqual(Application.objects.filter(job=self.job, student=self.student).count(), 1)

    def test_apply_outside_deadline_rejected(self):
        # Move job deadline to yesterday
        self.job.deadline = timezone.now().date() - timedelta(days=1)
        self.job.save()

        self.client.login(username='app_student', password='password123')
        response = self.client.post(reverse('applications:apply', args=[self.job.id]), {
            'cover_note': 'Late application.'
        }, follow=True)

        self.assertFalse(Application.objects.filter(job=self.job, student=self.student).exists())

    def test_officer_update_application_status_to_selected_places_student(self):
        app = Application.objects.create(job=self.job, student=self.student, status=ApplicationStatus.APPLIED)
        self.assertFalse(self.student.is_placed)

        self.client.login(username='officer_app', password='password123')
        response = self.client.post(reverse('applications:officer_update_status', args=[app.id]), {
            'status': ApplicationStatus.SELECTED,
            'notes': 'Selected after final technical round.'
        }, follow=True)

        app.refresh_from_db()
        self.assertEqual(app.status, ApplicationStatus.SELECTED)
        
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_placed)

        # Check status history was logged
        self.assertTrue(ApplicationStatusHistory.objects.filter(application=app, new_status=ApplicationStatus.SELECTED).exists())

    def test_student_withdraw_application(self):
        app = Application.objects.create(job=self.job, student=self.student, status=ApplicationStatus.APPLIED)

        self.client.login(username='app_student', password='password123')
        response = self.client.post(reverse('applications:withdraw', args=[app.id]), follow=True)

        app.refresh_from_db()
        self.assertEqual(app.status, ApplicationStatus.WITHDRAWN)

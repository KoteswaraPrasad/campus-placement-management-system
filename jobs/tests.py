from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from students.models import StudentProfile, Department
from companies.models import Company
from jobs.models import Job

class JobEligibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.officer = User.objects.create_user(
            username='officer_job',
            email='officer_job@test.com',
            password='password123',
            role=User.ROLE_OFFICER,
            is_staff=True
        )
        self.company = Company.objects.create(
            name='Acme Corp',
            industry='Technology',
            description='Test company',
            contact_person='HR Lead',
            contact_email='hr@acme.com',
            locations='Bangalore',
            is_active=True
        )

        today = timezone.now().date()
        self.job = Job.objects.create(
            title='Software Engineer',
            company=self.company,
            description='Build web systems.',
            location='Bangalore',
            job_type='Full-time',
            required_skills='Python, Django, SQL',
            min_cgpa=7.50,
            max_backlogs=0,
            eligible_departments='Computer Science and Engineering, Information Technology',
            eligible_semesters='7,8',
            salary_package='10 LPA',
            opening_date=today - timedelta(days=2),
            deadline=today + timedelta(days=10),
            status='published',
            created_by=self.officer
        )

        # Student 1: Fully eligible (CSE, 8.5 CGPA, 0 backlogs, sem 8)
        u1 = User.objects.create_user(username='el_student', email='el@test.com', password='password123', role=User.ROLE_STUDENT)
        self.eligible_student = StudentProfile.objects.create(
            user=u1, registration_number='REG_EL_1', department=Department.CSE,
            current_semester=8, cgpa=8.5, backlog_count=0, phone_number='1234567890', skills='Python',
            resume=SimpleUploadedFile("res1.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        )

        # Student 2: Ineligible due to low CGPA (6.8 < 7.5)
        u2 = User.objects.create_user(username='low_cgpa', email='low@test.com', password='password123', role=User.ROLE_STUDENT)
        self.low_cgpa_student = StudentProfile.objects.create(
            user=u2, registration_number='REG_LOW_CGPA', department=Department.CSE,
            current_semester=8, cgpa=6.8, backlog_count=0, phone_number='1234567890', skills='Python',
            resume=SimpleUploadedFile("res2.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        )

        # Student 3: Ineligible due to backlogs (2 > 0)
        u3 = User.objects.create_user(username='backlogs_user', email='bk@test.com', password='password123', role=User.ROLE_STUDENT)
        self.backlogs_student = StudentProfile.objects.create(
            user=u3, registration_number='REG_BK', department=Department.CSE,
            current_semester=8, cgpa=8.2, backlog_count=2, phone_number='1234567890', skills='Python',
            resume=SimpleUploadedFile("res3.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        )

        # Student 4: Ineligible due to branch (Mechanical Engineering not in CSE, IT)
        u4 = User.objects.create_user(username='mech_user', email='mech@test.com', password='password123', role=User.ROLE_STUDENT)
        self.mech_student = StudentProfile.objects.create(
            user=u4, registration_number='REG_MECH', department=Department.MECH,
            current_semester=8, cgpa=8.2, backlog_count=0, phone_number='1234567890', skills='CAD',
            resume=SimpleUploadedFile("res4.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        )

    def test_eligible_student_verification(self):
        is_el, reasons = self.job.check_eligibility(self.eligible_student)
        self.assertTrue(is_el)
        self.assertIn("satisfy all eligibility criteria", reasons[0])

    def test_ineligible_low_cgpa(self):
        is_el, reasons = self.job.check_eligibility(self.low_cgpa_student)
        self.assertFalse(is_el)
        self.assertTrue(any("below the minimum required" in r for r in reasons))

    def test_ineligible_excess_backlogs(self):
        is_el, reasons = self.job.check_eligibility(self.backlogs_student)
        self.assertFalse(is_el)
        self.assertTrue(any("exceeds the maximum allowed" in r for r in reasons))

    def test_ineligible_branch_mismatch(self):
        is_el, reasons = self.job.check_eligibility(self.mech_student)
        self.assertFalse(is_el)
        self.assertTrue(any("not in the eligible departments list" in r for r in reasons))

    def test_job_active_status_and_deadline(self):
        self.assertTrue(self.job.is_active_for_applications())

        # Expired job
        self.job.deadline = timezone.now().date() - timedelta(days=1)
        self.job.save()
        self.assertFalse(self.job.is_active_for_applications())
        self.assertTrue(self.job.is_past_deadline())

        # Reset deadline, deactivate company
        self.job.deadline = timezone.now().date() + timedelta(days=5)
        self.job.save()
        self.company.is_active = False
        self.company.save()
        self.assertFalse(self.job.is_active_for_applications())

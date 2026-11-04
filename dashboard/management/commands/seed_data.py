import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from students.models import StudentProfile, Department
from companies.models import Company
from jobs.models import Job
from applications.models import Application, ApplicationStatus, ApplicationStatusHistory
from notifications.models import Announcement, Notification

class Command(BaseCommand):
    help = "Seeds database with realistic initial academic placement data, users, and drives."

    def handle(self, *args, **options):
        self.stdout.write("Beginning database seeding process...")

        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@university.edu',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        self.stdout.write("  - Admin user created: admin / admin123")

        # 2. Placement Officer Account
        officer_user, created = User.objects.get_or_create(
            username='officer',
            defaults={
                'email': 'placement.officer@university.edu',
                'first_name': 'Dr. Rajesh',
                'last_name': 'Sharma',
                'role': User.ROLE_OFFICER,
                'is_staff': True,
            }
        )
        officer_user.set_password('officer123')
        officer_user.save()
        self.stdout.write("  - Placement Officer created: officer / officer123")

        # 3. Create sample resume dummy file content
        def dummy_pdf(name):
            return ContentFile(f"%PDF-1.4\n% Sample Academic Resume for {name}\n%%EOF".encode('utf-8'), name=f"{name.lower()}_resume.pdf")

        # 4. Create Sample Students
        students_data = [
            {
                'username': 'student1',
                'first_name': 'Aarav',
                'last_name': 'Patel',
                'email': 'aarav.patel@student.edu',
                'reg_no': '2022CSE015',
                'dept': Department.CSE,
                'sem': 8,
                'cgpa': 9.15,
                'backlogs': 0,
                'phone': '+91 9876500001',
                'skills': 'Python, Django, C++, Data Structures, Algorithms, Docker, PostgreSQL',
            },
            {
                'username': 'student2',
                'first_name': 'Priya',
                'last_name': 'Nair',
                'email': 'priya.nair@student.edu',
                'reg_no': '2022IT028',
                'dept': Department.IT,
                'sem': 8,
                'cgpa': 8.60,
                'backlogs': 0,
                'phone': '+91 9876500002',
                'skills': 'Java, Spring Boot, React, JavaScript, MySQL, Git, REST APIs',
            },
            {
                'username': 'student3',
                'first_name': 'Rohan',
                'last_name': 'Verma',
                'email': 'rohan.verma@student.edu',
                'reg_no': '2022ECE009',
                'dept': Department.ECE,
                'sem': 8,
                'cgpa': 7.40,
                'backlogs': 1,
                'phone': '+91 9876500003',
                'skills': 'Embedded C, Verilog, Python, MATLAB, IoT, Circuit Design',
            },
            {
                'username': 'student4',
                'first_name': 'Ananya',
                'last_name': 'Deshmukh',
                'email': 'ananya.deshmukh@student.edu',
                'reg_no': '2022AIDS004',
                'dept': Department.AIDS,
                'sem': 8,
                'cgpa': 8.90,
                'backlogs': 0,
                'phone': '+91 9876500004',
                'skills': 'Python, PyTorch, Pandas, Scikit-Learn, Machine Learning, NLP, SQL',
            },
            {
                'username': 'student5',
                'first_name': 'Vikram',
                'last_name': 'Reddy',
                'email': 'vikram.reddy@student.edu',
                'reg_no': '2022MECH045',
                'dept': Department.MECH,
                'sem': 8,
                'cgpa': 6.85,
                'backlogs': 0,
                'phone': '+91 9876500005',
                'skills': 'SolidWorks, AutoCAD, ANSYS, Manufacturing, Lean Principles, Python Basics',
            },
            {
                'username': 'student6',
                'first_name': 'Kavya',
                'last_name': 'Iyer',
                'email': 'kavya.iyer@student.edu',
                'reg_no': '2022EEE019',
                'dept': Department.EEE,
                'sem': 8,
                'cgpa': 7.85,
                'backlogs': 0,
                'phone': '+91 9876500006',
                'skills': 'Power Systems, MATLAB, Simulink, PLC Programming, C++, Microcontrollers',
            },
        ]

        created_students = []
        for s in students_data:
            u, _ = User.objects.get_or_create(
                username=s['username'],
                defaults={
                    'email': s['email'],
                    'first_name': s['first_name'],
                    'last_name': s['last_name'],
                    'role': User.ROLE_STUDENT,
                }
            )
            u.set_password('student123')
            u.save()

            sp, _ = StudentProfile.objects.get_or_create(
                user=u,
                defaults={
                    'registration_number': s['reg_no'],
                    'department': s['dept'],
                    'current_semester': s['sem'],
                    'cgpa': s['cgpa'],
                    'backlog_count': s['backlogs'],
                    'phone_number': s['phone'],
                    'skills': s['skills'],
                }
            )
            if not sp.resume:
                sp.resume.save(f"{s['username']}_resume.pdf", dummy_pdf(s['username']), save=True)
            created_students.append(sp)

        self.stdout.write(f"  - {len(created_students)} student accounts created.")

        # 5. Participating Companies
        companies_data = [
            {
                'name': 'Google India',
                'industry': 'Software & Cloud Services',
                'description': 'Google is a global technology leader focusing on search, cloud, artificial intelligence, and operating systems.',
                'website': 'https://careers.google.com',
                'contact_person': 'Sneha Kapoor (University Recruiting Lead)',
                'contact_email': 'sneha.recruiter@google.com',
                'locations': 'Bangalore, Hyderabad',
            },
            {
                'name': 'Microsoft',
                'industry': 'Enterprise Software & Cloud',
                'description': 'Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge.',
                'website': 'https://careers.microsoft.com',
                'contact_person': 'Arjun Mehta (Campus Talent Partner)',
                'contact_email': 'arjun.mehta@microsoft.com',
                'locations': 'Hyderabad, Bangalore, Noida',
            },
            {
                'name': 'Amazon',
                'industry': 'E-Commerce & Cloud Computing',
                'description': 'Amazon is guided by four principles: customer obsession rather than competitor focus, passion for invention, commitment to operational excellence, and long-term thinking.',
                'website': 'https://amazon.jobs',
                'contact_person': 'Tanvi Seth (Campus Lead)',
                'contact_email': 'tanvi.s@amazon.com',
                'locations': 'Bangalore, Chennai, Hyderabad',
            },
            {
                'name': 'Tata Consultancy Services (TCS)',
                'industry': 'IT Services & Consulting',
                'description': 'TCS is a global leader in IT services, consulting, and business solutions partnering with the world’s largest businesses.',
                'website': 'https://www.tcs.com/careers',
                'contact_person': 'Karan Malhotra (Regional Campus Manager)',
                'contact_email': 'karan.m@tcs.com',
                'locations': 'Pan-India, Mumbai, Pune, Bangalore',
            },
            {
                'name': 'Infosys',
                'industry': 'Digital Services & Consulting',
                'description': 'Infosys is a global leader in next-generation digital services and consulting navigating client transformations.',
                'website': 'https://www.infosys.com/careers',
                'contact_person': 'Deepika Rao (University Relations)',
                'contact_email': 'deepika.rao@infosys.com',
                'locations': 'Bangalore, Mysore, Pune, Hyderabad',
            },
            {
                'name': 'Deloitte USI',
                'industry': 'Consulting & Advisory',
                'description': 'Deloitte drives progress through consulting, audit, tax, and advisory services to Fortune 500 enterprises.',
                'website': 'https://www2.deloitte.com/careers',
                'contact_person': 'Naveen Joshi (Consulting Talent Lead)',
                'contact_email': 'naveen.j@deloitte.com',
                'locations': 'Hyderabad, Bangalore, Mumbai, Gurgaon',
            },
        ]

        created_companies = {}
        for c in companies_data:
            comp, _ = Company.objects.get_or_create(
                name=c['name'],
                defaults={
                    'industry': c['industry'],
                    'description': c['description'],
                    'website': c['website'],
                    'contact_person': c['contact_person'],
                    'contact_email': c['contact_email'],
                    'locations': c['locations'],
                    'is_active': True,
                }
            )
            created_companies[c['name']] = comp

        self.stdout.write(f"  - {len(created_companies)} companies seeded.")

        # 6. Job Openings with configured eligibility criteria
        today = timezone.now().date()
        jobs_data = [
            {
                'title': 'Software Engineer - Campus Graduate',
                'company': created_companies['Google India'],
                'description': 'Design, build, and deploy high-volume scalable backend systems, microservices, and client-facing web applications. Work directly alongside world-class engineering teams.',
                'location': 'Bangalore (Hybrid)',
                'job_type': 'Full-time',
                'required_skills': 'Python, C++, Java, Data Structures, Algorithms, Distributed Systems, SQL',
                'min_cgpa': 8.0,
                'max_backlogs': 0,
                'eligible_departments': 'Computer Science and Engineering, Information Technology, AI & Data Science',
                'eligible_semesters': '7,8',
                'salary_package': '18.5 LPA',
                'opening_date': today - timedelta(days=5),
                'deadline': today + timedelta(days=20),
                'status': 'published',
            },
            {
                'title': 'Cloud Support Engineer',
                'company': created_companies['Microsoft'],
                'description': 'Support enterprise Azure cloud deployments, troubleshoot virtualization issues, network configurations, and facilitate developer adoption.',
                'location': 'Hyderabad / Bangalore',
                'job_type': 'Full-time',
                'required_skills': 'Networking, Linux, PowerShell, Azure Fundamentals, Python, Problem Solving',
                'min_cgpa': 7.5,
                'max_backlogs': 0,
                'eligible_departments': 'Computer Science and Engineering, Information Technology, Electronics and Communication Engineering',
                'eligible_semesters': '7,8',
                'salary_package': '14.0 LPA',
                'opening_date': today - timedelta(days=7),
                'deadline': today + timedelta(days=15),
                'status': 'published',
            },
            {
                'title': 'Software Development Engineer I (SDE-1)',
                'company': created_companies['Amazon'],
                'description': 'Own complete lifecycle of software components for retail and AWS platforms. Write high-quality, test-driven Java/Python code with focus on security, latency, and fault tolerance.',
                'location': 'Bangalore',
                'job_type': 'Full-time',
                'required_skills': 'Java, Object-Oriented Design, Algorithm Design, AWS Services, Git',
                'min_cgpa': 8.5,
                'max_backlogs': 0,
                'eligible_departments': 'Computer Science and Engineering, Information Technology',
                'eligible_semesters': '7,8',
                'salary_package': '22.0 LPA',
                'opening_date': today - timedelta(days=10),
                'deadline': today + timedelta(days=18),
                'status': 'published',
            },
            {
                'title': 'Digital Software Developer (TCS Digital)',
                'company': created_companies['Tata Consultancy Services (TCS)'],
                'description': 'Develop innovative software applications utilizing cloud, analytics, and mobile technologies. Opportunities across banking, healthcare, and retail verticals.',
                'location': 'Pan-India',
                'job_type': 'Full-time',
                'required_skills': 'Python, Java, Web Technologies, Database Concepts, Analytical Thinking',
                'min_cgpa': 6.5,
                'max_backlogs': 1,
                'eligible_departments': 'ALL',
                'eligible_semesters': '7,8',
                'salary_package': '7.5 LPA',
                'opening_date': today - timedelta(days=12),
                'deadline': today + timedelta(days=25),
                'status': 'published',
            },
            {
                'title': 'Systems Engineer Specialist',
                'company': created_companies['Infosys'],
                'description': 'Participate in large-scale enterprise modernization, microservices refactoring, and AI-driven automation workflows.',
                'location': 'Pune / Bangalore / Mysore',
                'job_type': 'Full-time',
                'required_skills': 'Java, Python, SQL, REST APIs, Object-Oriented Programming',
                'min_cgpa': 7.0,
                'max_backlogs': 0,
                'eligible_departments': 'Computer Science and Engineering, Information Technology, Electronics and Communication Engineering, Electrical and Electronics Engineering',
                'eligible_semesters': '7,8',
                'salary_package': '9.5 LPA',
                'opening_date': today - timedelta(days=8),
                'deadline': today + timedelta(days=14),
                'status': 'published',
            },
            {
                'title': 'Associate Analyst - Technology Consulting',
                'company': created_companies['Deloitte USI'],
                'description': 'Deliver cutting-edge technology advisory, cloud transformations, ERP integrations, and business technology solutions to global Fortune 500 clients.',
                'location': 'Hyderabad, Bangalore',
                'job_type': 'Full-time',
                'required_skills': 'Business Analysis, SQL, Python, Excel, Communication, Cloud Concepts',
                'min_cgpa': 6.8,
                'max_backlogs': 1,
                'eligible_departments': 'ALL',
                'eligible_semesters': '7,8',
                'salary_package': '8.2 LPA',
                'opening_date': today - timedelta(days=6),
                'deadline': today + timedelta(days=16),
                'status': 'published',
            },
            {
                'title': 'Research & Innovation Intern',
                'company': created_companies['Tata Consultancy Services (TCS)'],
                'description': 'Semester-long research internship at TCS Research Labs focusing on applied machine learning, robotics, and cyber-physical systems.',
                'location': 'Pune / Bangalore',
                'job_type': 'Internship+PPO',
                'required_skills': 'Python, PyTorch, Research Methodologies, Algorithms, Technical Writing',
                'min_cgpa': 7.5,
                'max_backlogs': 0,
                'eligible_departments': 'Computer Science and Engineering, Information Technology, AI & Data Science, Electronics and Communication Engineering',
                'eligible_semesters': '7,8',
                'salary_package': '35,000 / month',
                'opening_date': today - timedelta(days=4),
                'deadline': today + timedelta(days=22),
                'status': 'published',
            },
            {
                'title': 'Site Reliability Engineer (Expired Drive)',
                'company': created_companies['Google India'],
                'description': 'Ensure global service availability and performance for Google applications.',
                'location': 'Bangalore',
                'job_type': 'Full-time',
                'required_skills': 'Linux, Python, Go, Networking, Kubernetes',
                'min_cgpa': 8.0,
                'max_backlogs': 0,
                'eligible_departments': 'Computer Science and Engineering, Information Technology',
                'eligible_semesters': '7,8',
                'salary_package': '17.0 LPA',
                'opening_date': today - timedelta(days=40),
                'deadline': today - timedelta(days=10),
                'status': 'closed',
            },
        ]

        created_jobs = []
        for j in jobs_data:
            job_obj, _ = Job.objects.get_or_create(
                title=j['title'],
                company=j['company'],
                defaults={
                    'description': j['description'],
                    'location': j['location'],
                    'job_type': j['job_type'],
                    'required_skills': j['required_skills'],
                    'min_cgpa': j['min_cgpa'],
                    'max_backlogs': j['max_backlogs'],
                    'eligible_departments': j['eligible_departments'],
                    'eligible_semesters': j['eligible_semesters'],
                    'salary_package': j['salary_package'],
                    'opening_date': j['opening_date'],
                    'deadline': j['deadline'],
                    'status': j['status'],
                    'created_by': officer_user,
                }
            )
            created_jobs.append(job_obj)

        self.stdout.write(f"  - {len(created_jobs)} jobs created.")

        # 7. Seed Applications across stages
        # Mapping student to jobs they applied for
        app_scenarios = [
            # Aarav (CSE, 9.15, 0 backlogs) -> Placed at Google!
            (created_students[0], created_jobs[0], ApplicationStatus.SELECTED, "Candidate demonstrated exceptional proficiency in system design and algorithms. Offer rolled out."),
            (created_students[0], created_jobs[2], ApplicationStatus.SHORTLISTED, "Cleared Online Assessment (OA). Interview round 1 scheduled."),
            
            # Priya (IT, 8.60, 0 backlogs) -> Placed at Microsoft!
            (created_students[1], created_jobs[1], ApplicationStatus.SELECTED, "Excellent cloud networking fundamentals. Final offer extended."),
            (created_students[1], created_jobs[0], ApplicationStatus.UNDER_REVIEW, "Profile shortlisted for technical screening."),

            # Rohan (ECE, 7.40, 1 backlog) -> Applied to TCS (eligible)
            (created_students[2], created_jobs[3], ApplicationStatus.INTERVIEW_SCHEDULED, "Technical & HR Interview scheduled on upcoming Saturday."),
            
            # Ananya (AIDS, 8.90, 0 backlogs) -> Shortlisted at Google, Selected at TCS Research
            (created_students[3], created_jobs[6], ApplicationStatus.SELECTED, "Outstanding publication record and NLP project portfolio. Research internship confirmed."),
            (created_students[3], created_jobs[0], ApplicationStatus.SHORTLISTED, "Code challenge passed with 100% test coverage."),

            # Vikram (MECH, 6.85, 0 backlogs) -> Deloitte (eligible)
            (created_students[4], created_jobs[5], ApplicationStatus.UNDER_REVIEW, "Initial aptitude screening cleared."),

            # Kavya (EEE, 7.85, 0 backlogs) -> Infosys (eligible)
            (created_students[5], created_jobs[4], ApplicationStatus.APPLIED, "Application submitted with verified resume."),
        ]

        for student, job, status, notes in app_scenarios:
            app, created = Application.objects.get_or_create(
                job=job,
                student=student,
                defaults={
                    'status': status,
                    'cover_note': f"I am deeply enthusiastic about the {job.title} role at {job.company.name} and eager to contribute my skills.",
                }
            )
            if created or not app.status_history.exists():
                ApplicationStatusHistory.objects.create(
                    application=app,
                    old_status=ApplicationStatus.APPLIED,
                    new_status=status,
                    changed_by=officer_user,
                    notes=notes,
                )
                if status == ApplicationStatus.SELECTED:
                    student.is_placed = True
                    student.save()

        self.stdout.write("  - Candidate applications and status histories created.")

        # 8. Placement Announcements
        announcements_data = [
            {
                'title': 'Google Campus Recruitment Drive 2026 - Registration Open',
                'category': 'new_job',
                'is_pinned': True,
                'content': 'Google India has opened on-campus recruitment for Software Engineer roles (Class of 2026). All eligible CSE, IT, and AI/DS students with CGPA >= 8.0 and no active backlogs must submit their applications before the deadline.',
            },
            {
                'title': 'TCS National Qualifier Test (NQT) Drive Schedule',
                'category': 'placement_drive',
                'is_pinned': True,
                'content': 'The online assessment for TCS Digital and Ninja will be conducted in the central computer labs next Wednesday from 9:00 AM to 1:00 PM. Please bring your college ID cards and hall tickets.',
            },
            {
                'title': 'Resume Verification & Placement Orientation Workshop',
                'category': 'general',
                'is_pinned': False,
                'content': 'The University Placement Cell is conducting a mandatory resume validation and technical mock interview boot-camp in the Main Auditorium on Friday at 3:00 PM.',
            },
            {
                'title': 'Microsoft Cloud Support Engineer Shortlist & Interview Roster',
                'category': 'interview_schedule',
                'is_pinned': False,
                'content': 'The shortlist for Microsoft Cloud Support Engineer interviews is published. Shortlisted candidates must join the virtual Teams bridge as per their assigned time slots.',
            },
            {
                'title': 'Upcoming Deadline: Amazon SDE-1 Application Closes in 48 Hours',
                'category': 'deadline_alert',
                'is_pinned': False,
                'content': 'Eligible students who haven’t applied for Amazon SDE-1 are reminded to submit before the portal locks. No extensions will be granted by the corporate recruitment team.',
            },
        ]

        for a in announcements_data:
            Announcement.objects.get_or_create(
                title=a['title'],
                defaults={
                    'category': a['category'],
                    'is_pinned': a['is_pinned'],
                    'content': a['content'],
                    'created_by': officer_user,
                }
            )

        self.stdout.write("  - Placement announcements published.")

        # 9. In-App Notifications for Students
        Notification.objects.get_or_create(
            recipient=created_students[0].user,
            title="Congratulations! Offer Received",
            defaults={
                'message': "Your application for 'Software Engineer' at Google India has been SELECTED. Official offer letter details will follow.",
                'link': '/applications/my-applications/',
                'is_read': False,
            }
        )
        Notification.objects.get_or_create(
            recipient=created_students[1].user,
            title="Offer Selected at Microsoft",
            defaults={
                'message': "You have been selected for 'Cloud Support Engineer' at Microsoft! Congratulations on your placement.",
                'link': '/applications/my-applications/',
                'is_read': False,
            }
        )
        Notification.objects.get_or_create(
            recipient=created_students[2].user,
            title="Interview Scheduled: TCS Digital",
            defaults={
                'message': "Your technical interview with TCS is scheduled for Saturday 11:00 AM.",
                'link': '/applications/my-applications/',
                'is_read': False,
            }
        )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

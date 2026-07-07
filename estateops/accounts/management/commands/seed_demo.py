import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import User
from projects.models import Project, Employee, Attendance, Visitor, Asset, Leave, ProgressUpdate
from leads.models import Lead, FollowUp
from stock.models import StockItem


class Command(BaseCommand):
    help = "Seed demo projects and multi-tenant assets matching requirements"

    def handle(self, *args, **options):
        # Clear existing workspace data to avoid clashes on seed
        Leave.objects.all().delete()
        Visitor.objects.all().delete()
        Asset.objects.all().delete()
        Attendance.objects.all().delete()
        Employee.objects.all().delete()
        
        # User cleanup (excluding admin/superusers we want to keep if exist, but recreate standard ones)
        User.objects.exclude(username="admin").delete()
        Project.objects.all().delete()

        # 1. Create Super Admin
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser(
                "admin", "admin@estateops.test", "admin123", 
                role=User.Role.SUPER_ADMIN
            )
            self.stdout.write(self.style.SUCCESS("Created Super Admin user -> admin / admin123"))
        else:
            admin_user = User.objects.get(username="admin")
            admin_user.role = User.Role.SUPER_ADMIN
            admin_user.save()

        # 2. Create Projects
        proj_amd = Project.objects.create(
            name="Estate Ops Ahmedabad",
            code="AMD-01",
            location_type="AHMEDABAD",
            address="Near SG Highway, Bodakdev",
            city="Ahmedabad",
            state="Gujarat",
            pincode="380054",
            status="UNDER_CONSTRUCTION",
            current_stage=Project.Stage.PLASTER,
            progress=70,
            created_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS("Created Project -> Estate Ops Ahmedabad (AMD-01)"))
 
        proj_rjt = Project.objects.create(
            name="Estate Ops Rajkot",
            code="RJT-01",
            location_type="OTHER",
            address="Kalavad Road, Opp. University Site",
            city="Rajkot",
            state="Gujarat",
            pincode="360005",
            status="UNDER_CONSTRUCTION",
            current_stage=Project.Stage.SLAB,
            progress=45,
            created_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS("Created Project -> Estate Ops Rajkot (RJT-01)"))

        # 3. Create Project Admins, HRs, and Security Users
        # Ahmedabad Workspace
        User.objects.create_user(
            "amd_admin", "amd_admin@estateops.test", "admin123",
            role=User.Role.PROJECT_ADMIN, project=proj_amd
        )
        User.objects.create_user(
            "amd_hr", "amd_hr@estateops.test", "hr123",
            role=User.Role.HR, project=proj_amd
        )
        User.objects.create_user(
            "amd_sec", "amd_sec@estateops.test", "sec123",
            role=User.Role.SECURITY, project=proj_amd
        )
        # Rajkot Workspace
        User.objects.create_user(
            "rjt_admin", "rjt_admin@estateops.test", "admin123",
            role=User.Role.PROJECT_ADMIN, project=proj_rjt
        )
        User.objects.create_user(
            "rjt_hr", "rjt_hr@estateops.test", "hr123",
            role=User.Role.HR, project=proj_rjt
        )

        self.stdout.write(self.style.SUCCESS("Created user roles for Ahmedabad and Rajkot projects."))

        # 4. Create Employees
        # Ahmedabad Employees
        emp_rahul = Employee.objects.create(
            name="Rahul Sharma",
            email="rahul.sharma@estateops.test",
            mobile="9876543210",
            department="Civil Construction",
            designation="Site Supervisor",
            joining_date=datetime.date(2025, 6, 1),
            aadhaar="1234-5678-9012",
            address="12, Shanti Nagar, Ahmedabad",
            status="ACTIVE",
            project=proj_amd,
            created_by=admin_user
        )
        emp_amit = Employee.objects.create(
            name="Amit Patel",
            email="amit.patel@estateops.test",
            mobile="9988776655",
            department="Safety & Quality",
            designation="Safety Inspector",
            joining_date=datetime.date(2025, 8, 15),
            aadhaar="9876-5432-1098",
            address="G-45, Riverfront Apts, Ahmedabad",
            status="ACTIVE",
            project=proj_amd,
            created_by=admin_user
        )
        # Rajkot Employees
        emp_karan = Employee.objects.create(
            name="Karan Dave",
            email="karan.dave@estateops.test",
            mobile="9080706050",
            department="Electrical & Plumbing",
            designation="Chief Electrical Engineer",
            joining_date=datetime.date(2026, 1, 10),
            aadhaar="4455-6677-8899",
            address="University Road, Rajkot",
            status="ACTIVE",
            project=proj_rjt,
            created_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS("Seeded demo employees."))

        # 5. Seed Attendance Logs
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        # Ahmedabad Attendance
        Attendance.objects.create(employee=emp_rahul, date=yesterday, status="PRESENT", project=proj_amd, created_by=admin_user)
        Attendance.objects.create(employee=emp_amit, date=yesterday, status="LATE", project=proj_amd, created_by=admin_user)
        Attendance.objects.create(employee=emp_rahul, date=today, status="PRESENT", project=proj_amd, created_by=admin_user)
        # Leave logged today for Amit
        Attendance.objects.create(employee=emp_amit, date=today, status="LEAVE", project=proj_amd, created_by=admin_user)

        # Rajkot Attendance
        Attendance.objects.create(employee=emp_karan, date=yesterday, status="PRESENT", project=proj_rjt, created_by=admin_user)
        Attendance.objects.create(employee=emp_karan, date=today, status="PRESENT", project=proj_rjt, created_by=admin_user)
        
        self.stdout.write(self.style.SUCCESS("Seeded Attendance logs."))

        # 6. Seed Visitors
        Visitor.objects.create(
            name="Suresh Mehta",
            mobile="9123456780",
            purpose="Cement Delivery Supply",
            contact_person="Rahul Sharma",
            entry_time=timezone.now() - datetime.timedelta(hours=2),
            project=proj_amd,
            created_by=admin_user
        )
        Visitor.objects.create(
            name="Vijay Rupani",
            mobile="9898989898",
            purpose="Site Safety Audit Inspection",
            contact_person="Amit Patel",
            entry_time=timezone.now() - datetime.timedelta(hours=4),
            exit_time=timezone.now() - datetime.timedelta(hours=3),
            project=proj_amd,
            created_by=admin_user
        )
        Visitor.objects.create(
            name="Ramesh Bhai",
            mobile="9090909090",
            purpose="Plumbing consultant meeting",
            contact_person="Karan Dave",
            entry_time=timezone.now() - datetime.timedelta(hours=1),
            project=proj_rjt,
            created_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS("Seeded visitor logs."))

        # 7. Seed Assets
        Asset.objects.create(
            name="Heavy Duty Concrete Mixer",
            code="MIX-001",
            value=85000.00,
            description="Mixer machine for concrete layouts",
            project=proj_amd,
            created_by=admin_user
        )
        Asset.objects.create(
            name="Industrial Welding Rig",
            code="WLD-042",
            value=25000.00,
            description="Plaster stage welding machine setup",
            project=proj_amd,
            created_by=admin_user
        )
        Asset.objects.create(
            name="Excavator Crane Rig",
            code="CRN-099",
            value=650000.00,
            description="Rig setup for Rajkot site foundation excavation",
            project=proj_rjt,
            created_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS("Seeded assets inventory."))

        # 8. Seed Leaves
        Leave.objects.create(
            employee=emp_amit,
            start_date=today,
            end_date=today + datetime.timedelta(days=2),
            reason="Medical Checkup / Rest",
            status="APPROVED",
            project=proj_amd,
            created_by=admin_user
        )
        Leave.objects.create(
            employee=emp_karan,
            start_date=today + datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=7),
            reason="Personal Emergency Leave",
            status="PENDING",
            project=proj_rjt,
            created_by=admin_user
        )
        self.stdout.write(self.style.SUCCESS("Seeded leave requests."))

        # 9. Seed Leads isolated by project
        Lead.objects.create(
            client_name="Haresh Bhai",
            mobile="9898765432",
            requirement="3BHK",
            source="Facebook Ads",
            budget_min=4500000,
            budget_max=6000000,
            status="interested",
            project=proj_amd,
            created_by=admin_user
        )
        Lead.objects.create(
            client_name="Rajesh Patel",
            mobile="9191919191",
            requirement="VILLA",
            source="Newspaper Ad",
            budget_min=12000000,
            budget_max=15000000,
            status="active",
            project=proj_rjt,
            created_by=admin_user
        )
        
        # 10. Seed StockItems isolated by project
        StockItem.objects.create(
            item="Cement Bags (OPC 53)",
            price=450.00,
            available=350,
            threshold=100,
            project=proj_amd
        )
        StockItem.objects.create(
            item="Steel Bars (12mm TMT)",
            price=72.00,
            available=50,
            threshold=200,  # triggers Low Stock warning
            project=proj_amd
        )
        StockItem.objects.create(
            item="Plumbing Pipes (PVC)",
            price=120.00,
            available=1200,
            threshold=150,
            project=proj_rjt
        )

        # 11. Seed FollowUps for Leads
        lead_amd = Lead.objects.filter(project=proj_amd).first()
        if lead_amd:
            FollowUp.objects.create(
                lead=lead_amd,
                outcome="interested",
                next_followup_date=today + datetime.timedelta(days=3),
                note="Client is interested in site visit next Sunday.",
                created_by=admin_user
            )

        # 12. Seed Progress Updates
        ProgressUpdate.objects.create(
            project=proj_amd,
            stage="Brickwork",
            progress=55,
            message="Completed brickwork for first block floor.",
            created_by=admin_user
        )

        self.stdout.write(self.style.SUCCESS("Demo data successfully seeded for all workspaces."))

from django.contrib import admin
from .models import (
    studentInfo,
    RequestedGMC,
    Schedule,
    Equipment,
    ProcurementItem,
    BorrowingRecord,
)
from .models import (
    Officer,
    Project,
    FinancialStatement,
    Accreditation,
    Adviser,
    AdminLogin,
    OfficerLogin,
)
from .models import Alumni, graduateForm, Event, Yearbook, Event, JobFair
from .models import (
    IndividualProfileBasicInfo,
    TestArray,
    FileUploadTest,
    counseling_schedule,
    exit_interview_db,
    OjtAssessment,
    IntakeInverView,
    GuidanceTransaction,
)
from .models import (
    Program,
    Projects,
    MOD,
    QrDonation,
)


# Register your models here.
class OfficerAdmin(admin.ModelAdmin):
    list_display = (
        "surname",
        "student_id",
        "Officer_profile_picture",
        "firstname",
        "middlename",
        "organization",
        "course",
        "year",
        "status",
    )


class AdviserAdmin(admin.ModelAdmin):
    list_display = (
        "surname",
        "Adviser_profile_picture",
        "firstname",
        "middlename",
        "department",
        "status",
    )


class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "project_id",
        "objective",
        "org",
        "target",
        "involved_officer",
        "p_budget",
        "expected_output",
        "actual_accomplishment",
        "remarks",
        "status",
        "date_saved",
    ]


class FinancialStatementAdmin(admin.ModelAdmin):
    list_display = [
        "financial_id",
        "date",
        "purpose",
        "source_of_funds",
        "org",
        "amount",
        "remarks",
        "status",
        "date_saved",
    ]


class AccreditationAdmin(admin.ModelAdmin):
    list_display = ("accreditation_id", "organization", "date_saved")


class LoginadminAdmin(admin.ModelAdmin):
    list_display = ("admin_id", "admin_username", "admin_password")


class OfficerLoginAdmin(admin.ModelAdmin):
    list_display = ("student_id", "organization", "username", "password")


admin.site.register(OfficerLogin, OfficerLoginAdmin)
admin.site.register(AdminLogin, LoginadminAdmin)
admin.site.register(FinancialStatement, FinancialStatementAdmin)
admin.site.register(Adviser, AdviserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Officer, OfficerAdmin)
admin.site.register(Accreditation, AccreditationAdmin)


class StudentInfoAdmin(admin.ModelAdmin):

    list_display = (
        "studID",
        "lastname",
        "firstname",
        "middlename",
        "degree",
        "yearlvl",
        "sex",
        "emailadd",
        "contact",
    )
    search_fields = ("studID", "lastname", "firstname", "lrn")
    list_filter = ("degree", "yearlvl", "sex")


admin.site.register(studentInfo, StudentInfoAdmin)


class requestedgmcAdmin(admin.ModelAdmin):
    list_display = ("student", "reason", "or_num", "request_date", "processed")


admin.site.register(RequestedGMC, requestedgmcAdmin)


class scheduleAdmin(admin.ModelAdmin):
    list_display = (
        "sched_Id",
        "title",
        "description",
        "start_datetime",
        "end_datetime",
    )


admin.site.register(Schedule, scheduleAdmin)

admin.site.register(Equipment)

admin.site.register(BorrowingRecord)

# FOR PPMP TRACKER


class ProcurementItemAdmin(admin.ModelAdmin):
    list_display = (
        "itemid",
        "item",
        "quantity",
        "unit",
        "estimated_budget",
        "mode_of_procurement",
        "unit_price",
        "status",
    )
    list_filter = ("mode_of_procurement",)
    search_fields = ("item",)


admin.site.register(ProcurementItem, ProcurementItemAdmin)

# for delivered
from .models import Storage


class StorageAdmin(admin.ModelAdmin):
    list_display = ("get_item_id", "get_item", "serial_no", "get_unit_price")
    search_fields = ("procurement_item__itemid", "procurement_item__item", "serial_no")

    def get_item_id(self, obj):
        return obj.procurement_item.itemid

    get_item_id.short_description = "Item ID"

    def get_item(self, obj):
        return obj.procurement_item.item

    get_item.short_description = "Item"

    def get_unit_price(self, obj):
        return obj.procurement_item.unit_price

    get_unit_price.short_description = "Unit Price"


admin.site.register(Storage, StorageAdmin)

# for my lnd
from .models import ExcelData


@admin.register(ExcelData)
class ExcelDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_of_l_d",
        "frequency",
        "category",
        "expected_number_of_participants",
        "duration",
        "registration_fees",
        "travelling_expenses",
        "planned_total_budget",
        "actual_total_budget",
        "variance",
        "admin_remarks",
    )
    ordering = ("id",)


# Alumni


class AlumniAdmin(admin.ModelAdmin):
    list_display = (
        "alumniID",
        "student_id",
        "firstname",
        "lastname",
        "degree",
        "alumniaddress",
    )

    def get_firstname(self, obj):
        return obj.student.fname

    get_firstname.short_description = "First Name"

    def get_lastname(self, obj):
        return obj.student.lname

    get_lastname.short_description = "Last Name"


class graduateFormAdmin(admin.ModelAdmin):
    list_display = (
        "get_alumniID",
        "dategraduated",
        "firstname",
        "lastname",
        "alumniaddress",
    )

    def get_alumniID(self, obj):
        return obj.alumniID.alumniID

    get_alumniID.short_description = "Alumni ID"


class EventAdmin(admin.ModelAdmin):
    list_display = ("eventID", "eventsName", "eventsDate", "eventsLocation")


class JobFairAdmin(admin.ModelAdmin):
    list_display = (
        "jobfair_id",
        "jobtitle",
        "companyname",
        "joblocation",
        "employmenttype",
        "jobsalary",
    )


class YearbookAdmin(admin.ModelAdmin):
    list_display = (
        "yearbookID",
        "yearbookFirstname",
        "yearbookLastname",
        "yearbookGender",
        "yearbookAddress",
        "yearbookCourse",
        "yearbookYearGrad",
    )


admin.site.register(Yearbook, YearbookAdmin)
admin.site.register(JobFair, JobFairAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(graduateForm, graduateFormAdmin)
admin.site.register(Alumni, AlumniAdmin)


# StudentOrg


class IndividualProfileBasicInfoAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.get_fields()]
        super().__init__(model, admin_site)


class IntakeInverViewAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.get_fields()]
        super().__init__(model, admin_site)


admin.site.register(IndividualProfileBasicInfo)
admin.site.register(IntakeInverView)


class counselingSceduleAdmin(admin.ModelAdmin):
    list_display = (
        "counselingID",
        "dateRecieved",
        "studentID",
        "reason",
        "scheduled_date",
        "scheduled_time",
        "email",
        "status",
    )
    list_editable = (
        "dateRecieved",
        "reason",
        "scheduled_date",
        "scheduled_time",
        "email",
        "status",
    )


class OjtAssessmentAdmin(admin.ModelAdmin):
    list_display = [
        "OjtRequestID",
        "studentID",
        "dateRecieved",
        "schoolYear",
        "status",
        "dateAccepted",
        "orno",
    ]
    list_editable = ["schoolYear", "status", "dateAccepted"]


class exitInterviewAdmine(admin.ModelAdmin):
    list_display = (
        "exitinterviewId",
        "studentID",
        "dateRecieved",
        "date",
        "dateEnrolled",
        "reasonForLeaving",
        "satisfiedWithAcadamic",
        "feedbackWithAcademic",
        "satisfiedWithSocial",
        "feedbackWithSocial",
        "satisfiedWithServices",
        "feedbackWithServices",
        "contributedToDecision",
        "intendedMajor",
        "firstConsider",
        "whatCondition",
        "recommend",
        "howSatisfied",
        "planTOReturn",
        "accademicExperienceSatisfied",
        "knowAboutYourTime",
        "currentlyEmployed",
        "explainationEmployed",
        "status",
        "scheduled_date",
        "scheduled_time",
        "emailadd",
    )
    list_editable = (
        "date",
        "dateEnrolled",
        "reasonForLeaving",
        "satisfiedWithAcadamic",
        "feedbackWithAcademic",
        "satisfiedWithSocial",
        "feedbackWithSocial",
        "satisfiedWithServices",
        "feedbackWithServices",
        "intendedMajor",
        "firstConsider",
        "whatCondition",
        "recommend",
        "howSatisfied",
        "planTOReturn",
        "accademicExperienceSatisfied",
        "knowAboutYourTime",
        "currentlyEmployed",
        "explainationEmployed",
        "status",
        "scheduled_date",
        "scheduled_time",
        "emailadd",
    )


admin.site.register(counseling_schedule, counselingSceduleAdmin)
admin.site.register(exit_interview_db, exitInterviewAdmine)
admin.site.register(OjtAssessment, OjtAssessmentAdmin)
admin.site.register(GuidanceTransaction)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "caption", "date_time", "archive", "image_upload")


class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "caption", "date_time", "archive", "image_upload")


class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "donated",
        "donation_type",
        "name",
        "gcash_number",
        "bank_number",
        "bank_card",
        "contact_number",
        "amount",
        "what_kind",
        "recepient",
        "recepient_things",
        "date_sched",
        "date",
        "image_details",
    )


class QrDonationAdmin(admin.ModelAdmin):
    list_display = (
        "qr_id",
        "gcash",
        "bpi",
        "bdo",
        "landbank",
        "pnb",
        "metro",
        "union",
        "china",
    )


admin.site.register(Program, ProgramAdmin)
admin.site.register(Projects, ProjectAdmin)
admin.site.register(MOD, DonationAdmin)
admin.site.register(QrDonation, QrDonationAdmin)

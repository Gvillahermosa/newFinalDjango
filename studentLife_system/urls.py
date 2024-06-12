from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import transac_search
from .views import approve_alumni_request, claim_alumni_id
from .views import UpdateStatusView

from .views import projects, program_form
from .views import (
    home,
    counseling_app,
    exit_interview,
    individualProfile,
    search_student_info,
    check_date_time_validity,
)
from .views import (
    counseling_app_admin_view,
    ojt_assessment,
    exit_interview_admin_view,
    ojt_assessment_admin_view,
    update_exit_interview_status,
    counselor_scheduler,
    counseling_schedule_admin,
)
from .views import (
    delete_exit_interview_status,
    update_ojt_assessment,
    delete_ojt_assessment,
    check_date_time_validity_for_exit,
    get_ojt_assessment_data,
)
from .views import (
    search_ojt_assessment_request,
    search_exit_interview_request,
    get_exit_interview_request,
    update_counseling_schedule,
    delete_counseling_schedule,
)
from .views import (
    search_student_info_for_individual,
    intake_interview_view,
    search_student_info_for_intake,
    individual_profile_sheet,
)
from .views import (
    home,
    counseling_app,
    exit_interview,
    individualProfile,
    search_student_info,
    check_date_time_validity,
)
from .views import (
    counseling_app_admin_view,
    ojt_assessment,
    exit_interview_admin_view,
    ojt_assessment_admin_view,
    update_exit_interview_status,
)
from .views import (
    delete_exit_interview_status,
    update_ojt_assessment,
    delete_ojt_assessment,
    check_date_time_validity_for_exit,
    get_ojt_assessment_data,
)
from .views import (
    search_ojt_assessment_request,
    search_exit_interview_request,
    get_exit_interview_request,
    update_counseling_schedule,
    delete_counseling_schedule,
)
from .views import (
    search_student_info_for_individual,
    intake_interview_view,
    search_student_info_for_intake,
    individual_profile_sheet,
    guidance_transaction,
    daily_montly_guidance_transaction,
    show_transaction_specific_date,
    sort_counseling_app_admin_view,
    sort_exit_interview_admin_view,
)


app_name = "studentLife_system"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("settings", views.upload_student_data, name="upload_student_data"),
    path("homepage", views.homepage, name="homepage"),
    path("requestgmc", views.requestedgmc, name="requestgmc"),
    path("equipmenttracker", views.equipmentTracker, name="equipmentTracker"),
    path(
        "equipmenttrackerAdmin/",
        views.equipmentTrackerAdmin,
        name="equipmentTrackerAdmin",
    ),
    path(
        "save_equipment_borrowing/",
        views.save_equipment_borrowing,
        name="save_equipment_borrowing",
    ),
    path(
        "update_return_status/", views.update_return_status, name="update_return_status"
    ),
    path("adminmain", views.adminhome, name="adminmain"),
    path("requested-gmc", views.adminRequestedGmc, name="adminRequestedGmc"),
    path("gmc-form", views.gmcform, name="gmcform"),
    path("generate-gmc/<int:request_id>/", views.generateGmc, name="generateGmc"),
    path(
        "transactionreport",
        views.processed_gmc_transactions,
        name="processed_gmc_transactions",
    ),
    path("monthlyCalendar", views.monthlyCalendar, name="monthlyCalendar"),
    path(
        "monthlyCalendarAdmin", views.monthlyCalendarAdmin, name="monthlyCalendarAdmin"
    ),
    path("save-schedule/", views.save_schedule, name="save_schedule"),
    path(
        "update-schedule/<int:schedule_id>/",
        views.update_schedule,
        name="update_schedule",
    ),
    path(
        "delete-schedule/<int:schedule_id>/",
        views.delete_schedule,
        name="delete_schedule",
    ),
    path("addEquipment/", views.addEquipment, name="addEquipment"),
    path("upload/", views.upload_file, name="upload_file"),
    path("display_items/", views.display_items, name="display_items"),
    path("update_status/", UpdateStatusView.as_view(), name="update_status"),
    path("purchased_items/", views.purchased_items, name="purchased_items"),
    path("lnd_file/", views.lnd_file, name="lnd_file"),
    path(
        "display_storage_items/",
        views.display_storage_items,
        name="display_storage_items",
    ),
    path(
        "update_serial_no/<int:storage_id>/",
        views.update_serial_no,
        name="update_serial_no",
    ),
    path(
        "edit/", views.edit_excel_data, name="edit_excel_data"
    ),  # mao ne na lines napuno
    path(
        "update/<int:pk>/", views.update_excel_data, name="update_excel_data"
    ),  # asta ne
    # ALUMNI
    path("id_request/", views.idRequest, name="idRequest"),
    path("search_id/", views.search_id, name="search_id"),
    path("add_alumni/", views.add_alumni, name="add_alumni"),
    path("search_id2/", views.search_id2, name="search_id2"),
    path(
        "graduateTracer_submit",
        views.graduateTracer_submit,
        name="graduateTracer_submit",
    ),
    path("graduatetracer/", views.graduateTracer, name="graduateTracer"),
    path("reunionandevents/", views.alumni_events, name="alumni_events"),
    path("jobfairs/", views.jobfairs, name="jobfairs"),
    path("yearbook/", views.yearbook, name="yearbook"),
    path("search_yearbook/", views.search_yearbook, name="search_yearbook"),
    path(
        "transaction_alumni.html/", views.transaction_alumni, name="transaction_alumni"
    ),
    path("transac_search", transac_search, name="transac_search"),
    path("admin_id_request/", views.admin_id_request, name="admin_idRequest"),
    path(
        "approve_alumni_request/<int:alumni_id>/",
        approve_alumni_request,
        name="approve_alumni_request",
    ),
    path("claim_alumni_id/<int:alumni_id>/", claim_alumni_id, name="claim_alumni_id"),
    path("admin_grad_tracer/", views.admin_gradTracer, name="admin_gradTracer"),
    path("admin_events/", views.admin_events, name="admin_events"),
    path("admin_jobfairs", views.admin_jobfairs, name="admin_jobfairs"),
    path("admin_yearbook", views.admin_yearbook, name="admin_yearbook"),
    # Studentorg
    # LOG-IN
    path("admin_login/", views.admin_login, name="admin_login"),
    path("register_officer/", views.register_officer, name="register_officer"),
    path("officer_login/", views.officer_login, name="officer_login"),
    path("logins/", views.logins, name="logins"),
    # ADMIN
    path("admin_manageofficer/", views.admin_manageofficer, name="admin_manageofficer"),
    path("admin_manageadviser/", views.admin_manageadviser, name="admin_manageadviser"),
    path(
        "admin_managefinancial/",
        views.admin_managefinancial,
        name="admin_managefinancial",
    ),
    path("admin_manageproject/", views.admin_manageproject, name="admin_manageproject"),
    path(
        "admin_manage_accreditations/",
        views.admin_manage_accreditations,
        name="admin_manage_accreditations",
    ),
    path(
        "admin_view_accreditations/",
        views.admin_view_accreditations,
        name="admin_view_accreditations",
    ),
    path(
        "admin_transactionreport/",
        views.admin_transactionreport,
        name="transaction_report",
    ),
    # Certification
    path("FSTLP_certification", views.FSTLP_certification, name="FSTLP_certification"),
    path("SI_certification", views.SI_certification, name="SI_certification"),
    path(
        "THEEQUATIONERS_certification",
        views.THEEQUATIONERS_certification,
        name="THEEQUATIONERS_certification",
    ),
    path("SSG_certification", views.SSG_certification, name="SSG_certification"),
    path(
        "TECHNOCRATS_certification",
        views.TECHNOCRATS_certification,
        name="TECHNOCRATS_certification",
    ),
    # FSTLP
    path("FSTLP_profile", views.FSTLP_profile, name="FSTLP_profile"),
    path("FSTLP_projects", views.FSTLP_projects, name="FSTLP_projects"),
    path("FSTLP_financial", views.FSTLP_financial, name="FSTLP_financial"),
    path("FSTLP_CBL", views.FSTLP_CBL, name="FSTLP_CBL"),
    path("FSTLP_officerdata", views.FSTLP_officerdata, name="FSTLP_officerdata"),
    path("FSTLP_adviserdata", views.FSTLP_adviserdata, name="FSTLP_adviserdata"),
    path("FSTLP_viewproject", views.FSTLP_viewproject, name="FSTLP_viewproject"),
    path("FSTLP_viewfinancial", views.FSTLP_viewfinancial, name="FSTLP_viewfinancial"),
    path("FSTLP_viewofficer", views.FSTLP_viewofficer, name="FSTLP_viewofficer"),
    path("FSTLP_viewadviser", views.FSTLP_viewadviser, name="FSTLP_viewadviser"),
    path("FSTLP_accreditation", views.FSTLP_accreditation, name="FSTLP_accreditation"),
    # SI++
    path("SI_profile", views.SI_profile, name="SI_profile"),
    path("SI_projects", views.SI_projects, name="SI_projects"),
    path("SI_financial", views.SI_financial, name="SI_financial"),
    path("SI_CBL", views.SI_CBL, name="SI_CBL"),
    path("SI_officerdata", views.SI_officerdata, name="SI_officerdata"),
    path("SI_adviserdata", views.SI_adviserdata, name="SI_adviserdata"),
    path("SI_viewproject", views.SI_viewproject, name="SI_viewproject"),
    path("SI_viewfinancial", views.SI_viewfinancial, name="SI_viewfinancial"),
    path("SI_viewadviser", views.SI_viewadviser, name="SI_viewadviser"),
    path("SI_viewofficer", views.SI_viewofficer, name="SI_viewofficer"),
    path("SI_accreditation", views.SI_accreditation, name="SI_accreditation"),
    # THE EQUATIONERS
    path(
        "THEEQUATIONERS_profile",
        views.THEEQUATIONERS_profile,
        name="THEEQUATIONERS_profile",
    ),
    path(
        "THEEQUATIONERS_projects",
        views.THEEQUATIONERS_projects,
        name="THEEQUATIONERS_projects",
    ),
    path(
        "THEEQUATIONERS_financial",
        views.THEEQUATIONERS_financial,
        name="THEEQUATIONERS_financial",
    ),
    path(
        "THEEQUATIONERS_accreditation",
        views.THEEQUATIONERS_accreditation,
        name="THEEQUATIONERS_accreditation",
    ),
    path("THEEQUATIONERS_CBL", views.THEEQUATIONERS_CBL, name="THEEQUATIONERS_CBL"),
    path(
        "THEEQUATIONERS_officerdata",
        views.THEEQUATIONERS_officerdata,
        name="THEEQUATIONERS_officerdata",
    ),
    path(
        "THEEQUATIONERS_adviserdata",
        views.THEEQUATIONERS_adviserdata,
        name="THEEQUATIONERS_adviserdata",
    ),
    path(
        "THEEQUATIONERS_viewproject",
        views.THEEQUATIONERS_viewproject,
        name="THEEQUATIONERS_viewproject",
    ),
    path(
        "THEEQUATIONERS_viewfinancial",
        views.THEEQUATIONERS_viewfinancial,
        name="THEEQUATIONERS_viewfinancial",
    ),
    path(
        "THEEQUATIONERS_viewadviser",
        views.THEEQUATIONERS_viewadviser,
        name="THEEQUATIONERS_viewadviser",
    ),
    path(
        "THEEQUATIONERS_viewofficer",
        views.THEEQUATIONERS_viewofficer,
        name="THEEQUATIONERS_viewofficer",
    ),
    # SSGSSG_viewadviser
    path("SSG_profile", views.SSG_profile, name="SSG_profile"),
    path("SSG_projects", views.SSG_projects, name="SSG_projects"),
    path("SSG_financial", views.SSG_financial, name="SSG_financial"),
    path("SSG_accreditation", views.SSG_accreditation, name="SSG_accreditation"),
    path("SSG_CBL", views.SSG_CBL, name="SSG_CBL"),
    path("SSG_officerdata", views.SSG_officerdata, name="SSG_officerdata"),
    path("SSG_adviserdata", views.SSG_adviserdata, name="SSG_adviserdata"),
    path("SSG_viewproject", views.SSG_viewproject, name="SSG_viewproject"),
    path("SSG_viewfinancial", views.SSG_viewfinancial, name="SSG_viewfinancial"),
    path("SSG_viewadviser", views.SSG_viewadviser, name="SSG_viewadviser"),
    path("SSG_viewofficer", views.SSG_viewofficer, name="SSG_viewofficer"),
    # TECHNOCRATS
    path("TECHNOCRATS_profile", views.TECHNOCRATS_profile, name="TECHNOCRATS_profile"),
    path(
        "TECHNOCRATS_projects", views.TECHNOCRATS_projects, name="TECHNOCRATS_projects"
    ),
    path(
        "TECHNOCRATS_financial",
        views.TECHNOCRATS_financial,
        name="TECHNOCRATS_financial",
    ),
    path(
        "TECHNOCRATS_accreditation",
        views.TECHNOCRATS_accreditation,
        name="TECHNOCRATS_accreditation",
    ),
    path("TECHNOCRATS_CBL", views.TECHNOCRATS_CBL, name="TECHNOCRATS_CBL"),
    path(
        "TECHNOCRATS_officerdata",
        views.TECHNOCRATS_officerdata,
        name="TECHNOCRATS_officerdata",
    ),
    path(
        "TECHNOCRATS_adviserdata",
        views.TECHNOCRATS_adviserdata,
        name="TECHNOCRATS_adviserdata",
    ),
    path(
        "TECHNOCRATS_viewproject",
        views.TECHNOCRATS_viewproject,
        name="TECHNOCRATS_viewproject",
    ),
    path(
        "TECHNOCRATS_viewfinancial",
        views.TECHNOCRATS_viewfinancial,
        name="TECHNOCRATS_viewfinancial",
    ),
    path(
        "TECHNOCRATS_viewadviser",
        views.TECHNOCRATS_viewadviser,
        name="TECHNOCRATS_viewadviser",
    ),
    path(
        "TECHNOCRATS_viewofficer",
        views.TECHNOCRATS_viewofficer,
        name="TECHNOCRATS_viewofficer",
    ),
    # General View\
    path("Gen_Home", views.Gen_Home, name="Gen_Home"),
    path("Gen_FSTLP_profile", views.Gen_FSTLP_profile, name="Gen_FSTLP_profile"),
    path(
        "Gen_FSTLP_viewproject",
        views.Gen_FSTLP_viewproject,
        name="Gen_FSTLP_viewproject",
    ),
    path(
        "Gen_FSTLP_viewfinancial",
        views.Gen_FSTLP_viewfinancial,
        name="Gen_FSTLP_viewfinancial",
    ),
    path(
        "Gen_FSTLP_viewofficer",
        views.Gen_FSTLP_viewofficer,
        name="Gen_FSTLP_viewofficer",
    ),
    path(
        "Gen_FSTLP_viewadviser",
        views.Gen_FSTLP_viewadviser,
        name="Gen_FSTLP_viewadviser",
    ),
    path("Gen_SI_profile", views.Gen_SI_profile, name="Gen_SI_profile"),
    path("Gen_SI_viewproject", views.Gen_SI_viewproject, name="Gen_SI_viewproject"),
    path(
        "Gen_SI_viewfinancial", views.Gen_SI_viewfinancial, name="Gen_SI_viewfinancial"
    ),
    path("Gen_SI_viewadviser", views.Gen_SI_viewadviser, name="Gen_SI_viewadviser"),
    path("Gen_SI_viewofficer", views.Gen_SI_viewofficer, name="Gen_SI_viewofficer"),
    path(
        "Gen_THEEQUATIONERS_profile",
        views.Gen_THEEQUATIONERS_profile,
        name="Gen_THEEQUATIONERS_profile",
    ),
    path(
        "Gen_THEEQUATIONERS_viewproject",
        views.Gen_THEEQUATIONERS_viewproject,
        name="Gen_THEEQUATIONERS_viewproject",
    ),
    path(
        "Gen_THEEQUATIONERS_viewfinancial",
        views.Gen_THEEQUATIONERS_viewfinancial,
        name="Gen_THEEQUATIONERS_viewfinancial",
    ),
    path(
        "Gen_THEEQUATIONERS_viewadviser",
        views.Gen_THEEQUATIONERS_viewadviser,
        name="Gen_THEEQUATIONERS_viewadviser",
    ),
    path(
        "Gen_THEEQUATIONERS_viewofficer",
        views.Gen_THEEQUATIONERS_viewofficer,
        name="Gen_THEEQUATIONERS_viewofficer",
    ),
    path("Gen_SSG_profile", views.Gen_SSG_profile, name="Gen_SSG_profile"),
    path("Gen_SSG_viewproject", views.Gen_SSG_viewproject, name="Gen_SSG_viewproject"),
    path(
        "Gen_SSG_viewfinancial",
        views.Gen_SSG_viewfinancial,
        name="Gen_SSG_viewfinancial",
    ),
    path("Gen_SSG_viewadviser", views.Gen_SSG_viewadviser, name="Gen_SSG_viewadviser"),
    path("Gen_SSG_viewofficer", views.Gen_SSG_viewofficer, name="Gen_SSG_viewofficer"),
    path(
        "Gen_TECHNOCRATS_profile",
        views.Gen_TECHNOCRATS_profile,
        name="Gen_TECHNOCRATS_profile",
    ),
    path(
        "Gen_TECHNOCRATS_viewproject",
        views.Gen_TECHNOCRATS_viewproject,
        name="Gen_TECHNOCRATS_viewproject",
    ),
    path(
        "Gen_TECHNOCRATS_viewfinancial",
        views.Gen_TECHNOCRATS_viewfinancial,
        name="Gen_TECHNOCRATS_viewfinancial",
    ),
    path(
        "Gen_TECHNOCRATS_viewadviser",
        views.Gen_TECHNOCRATS_viewadviser,
        name="Gen_TECHNOCRATS_viewadviser",
    ),
    path(
        "Gen_TECHNOCRATS_viewofficer",
        views.Gen_TECHNOCRATS_viewofficer,
        name="Gen_TECHNOCRATS_viewofficer",
    ),
    # Individual Profile URLS
    path("individual_profile", individualProfile, name="Individual Profile"),
    path(
        "search_student_info_for_individual_profile/",
        search_student_info_for_individual,
        name="search_student_info_for_individual_profile",
    ),
    # Intake Interview URLS
    path("intake_interview/", intake_interview_view, name="Intake Interview"),
    path(
        "search_student_info_for_intake/",
        search_student_info_for_intake,
        name="search_student_info_for_intake",
    ),
    path(
        "individual_profile_sheet/",
        individual_profile_sheet,
        name="individual_profile_sheet",
    ),
    # Counseling App Views URLS
    path("counseling_app/", counseling_app, name="Counseling App With Scheduler"),
    path(
        "counseling_app/admin/",
        counseling_app_admin_view,
        name="Counseling App With Scheduler Admin View",
    ),
    path(
        "counseling_schedule_admin/",
        counseling_schedule_admin,
        name="counseling_schedule_admin",
    ),
    path(
        "counselor_scheduler/",
        counselor_scheduler,
        name="counselor_scheduler",
    ),
    # Counseling App Validator, Updator URLS
    path(
        "check_date_time_validity/",
        check_date_time_validity,
        name="check_date_time_validity",
    ),
    path(
        "update_counseling_schedule/",
        update_counseling_schedule,
        name="update_counseling_schedule",
    ),
    path(
        "delete_counseling_schedule/",
        delete_counseling_schedule,
        name="delete_counseling_schedule",
    ),
    # Exit Interview Views URLS
    path("exit_interview", exit_interview, name="Exit Interview"),
    path(
        "exit_interview/admin/",
        exit_interview_admin_view,
        name="Exit Interview Admin View",
    ),
    path(
        "search_exit_interview_request/",
        search_exit_interview_request,
        name="search_exit_interview_request",
    ),
    # Exit Interview Searcher, Validator,Updator URLS
    path("search_student_info/", search_student_info, name="search_student_info"),
    path(
        "check_date_time_validity_for_exit/",
        check_date_time_validity_for_exit,
        name="check_date_time_validity_for_exit",
    ),
    path(
        "update_exit_interview_status/",
        update_exit_interview_status,
        name="update_exit_interview_status",
    ),
    path(
        "delete_exit_interview_status/",
        delete_exit_interview_status,
        name="delete_exit_interview_status",
    ),
    path(
        "get_exit_interview_request/",
        get_exit_interview_request,
        name="get_exit_interview_request",
    ),
    # OJT Assessment Views URLS
    path("ojt_assessment", ojt_assessment, name="OJT Assessment"),
    path(
        "ojt_assessment/admin/",
        ojt_assessment_admin_view,
        name="OJT Assessment Admin View",
    ),
    # OJT Assessment Seacher, Validator, Updator URLS
    path(
        "search_ojt_assessment_request/",
        search_ojt_assessment_request,
        name="search_ojt_assessment_request",
    ),
    path("update_ojt_assessment/", update_ojt_assessment, name="update_ojt_assessment"),
    path("delete_ojt_assessment/", delete_ojt_assessment, name="delete_ojt_assessment"),
    path(
        "get_ojt_assessment_data/",
        get_ojt_assessment_data,
        name="get_ojt_assessment_data",
    ),
    # Individual Profile URLS
    path("individual_profile", individualProfile, name="Individual Profile"),
    path(
        "search_student_info_for_individual_profile/",
        search_student_info_for_individual,
        name="search_student_info_for_individual_profile",
    ),
    # Intake Interview URLS
    path("intake_interview/", intake_interview_view, name="Intake Interview"),
    path(
        "search_student_info_for_intake/",
        search_student_info_for_intake,
        name="search_student_info_for_intake",
    ),
    path(
        "individual_profile_sheet/<int:id>/",
        individual_profile_sheet,
        name="individual_profile_sheet",
    ),
    # Counseling App Views URLS
    path("counseling_app/", counseling_app, name="Counseling App With Scheduler"),
    path(
        "counseling_app/admin/",
        counseling_app_admin_view,
        name="Counseling App With Scheduler Admin View",
    ),
    # Counseling App Validator, Updator URLS
    path(
        "check_date_time_validity/",
        check_date_time_validity,
        name="check_date_time_validity",
    ),
    path(
        "update_counseling_schedule/",
        update_counseling_schedule,
        name="update_counseling_schedule",
    ),
    path(
        "delete_counseling_schedule/",
        delete_counseling_schedule,
        name="delete_counseling_schedule",
    ),
    # Exit Interview Views URLS
    path("exit_interview", exit_interview, name="Exit Interview"),
    path(
        "exit_interview/admin/",
        exit_interview_admin_view,
        name="Exit Interview Admin View",
    ),
    path(
        "search_exit_interview_request/",
        search_exit_interview_request,
        name="search_exit_interview_request",
    ),
    # Exit Interview Searcher, Validator,Updator URLS
    path("search_student_info/", search_student_info, name="search_student_info"),
    path(
        "check_date_time_validity_for_exit/",
        check_date_time_validity_for_exit,
        name="check_date_time_validity_for_exit",
    ),
    path(
        "update_exit_interview_status/",
        update_exit_interview_status,
        name="update_exit_interview_status",
    ),
    path(
        "delete_exit_interview_status/",
        delete_exit_interview_status,
        name="delete_exit_interview_status",
    ),
    path(
        "get_exit_interview_request/",
        get_exit_interview_request,
        name="get_exit_interview_request",
    ),
    # OJT Assessment Views URLS
    path("ojt_assessment", ojt_assessment, name="OJT Assessment"),
    path(
        "ojt_assessment/admin/",
        ojt_assessment_admin_view,
        name="OJT Assessment Admin View",
    ),
    # OJT Assessment Seacher, Validator, Updator URLS
    path(
        "search_ojt_assessment_request/",
        search_ojt_assessment_request,
        name="search_ojt_assessment_request",
    ),
    path("update_ojt_assessment/", update_ojt_assessment, name="update_ojt_assessment"),
    path("delete_ojt_assessment/", delete_ojt_assessment, name="delete_ojt_assessment"),
    path(
        "get_ojt_assessment_data/",
        get_ojt_assessment_data,
        name="get_ojt_assessment_data",
    ),
    path("guidance_transaction", guidance_transaction, name="guidance_transaction"),
    path(
        "daily_montly_guidance_transaction/",
        daily_montly_guidance_transaction,
        name="daily_montly_guidance_transaction",
    ),
    path(
        "show_transaction_specific_date/",
        show_transaction_specific_date,
        name="show_transaction_specific_date",
    ),
    path(
        "sort_counseling_app_admin_view/",
        sort_counseling_app_admin_view,
        name="sort_counseling_app_admin_view",
    ),
    path(
        "sort_exit_interview_admin_view/",
        sort_exit_interview_admin_view,
        name="sort_exit_interview_admin_view",
    ),
    # COMMUNITY INVOLVEMENT
    path("programs/", views.programs, name="programs"),
    path("projects/", views.projects, name="projects"),
    path("reports/", views.reports, name="reports"),
    # Forms
    path("program-form/", views.program_form, name="program-form"),
    path("project-form/", views.project_form, name="project-form"),
    # Add
    path("program-form/add_program/", views.add_program, name="add_program"),
    path("project-form/add_project/", views.add_project, name="add_project"),
    # Delete
    path(
        "program-form/archive_program/<int:id>/",
        views.archive_program,
        name="archive_program",
    ),
    path(
        "project-form/archive_project/<int:id>/",
        views.archive_project,
        name="archive_project",
    ),
    # Mode
    path("projects/gcash-mode", views.gcash_mode, name="gcash-mode"),
    path("projects/bank-mode", views.bank_mode, name="bank-mode"),
    path("projects/volunteer-mode", views.volunteer_mode, name="volunteer-mode"),
    path("reports/", views.reports, name="reports"),
    path("reports-all/", views.reports_all, name="reports-all"),
    path("reports-find/", views.reports_find, name="reports-find"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("donation-dashboard/", views.donation_dashboard, name="donation_dashboard"),
    path("gcash-dashboard/", views.gcash_dashboard, name="gcash_dashboard"),
    path("banks-dashboard/", views.banks_dashboard, name="banks_dashboard"),
    path("volunteer-dashboard/", views.volunteer_dashboard, name="volunteer_dashboard"),
    path("donation-validate/", views.donation_validate, name="donation-validate"),
    path("donation_accept/<int:id>/", views.donation_accept, name="donation_accept"),
    path("donation_decline/<int:id>/", views.donation_decline, name="donation_decline"),
    path("gcash_mode_admin/<int:id>/", views.gcash_mode_admin, name="gcash_mode_admin"),
    path("bank_mode_admin/<int:id>/", views.bank_mode_admin, name="bank_mode_admin"),
    path("donation_filter/", views.donation_filter, name="donation_filter"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

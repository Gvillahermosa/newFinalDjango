from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import studentInfo, Equipment, BorrowingRecord
from .models import (
    studentInfo,
    RequestedGMC,
    Equipment,
    Schedule,
    ProcurementItem,
    Storage,
    ExcelData,
    BorrowingRecord,
)
from django.utils.timezone import localtime, now
from .forms import ScheduleForm, UploadFileForm, UpdateSerialNoForm, UploadExcelForm
from datetime import datetime
from .forms import (
    CounselingSchedulerForm,
    IndividualProfileForm,
    FileUpload,
    UploadFileForm,
    ExitInterviewForm,
    OjtAssessmentForm,
)

from .models import (
    TestArray,
    studentInfo,
    counseling_schedule,
    exit_interview_db,
    OjtAssessment,
    IndividualProfileBasicInfo,
    IntakeInverView,
    GuidanceTransaction,
)
import json
import openpyxl
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Sum, F
from django.core.files.storage import FileSystemStorage
from .forms import UploadExcelForm, ExcelDataForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Alumni, graduateForm, Event, JobFair, Yearbook
from django.utils import timezone
from django.db.models import Avg
from django.core.mail import send_mail, BadHeaderError
import socket
from django.template.defaulttags import register
from .forms import OfficerForm
from .forms import ProjectForm
from .forms import FinancialStatementForm, AdminLoginForm, LoginForm
from .forms import AccreditationForm, AdviserForm
from .models import Project, Accreditation, Adviser, OfficerLogin
from .models import FinancialStatement, Officer, AdminLogin
from .models import Storage, Equipment
from django.http import HttpResponse
from medicalv2.models import Student
# Create your views here.
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.contrib import messages
from .models import studentInfo
import calendar
from .models import (
    Program,
    Projects,
    MOD,
    QrDonation,
)
from .decorators import sao_admin_required, medical_admin_required



def upload_student_data(request):
    if request.method == "POST":
        if "excel_file" in request.FILES:
            excel_file = request.FILES["excel_file"]
            if "student-profile" in excel_file.name and excel_file.name.endswith((".xlsx", ".xls")):
                fs = FileSystemStorage()
                filename = fs.save(excel_file.name, excel_file)
                file_path = fs.path(filename)

                try:
                    df = pd.read_excel(file_path)
                    for _, row in df.iterrows():
                        # Save to medical_student table
                        medical_student = Student(
                            student_id=row["studID"],
                            lrn=row["lrn"],
                            lastname=row["lastname"],
                            firstname=row["firstname"],
                            middlename=row["middlename"],
                            degree=row["degree"],
                            year_level=row["yearlvl"],
                            sex=row["sex"],
                            email=row["emailadd"],
                            contact_number=row["contact"]
                        )
                        medical_student.save()

                        # Save to student_info table
                        student_info = studentInfo(
                            studID=row["studID"],
                            lrn=row["lrn"],
                            lastname=row["lastname"],
                            firstname=row["firstname"],
                            middlename=row["middlename"],
                            degree=row["degree"],
                            yearlvl=row["yearlvl"],
                            sex=row["sex"],
                            emailadd=row["emailadd"],
                            contact=row["contact"]
                        )
                        student_info.save()
                    
                    messages.success(request, "Data imported successfully!")
                except Exception as e:
                    messages.error(request, f"Error importing data: {e}")

                fs.delete(filename)
                return redirect("studentLife_system:upload_student_data")
            else:
                messages.error(request, "Invalid file format or name. Please upload an Excel file with 'student-profile' in the filename.")
                return redirect("studentLife_system:upload_student_data")
        else:
            messages.error(request, "No file uploaded")
            return redirect("studentLife_system:upload_student_data")

    return render(request, "settingSecurity/settingSecurity.html")



# Student 
def home(request):
    return render(request, "studentLife/main.html")

def homepage(request):
    return render(request, "studentLife/main_page.html")

# Admin
def adminhome(request):
    return render(request, "adminUser/adminmain.html")

def adminGmc(request):
    return render(request, "adminUser/adminRequestedGmc.html")

def gmcform(request):
    return render(request, "adminUser/gmcform.html")


import logging

logger = logging.getLogger(__name__)

def update_return_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            record_id = data.get("record_id")
            if not record_id:
                return JsonResponse({"status": "error", "message": "Record ID not provided"}, status=400)
            
            record = BorrowingRecord.objects.get(id=record_id)
            record.is_returned = True
            record.date_returned = timezone.now().date()
            record.save()
            return JsonResponse({"status": "success", "date_returned": record.date_returned})
        except BorrowingRecord.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Record not found"}, status=404)
        except Exception as e:
            logger.error(f"Error updating return status: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Request for GoodMoral Certificate Student Side
def requestedgmc(request):
    student = None

    if request.user.is_authenticated:
        try:
            student = studentInfo.objects.get(user_student=request.user)
        except studentInfo.DoesNotExist:
            student = None
            messages.error(request, "Student not found")

    if request.method == "POST":
        reason = request.POST.get("reason")
        if reason:
            try:
                student = studentInfo.objects.get(user_student=request.user)
                RequestedGMC.objects.create(student=student, reason=reason)
                messages.success(request, "Good Moral Certificate request submitted successfully")
                return redirect('studentLife_system:requestgmc')
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")

    context = {"student": student}
    return render(request, "studentLife/requestgmc.html", context)


# Processing Goodmoral Certificate Admin side 
def adminRequestedGmc(request):
    gmc_requests = RequestedGMC.objects.filter(processed=False)
    context = {"gmc_requests": gmc_requests}
    return render(request, "adminUser/adminRequestedGmc.html", context)

# Making of Goodmoral Certificate
def generateGmc(request, request_id):
    try:
        gmc_request = RequestedGMC.objects.get(id=request_id)
        student = gmc_request.student
        or_num = request.GET.get('ornum', '')  # Capture the OR Number from the query parameters

        # Mark the request as processed
        gmc_request.or_num = or_num
        gmc_request.processed = True
        gmc_request.save()

        context = {
            "student_name": f"{student.firstname} {student.lastname}",
            "student_degree": student.degree,
            "request_date": localtime(gmc_request.request_date).strftime('%B %d, %Y'),
            "reason": gmc_request.reason,
            "year": student.yearlvl,
            "today_date": localtime(now()).strftime('%B %d, %Y'),
            "or_num": or_num  # Include the OR Number in the context
        }
        return render(request, "adminUser/good_moral_certificate.html", context)
    except RequestedGMC.DoesNotExist:
        messages.error(request, "GMC Request not found")
        return redirect('adminRequestedGmc')


def processed_gmc_transactions(request):
    # Fetch all processed GMC requests
    processed_gmcs = RequestedGMC.objects.filter(processed=True)
    
    return render(request, 'adminUser/transactionsGMC.html', {
        'transaction_records': processed_gmcs
    })


# Calendar Of Activities Student Side 
def monthlyCalendar(request):
    schedules = Schedule.objects.all()
    sched_res = {}

    for schedule in schedules:
        sched_res[schedule.sched_Id] = {
            'id': schedule.sched_Id,
            'title': schedule.title,
            'description': schedule.description,
            'start_datetime': schedule.start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'end_datetime': schedule.end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'sdate': schedule.start_datetime.strftime("%B %d, %Y %I:%M %p"),
            'edate': schedule.end_datetime.strftime("%B %d, %Y %I:%M %p")
        }

    context = {
        'sched_json': json.dumps(sched_res)
    }
    return render(request, "studentLife/monthlyCalendar.html", context)

# Calendar of Activities Admin 
def monthlyCalendarAdmin(request):
    schedules = Schedule.objects.all()
    sched_res = {}

    for schedule in schedules:
        sched_res[schedule.sched_Id] = {
            'id': schedule.sched_Id,
            'title': schedule.title,
            'description': schedule.description,
            'start_datetime': schedule.start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'end_datetime': schedule.end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            'sdate': schedule.start_datetime.strftime("%B %d, %Y %I:%M %p"),
            'edate': schedule.end_datetime.strftime("%B %d, %Y %I:%M %p")
        }

    context = {
        'sched_json': json.dumps(sched_res)
    }
    return render(request, 'adminUser/monthlyCalendarAdmin.html', context)


# Save Schedule
def save_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('id')
        if schedule_id:
            schedule = get_object_or_404(Schedule, pk=schedule_id)
            form = ScheduleForm(request.POST, instance=schedule)
        else:
            form = ScheduleForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:monthlyCalendarAdmin')
    else:
        form = ScheduleForm()
    return render(request, 'adminUser/monthlyCalendarAdmin.html', {'form': form})


# Update schedule start and end datetime drag & drop
def update_schedule(request, schedule_id):
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')

        if start_datetime and end_datetime:
            schedule.start_datetime = start_datetime
            schedule.end_datetime = end_datetime
            schedule.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data provided.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

# Delete Schedule
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    schedule.delete()
    return redirect('studentLife_system:monthlyCalendarAdmin')

def equipmentTracker(request):
    # Get the logged-in user
    user = request.user

    # Initialize borrowing records
    borrowing_records = BorrowingRecord.objects.none()

    # Check if the user is authenticated
    if user.is_authenticated:
        # Get the studentInfo instance for the logged-in user
        try:
            student = studentInfo.objects.get(user_student=user)
        except studentInfo.DoesNotExist:
            student = None

        # Filter borrowing records based on the studentInfo instance
        if student:
            borrowing_records = BorrowingRecord.objects.filter(student=student)

    context = {
        'borrowing_records': borrowing_records
    }
    return render(request, 'studentLife/equipmentTracker.html', context)

def equipmentTrackerAdmin(request):
    student = None
    borrowing_records = BorrowingRecord.objects.all()
    if request.method == "GET" and "search" in request.GET:
        search_id = request.GET.get("search")
        if search_id:
            try:
                student = studentInfo.objects.get(studID=search_id)
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")

    all_equipment = Equipment.objects.all()

    context = {
        'student': student,
        'all_equipment': all_equipment,
        'borrowing_records': borrowing_records
    }
    return render(request, 'adminUser/equipmentTrackerAdmin.html', context)


# Add Equipment
def addEquipment(request):
    if request.method == "POST":
        equipment_name = request.POST.get("equipmentname")
        serial = request.POST.get("serialnum")
        
        if equipment_name and serial:
            # Add to Equipment table
            new_equipment = Equipment(equipmentName=equipment_name, equipmentSN=serial)
            new_equipment.save()
            
            messages.success(request, "Equipment added successfully")
            return redirect('studentLife_system:addEquipment')
        else:
            messages.error(request, "Please provide both equipment name and serial number")
    
    # Fetch all equipment objects from the database
    all_equipment = Equipment.objects.all()

    # Pass the equipment objects to the template context
    return render(request, 'adminUser/addEquipment.html', {'all_equipment': all_equipment})

def save_equipment_borrowing(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        equipment_id = request.POST.get("equipmentname")
        date_borrowed = request.POST.get("dateborrowed")

        if student_id and equipment_id and date_borrowed:
            try:
                student = studentInfo.objects.get(studID=student_id)
                equip = Equipment.objects.get(itemId=equipment_id)
                BorrowingRecord.objects.create(student=student, equipment=equip, date_borrowed=date_borrowed)
                messages.success(request, "Equipment borrowing record saved successfully")
            except studentInfo.DoesNotExist:
                messages.error(request, "Student not found")
            except Equipment.DoesNotExist:
                messages.error(request, "Equipment not found")
        else:
            messages.success(request, "Equipment returned successfully")

    return redirect('studentLife_system:equipmentTrackerAdmin')


#Transaction Report

def transactionreport(request):
    return render(request, 'adminUSer/transactions.html')


#FOR PPMP TRACKER

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            if not uploaded_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'File is not an excel file.')
            else:
                try:
                    handle_uploaded_file(uploaded_file)
                    messages.success(request, 'File uploaded successfully')
                except ValueError as e:
                    messages.error(request, str(e))
        else:
            messages.error(request, 'File upload failed')
    else:
        form = UploadFileForm()
    return render(request, 'adminUser/ppmpTracker/ppmp.html', {'form': form})

def handle_uploaded_file(f):
    df = pd.read_excel(f)

    for index, row in df.iterrows():
        procurement_item, created = ProcurementItem.objects.update_or_create(
            itemid=row['id'],
            defaults={
                'item': row['item'],
                'quantity': row['quantity'],
                'unit': row['unit'],
                'estimated_budget': row['estimated_budget'],
                'mode_of_procurement': row['mode_of_procurement'],
                'jan': row['jan'],
                'feb': row['feb'],
                'mar': row['mar'],
                'apr': row['apr'],
                'may': row['may'],
                'jun': row['jun'],
                'jul': row['jul'],
                'aug': row['aug'],
                'sep': row['sep'],
                'oct': row['oct'],
                'nov': row['nov'],
                'dec': row['dec'],
                'unit_price': row['unit_price']
            }
        )

    print("Database updated from Excel file.")

# display the items, though need pag further design for printing huhu

def display_items(request):
    items = ProcurementItem.objects.all()
    return render(request, 'adminUser/ppmpTracker/display_items.html', {'items': items})

# status

@method_decorator(csrf_exempt, name='dispatch')
class UpdateStatusView(View):
    def post(self, request):
        item_id = request.POST.get('item_id')
        new_status = request.POST.get('new_status')
        serial_no = request.POST.get('serial_no', None)

        try:
            item = ProcurementItem.objects.get(itemid=item_id)
            item.status = new_status
            item.save()

            if new_status == 'delivered':
                # Create a new Storage entry
                storage = Storage.objects.create(procurement_item=item, serial_no=serial_no)

                # Also create a new equipment entry
                equipment_name = item.item  # Assuming 'item' is the name of the equipment
                equipmentSN = serial_no if serial_no else 'No Serial Number'
                Equipment.objects.create(equipmentName=equipment_name, equipmentSN=equipmentSN)

            return JsonResponse({'status': 'success'}, status=200)
        except ProcurementItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def display_storage_items(request):
    storage_items = Storage.objects.all()
    return render(request, 'adminUser/ppmpTracker/display_storage_items.html', {'storage_items': storage_items})

def update_serial_no(request, storage_id):
    storage_item = Storage.objects.get(id=storage_id)
    
    if request.method == 'POST':
        form = UpdateSerialNoForm(request.POST, instance=storage_item)
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:display_storage_items')
    else:
        form = UpdateSerialNoForm(instance=storage_item)

    return render(request, 'adminUser/ppmpTracker/update_serial_no.html', {'form': form, 'storage_item': storage_item})


# Day five: try to print the purchased items:)
# Day six: total cost per item purchased, final total cost

def purchased_items(request):
   items = ProcurementItem.objects.filter(status="purchased")
   for item in items:
        item.total_cost = item.quantity * item.unit_price

   total_cost_sum = items.aggregate(total_cost_sum=Sum(F('quantity') * F('unit_price')))['total_cost_sum']


   return render(request, 'adminUser/ppmpTracker/purchased_items.html', {'items': items, 'total_cost_sum': total_cost_sum})

def lnd_file(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)
            
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            for row in ws.iter_rows(min_row=7, max_col=10, values_only=True):
                title_of_l_d = row[0] if row[0] is not None else ''
                frequency = row[1] if row[1] is not None else ''
                category = row[2] if row[2] is not None else ''
                expected_number_of_participants = row[3] if row[3] is not None else ''
                duration = row[4] if row[4] is not None else ''
                registration_fees = row[5] if row[5] is not None else ''
                travelling_expenses = row[6] if row[6] is not None else ''
                planned_total_budget = row[7] if row[7] is not None else ''
                actual_total_budget = row[8] if row[8] is not None else ''

                excel_data, created = ExcelData.objects.update_or_create(
                    title_of_l_d=title_of_l_d,
                    defaults={
                        'frequency': frequency,
                        'category': category,
                        'expected_number_of_participants': expected_number_of_participants,
                        'duration': duration,
                        'registration_fees': registration_fees,
                        'travelling_expenses': travelling_expenses,
                        'planned_total_budget': planned_total_budget,
                        'actual_total_budget': actual_total_budget
                    }
                )
            
            messages.success(request, "L&D File Uploaded!")
           
    else:
        form = UploadExcelForm()
    return render(request, 'adminUser/ppmpTracker/learning_dev.html', {'form': form})

def edit_excel_data(request):
    excel_data = ExcelData.objects.all()
    return render(request, 'adminUser/ppmpTracker/edit_excel_data.html', {'excel_data': excel_data})

def update_excel_data(request, pk):
    excel_data = get_object_or_404(ExcelData, pk=pk)
    if request.method == 'POST':
        form = ExcelDataForm(request.POST, instance=excel_data)
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:edit_excel_data')
    else:
        form = ExcelDataForm(instance=excel_data)
    return render(request, 'adminUser/ppmpTracker/update_excel_data.html', {'form': form})


#ALUMNI
def idRequest(request):
    return render(request, 'alumni/users/id_alumni.html')


def search_id(request):
    if request.method == 'GET':
        student_id = request.GET.get('student_id')
        if student_id:
            try:
                student_obj = studentInfo.objects.get(studID=student_id)
                return render(request, 'alumni/users/id_alumni.html', {'student': student_obj})
            except studentInfo.DoesNotExist:
                
                messages.error(request, 'No student found with the provided ID.')
                return render(request, 'alumni/users/id_alumni.html')
        else:
            
            messages.error(request, 'Please provide a student ID.')
            return render(request, 'alumni/users/id_alumni.html')
    else:
        
        return render(request, 'alumni/users/id_alumni.html')
    

def add_alumni(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        email_add = request.POST.get('email_add')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        alumnidate = request.POST.get('alumnidate')
        alumnibirthday = request.POST.get('alumnibirthday')
        alumnicontact = request.POST.get('alumnicontact')
        sssgsis = request.POST.get('sssgsis')
        tin = request.POST.get('tin')
        parentguardian = request.POST.get('parentguardian')
        alumniaddress = request.POST.get('alumniaddress')
        degree = request.POST.get('degree')
        sex = request.POST.get('sex')
        
        if Alumni.objects.filter(student__studID=student_id).exists():
            messages.error(request, f'You already requested Alumni ID!')
            return redirect('studentLife_system:idRequest')

        student = get_object_or_404(studentInfo, studID=student_id)
        alumni = Alumni.objects.create(student=student, firstname=firstname, lastname=lastname,
                               alumnidate=alumnidate, alumnibirthday=alumnibirthday,
                               alumnicontact=alumnicontact, sssgsis=sssgsis, tin=tin,
                               parentguardian=parentguardian, alumniaddress=alumniaddress,email_add=email_add,degree=degree,sex=sex)
        alumni_id = alumni.alumniID
        
        messages.success(request, f'Your request is successful! Your alumni ID requested is {alumni_id}')
        
        return redirect('studentLife_system:idRequest')
    else:
        return redirect('studentLife_system:idRequest')    
    

def graduateTracer(request):
    return render(request, 'alumni/users/graduateTracer.html')

def search_id2(request):
    if request.method == 'GET':
        student_id = request.GET.get('student_id')
        if student_id:
            try:
                
                alumni_obj = Alumni.objects.get(student__studID=student_id)
                
                
                if graduateForm.objects.filter(student__studID=student_id).exists():
                    messages.error(request, 'You have already filled out this form.')
                    return render(request, 'alumni/users/graduateTracer.html')
                
                return render(request, 'alumni/users/graduateTracer.html', {'alumni': alumni_obj})
            except Alumni.DoesNotExist:
                messages.error(request, 'Not Found! Please request first for alumni ID')
                return render(request, 'alumni/users/graduateTracer.html')
        else:
            messages.error(request, 'Please provide a student ID.')
            return render(request, 'alumni/users/graduateTracer.html')
    else:
        return render(request, 'alumni/users/graduateTracer.html')
    
def graduateTracer_submit(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        degree = request.POST.get('degree')
        email_add = request.POST.get('email_add')
        contactnum = request.POST.get('contactnum')
        sex = request.POST.get('sex')
        alumniaddress = request.POST.get('alumniaddress')
        dategraduated = request.POST.get('dategraduated')
        nameoforganization = request.POST.get('nameoforganization')
        employmenttype = request.POST.get('employmentype')
        occupationalClass = request.POST.get('occupationalClass')
        gradscholrelated = request.POST.get('gradscholrelated')
        yearscompany = request.POST.get('yearscompany')
        placework = request.POST.get('placework')
        firstjobgraduate = request.POST.get('firstjobgraduate')
        reasonstayingjob = request.POST.get('reasonstayingjob')
        designation = request.POST.get('designation')
        status = request.POST.get('status')
        monthlyincome = request.POST.get('monthlyincome')
        workwhileworking = request.POST.get('workwhileworking')
        ifnotworking = request.POST.get('ifnotworking')
        reasontimegap = request.POST.get('reasontimegap')
        natureemployment = request.POST.get('natureemployment')
        numberofyears = request.POST.get('numberofyears')
        monthlyincome2 = request.POST.get('monthlyincome2')
        academicprofession = request.POST.get('academicprofession')
        researchcapability = request.POST.get('researchcapability')
        learningefficiency = request.POST.get('learningefficiency')
        peopleskills = request.POST.get('peopleskills')
        problemsolvingskills = request.POST.get('problemsolvingskills')
        informationtechnologyskills = request.POST.get('informationtechnologyskills')
        meetingprofessionalneeds = request.POST.get('meetingprofessionalneeds')
        communityfield = request.POST.get('communityfield')
        globalfield = request.POST.get('globalfield')
        criticalskills = request.POST.get('criticalskills')
        rangeofcourses = request.POST.get('rangeofcourses')
        relevanceprofession = request.POST.get('relevanceprofession')
        extracurricular = request.POST.get('extracurricular')
        premiumresearch = request.POST.get('premiumresearch')
        interlearning = request.POST.get('interlearning')
        teachingenvironment = request.POST.get('teachingenvironment')
        qualityinstruction = request.POST.get('qualityinstruction')
        teachrelationship = request.POST.get('teachrelationship')
        libraryresources = request.POST.get('libraryresources')
        labresources = request.POST.get('labresources')
        classize = request.POST.get('classize')
        profexpertise = request.POST.get('profexpertise')
        profsubjectmatter = request.POST.get('profsubjectmatter')
        enrollmentdate = request.POST.get('enrollmentdate')
        studiesdegree = request.POST.get('studiesdegree')
        universityinstitution = request.POST.get('universityinstitution')
        studiesAddress = request.POST.get('studiesAddress')
        pursuingstudies = request.POST.get('pursuingstudies')  
        department = request.POST.get('department')  
        salaryimprovement = request.POST.get('salaryimprovement')  
        opportunitiesabroad = request.POST.get('opportunitiesabroad')  
        personalitydevelopment = request.POST.get('personalitydevelopment')  
        technologiesvaluesformation = request.POST.get('technologiesvaluesformation')  
        try:
            student = get_object_or_404(studentInfo, studID=student_id)
        except:
            messages.error(request, 'Student ID not found.')
            return redirect('studentLife_system:graduateTracer')

        try:
            alumni = get_object_or_404(Alumni, student=student)
        except:
            messages.error(request, 'No Alumni matches the given query.')
            return redirect('studentLife_system:graduateTracer')
        gradform = graduateForm.objects.create( alumniID=alumni,student=student,
                                    degree=degree,
                                    email_add=email_add,
                                    contactnum=contactnum,
                                    sex=sex,
                                    firstname=firstname,
                                    lastname=lastname,
                                    alumniaddress=alumniaddress,
                                    dategraduated=dategraduated,
                                    nameoforganization=nameoforganization,
                                    employmenttype=employmenttype,
                                    occupationalClass=occupationalClass,
                                    gradscholrelated=gradscholrelated,
                                    yearscompany=yearscompany,
                                    placework=placework,
                                    firstjobgraduate=firstjobgraduate,
                                    reasonstayingjob=reasonstayingjob,
                                    designation=designation,
                                    status=status,
                                    monthlyincome=monthlyincome,
                                    workwhileworking=workwhileworking,
                                    ifnotworking=ifnotworking,
                                    reasontimegap=reasontimegap,
                                    numberofyears=numberofyears,
                                    monthlyincome2=monthlyincome2,
                                    academicprofession=academicprofession,
                                    researchcapability=researchcapability,
                                    learningefficiency=learningefficiency,
                                    peopleskills=peopleskills,
                                    problemsolvingskills=problemsolvingskills,
                                    informationtechnologyskills=informationtechnologyskills,
                                    communityfield=communityfield,
                                    globalfield=globalfield,
                                    criticalskills=criticalskills,
                                    rangeofcourses=rangeofcourses,
                                    relevanceprofession=relevanceprofession,
                                    extracurricular=extracurricular,
                                    premiumresearch=premiumresearch,
                                    interlearning=interlearning,
                                    teachingenvironment=teachingenvironment,
                                    qualityinstruction=qualityinstruction,
                                    teachrelationship=teachrelationship,
                                    libraryresources=libraryresources,
                                    labresources=labresources,
                                    classize=classize,
                                    profexpertise=profexpertise,
                                    profsubjectmatter=profsubjectmatter,
                                    enrollmentdate=enrollmentdate,
                                    studiesdegree=studiesdegree,
                                    universityinstitution=universityinstitution,
                                    studiesAddress=studiesAddress,
                                    pursuingstudies=pursuingstudies,
                                    department=department,
                                    natureemployment = natureemployment,
                                    meetingprofessionalneeds=meetingprofessionalneeds,
                                    salaryimprovement=salaryimprovement,
                                    opportunitiesabroad=opportunitiesabroad,
                                    personalitydevelopment=personalitydevelopment,
                                    technologiesvaluesformation=technologiesvaluesformation,
                                    
    )
        alumni_id = alumni.alumniID
        
        messages.success(request, f'Your request is successful! Your alumni ID is {alumni_id}')
        return redirect('studentLife_system:graduateTracer')
    else:
        return redirect('studentLife_system:graduateTracer')    
    
def alumni_events(request):
    events = Event.objects.all()    
    return render(request, 'alumni/users/alumni_events.html', {'events': events})    


def jobfairs(request):
    job_fairs = JobFair.objects.order_by('-posted_date')
    return render(request, 'alumni/users/jobfairs.html', {'job_fairs': job_fairs})



def yearbook(request):
    return render(request, 'alumni/users/yearbook.html')


def search_yearbook(request):
    if request.method == 'GET':
        first_name = request.GET.get('yeargetfirstname')
        last_name = request.GET.get('yeargetlastname')

        if first_name and last_name:
            try:
               
                first_name = first_name.lower()
                last_name = last_name.lower()

       
                yearbook_entry = Yearbook.objects.get(yearbookFirstname__iexact=first_name, yearbookLastname__iexact=last_name)
                return render(request, 'alumni/users/yearbook.html', {'yearbook_entry': yearbook_entry})
            except Yearbook.DoesNotExist:
                return render(request, 'alumni/users/yearbook.html', {'error_message': 'No yearbook entry found.'})
        else:
            return render(request, 'alumni/users/yearbook.html', {'error_message': 'Please provide both first name and last name in the search.'})
    else:
        return render(request, 'alumni/users/yearbook.html')


def transaction_alumni(request):
    return render(request, 'alumni/users/transaction_alumni.html')

def transac_search(request):
    context = {}
    
    if request.method == 'POST':
        transac_choice = request.POST.get('transac_choice')
        transac_frequency = request.POST.get('transac_frequency')

        current_month = timezone.now().month

        # Alumni ID Requests
        if transac_choice == 'Alumni ID Requests':
            if transac_frequency == 'Monthly':
                alumni_requests = Alumni.objects.filter(alumnidate__month=current_month)
            elif transac_frequency == 'Yearly':
                alumni_requests = Alumni.objects.filter(alumnidate__year=timezone.now().year)
            else:
                alumni_requests = Alumni.objects.all()

            total_count = alumni_requests.count()
            context = {
                'alumni_requests': alumni_requests,
                'transac_frequency': transac_frequency,
                'total_count': total_count,
                'transac_choice': transac_choice
            }

        # Graduate Tracer
        elif transac_choice == 'Graduate Tracer':
            if transac_frequency == 'Monthly':
                graduate_tracer_data = graduateForm.objects.filter(enrollmentdate__month=current_month)
            elif transac_frequency == 'Yearly':
                graduate_tracer_data = graduateForm.objects.filter(enrollmentdate__year=timezone.now().year)
            else:
                graduate_tracer_data = graduateForm.objects.all()

            total_count = graduate_tracer_data.count()
            has_reports = total_count > 0

            # Aggregate weighted means
            weighted_means = {
                'academicprofession': graduate_tracer_data.aggregate(Avg('academicprofession'))['academicprofession__avg'],
                'researchcapability': graduate_tracer_data.aggregate(Avg('researchcapability'))['researchcapability__avg'],
                'learningefficiency': graduate_tracer_data.aggregate(Avg('learningefficiency'))['learningefficiency__avg'],
                'peopleskills': graduate_tracer_data.aggregate(Avg('peopleskills'))['peopleskills__avg'],
                'problemsolvingskills': graduate_tracer_data.aggregate(Avg('problemsolvingskills'))['problemsolvingskills__avg'],
                'informationtechnologyskills': graduate_tracer_data.aggregate(Avg('informationtechnologyskills'))['informationtechnologyskills__avg'],
                'meetingprofessionalneeds': graduate_tracer_data.aggregate(Avg('meetingprofessionalneeds'))['meetingprofessionalneeds__avg'],
                'communityfield': graduate_tracer_data.aggregate(Avg('communityfield'))['communityfield__avg'],
                'globalfield': graduate_tracer_data.aggregate(Avg('globalfield'))['globalfield__avg'],
                'criticalskills': graduate_tracer_data.aggregate(Avg('criticalskills'))['criticalskills__avg'],
                'salaryimprovement': graduate_tracer_data.aggregate(Avg('salaryimprovement'))['salaryimprovement__avg'],
                'opportunitiesabroad': graduate_tracer_data.aggregate(Avg('opportunitiesabroad'))['opportunitiesabroad__avg'],
                'personalitydevelopment': graduate_tracer_data.aggregate(Avg('personalitydevelopment'))['personalitydevelopment__avg'],
                'technologiesvaluesformation': graduate_tracer_data.aggregate(Avg('technologiesvaluesformation'))['technologiesvaluesformation__avg'],
                'rangeofcourses': graduate_tracer_data.aggregate(Avg('rangeofcourses'))['rangeofcourses__avg'],
                'relevanceprofession': graduate_tracer_data.aggregate(Avg('relevanceprofession'))['relevanceprofession__avg'],
                'extracurricular': graduate_tracer_data.aggregate(Avg('extracurricular'))['extracurricular__avg'],
                'premiumresearch': graduate_tracer_data.aggregate(Avg('premiumresearch'))['premiumresearch__avg'],
                'interlearning': graduate_tracer_data.aggregate(Avg('interlearning'))['interlearning__avg'],
                'teachingenvironment': graduate_tracer_data.aggregate(Avg('teachingenvironment'))['teachingenvironment__avg'],
                'qualityinstruction': graduate_tracer_data.aggregate(Avg('qualityinstruction'))['qualityinstruction__avg'],
                'teachrelationship': graduate_tracer_data.aggregate(Avg('teachrelationship'))['teachrelationship__avg'],
                'libraryresources': graduate_tracer_data.aggregate(Avg('libraryresources'))['libraryresources__avg'],
                'labresources': graduate_tracer_data.aggregate(Avg('labresources'))['labresources__avg'],
                'classize': graduate_tracer_data.aggregate(Avg('classize'))['classize__avg'],
                'profexpertise': graduate_tracer_data.aggregate(Avg('profexpertise'))['profexpertise__avg'],
                'profsubjectmatter': graduate_tracer_data.aggregate(Avg('profsubjectmatter'))['profsubjectmatter__avg']
            }

            context = {
                'graduate_tracer_data': graduate_tracer_data,
                'transac_frequency': transac_frequency,
                'total_count': total_count,
                'transac_choice': transac_choice,
                'weighted_means': weighted_means,
                'has_reports': has_reports
            }

    return render(request, 'alumni/users/transaction_alumni.html', context)


# admin alumni
def admin_id_request(request):
    alumni_requests = Alumni.objects.all()
    return render(request, 'alumni/users/admin_idRequest.html', {'alumni_requests': alumni_requests})

def approve_alumni_request(request, alumni_id):
    if request.method == 'POST':
        alumni = get_object_or_404(Alumni, pk=alumni_id)
        email_add = alumni.email_add

        try:
            send_mail(
                'Alumni ID Request Approved',
                f'Hello {alumni.firstname} {alumni.lastname},\n\nYour alumni ID request has been approved. Your ID is ready to claim.\n\nThank you!',
                'alumni_ctuac@ctu.edu.ph',
                [email_add],
                fail_silently=False,
            )
            alumni.approved = True  # Mark as approved
            alumni.save()

        except (socket.error, BadHeaderError) as e:
            messages.error(request, f'Error sending email: {e}')
        
        return redirect('studentLife_system:admin_idRequest')

    return redirect('studentLife_system:admin_idRequest')
    
def claim_alumni_id(request, alumni_id):
    if request.method == 'POST':
        alumni = get_object_or_404(Alumni, pk=alumni_id)
        alumni.claimed_date = timezone.now()
        alumni.save()
        return redirect('studentLife_system:admin_idRequest')

    return redirect('studentLife_system:admin_idRequest')

def admin_gradTracer(request):
    graduate_requests = graduateForm.objects.select_related('alumniID').all()
    return render(request, 'alumni/users/admin_gradTracer.html', {'graduate_requests': graduate_requests})

def admin_events(request):
    if request.method == 'POST':
        
        eventsName = request.POST.get('eventsName')
        eventsDate = request.POST.get('eventsDate')
        eventsLocation = request.POST.get('eventsLocation')
        eventsDescription = request.POST.get('eventsDescription')
        eventsImage = request.FILES.get('eventsImage') 

        
        event = Event.objects.create(
            eventsName=eventsName,
            eventsDate=eventsDate,
            eventsLocation=eventsLocation,
            eventsDescription=eventsDescription,
            eventsImage=eventsImage
        )
        messages.success(request, 'Successfully Added!')
        
        return redirect('studentLife_system:admin_events')

    return render(request, 'alumni/users/admin_events.html')




def admin_jobfairs(request):
    if request.method == "POST":
        jobtitle = request.POST.get("jobtitle")
        companyname = request.POST.get("companyname")
        joblocation = request.POST.get("joblocation")
        jobsalary = request.POST.get("jobsalary")
        employmenttype = request.POST.get("employmenttype")
        jobdescription = request.POST.get("jobdescription")
        applicationdeadline = request.POST.get('applicationdeadline')
        posted_date = request.POST.get('posted_date')

        jobfair = JobFair.objects.create(
            jobtitle=jobtitle,
            companyname=companyname,
            joblocation=joblocation,
            jobsalary=jobsalary,
            employmenttype=employmenttype,
            jobdescription=jobdescription,
            posted_date=posted_date,
            applicationdeadline=applicationdeadline
        )

        messages.success(request, "Successfully Added!")
        return redirect("studentLife_system:admin_jobfairs")

    job_fairs = JobFair.objects.order_by('-posted_date')
    return render(request, "alumni/users/admin_jobfairs.html", {"job_fairs": job_fairs})




def admin_yearbook(request):
    if request.method == 'POST':
        yearbookFirstname = request.POST.get('yearfirstname')
        yearbookLastname = request.POST.get('yearlastname')
        yearbookAddress = request.POST.get('yearaddress')
        yearbookCourse = request.POST.get('yearcourse')
        yearbookImage = request.FILES.get('yearImage')  
        yearbookGender = request.POST.get('yeargender')
        yearbookYearGrad = request.POST.get('yeargraduated')

        # Check if an entry with the same first name and last name already exists
        if Yearbook.objects.filter(yearbookFirstname=yearbookFirstname, yearbookLastname=yearbookLastname).exists():
            messages.error(request, 'An entry with this name already exists.')
        else:
            yearbook_entry = Yearbook.objects.create(
                yearbookFirstname=yearbookFirstname,
                yearbookLastname=yearbookLastname,
                yearbookAddress=yearbookAddress,
                yearbookCourse=yearbookCourse,
                yearbookImage=yearbookImage,
                yearbookGender=yearbookGender,
                yearbookYearGrad=yearbookYearGrad
            )
            messages.success(request, 'Successfully Added!')
        
        return redirect('studentLife_system:admin_yearbook')

    return render(request, 'alumni/users/admin_yearbook.html')
def log_in(request):
    return render(request, 'studentorg/Main/Logins.html')
#StudentOrg
#login

def admin_transactionreport(request):
    financial_statements = FinancialStatement.objects.all()
    projects = Project.objects.all()
    accreditations = Accreditation.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    organization = request.GET.get('organization')
    report_type = request.GET.get('report_type')  # New parameter for report type selection

    if start_date:
        financial_statements = financial_statements.filter(date_saved__gte=start_date)
        projects = projects.filter(date_saved__gte=start_date)
        accreditations = accreditations.filter(date_saved__gte=start_date)

    if end_date:
        financial_statements = financial_statements.filter(date_saved__lte=end_date)
        projects = projects.filter(date_saved__lte=end_date)
        accreditations = accreditations.filter(date_saved__lte=end_date)

    if organization:
        financial_statements = financial_statements.filter(org=organization)
        projects = projects.filter(org=organization)
        accreditations = accreditations.filter(organization=organization)

    if report_type == 'projects':
        total_financial_transactions = projects.count()
        total_budget = sum(project.p_budget for project in projects)
        return render(request, 'studentorg/ADMIN/transaction_report.html', {
            'projects': projects,
            'total_financial_transactions': total_financial_transactions,
            'total_budget': total_budget,
            'start_date': start_date,
            'end_date': end_date,
            'organization': organization,
            'report_type': report_type,
        })
    elif report_type == 'financial_statements':
        total_financial_transactions = financial_statements.count()
        total_amount_financial_statements = sum(statement.amount for statement in financial_statements)
        return render(request, 'studentorg/ADMIN/transaction_report.html', {
            'financial_statements': financial_statements,
            'total_financial_transactions': total_financial_transactions,
            'total_amount_financial_statements': total_amount_financial_statements,
            'start_date': start_date,
            'end_date': end_date,
            'organization': organization,
            'report_type': report_type,
        })
    elif report_type == 'accreditations':
        total_financial_transactions = accreditations.count()
        return render(request, 'studentorg/ADMIN/transaction_report.html', {
            'accreditations': accreditations,
            'total_financial_transactions': total_financial_transactions,
            'start_date': start_date,
            'end_date': end_date,
            'organization': organization,
            'report_type': report_type,
        })
    else:
        total_financial_transactions = financial_statements.count() + projects.count() + accreditations.count()
        total_projects = projects.count()
        total_accreditations = accreditations.count()
        total_budget = sum(project.p_budget for project in projects)
        total_amount_financial_statements = sum(statement.amount for statement in financial_statements)
        return render(request, 'studentorg/ADMIN/transaction_report.html', {
            'financial_statements': financial_statements,
            'projects': projects,
            'accreditations': accreditations,
            'total_financial_transactions': total_financial_transactions,
            'total_projects': total_projects,
            'total_accreditations': total_accreditations,
            'total_budget': total_budget,
            'total_amount_financial_statements': total_amount_financial_statements,
            'start_date': start_date,
            'end_date': end_date,
            'organization': organization,
            'report_type': report_type,
        })
    
#oRG
def logins(request):
    return render (request, "studentorg/Main/Logins.html")

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['admin_username']
            password = form.cleaned_data['admin_password']
            try:
                admin = AdminLogin.objects.get(admin_username=username, admin_password=password)
                return redirect('studentLife_system:admin_manageofficer')
            except AdminLogin.DoesNotExist:
                messages.error(request, "Invalid username or password")
    else:
        form = AdminLoginForm()
    return render(request, 'studentorg/ADMIN/admin_login.html', {'form': form})

def register_officer(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        organization = request.POST['organization']
        username = request.POST['username']
        password = request.POST['password']

        try:
            officer = Officer.objects.get(student_id=student_id)
        except Officer.DoesNotExist:
            messages.error(request, 'Officer with the provided student ID does not exist.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        if officer.organization != organization:
            messages.error(request, 'The provided organization does not match the officer\'s organization.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        if officer.status != 'approved':
            messages.error(request, 'Officer status must be approved to create an account.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        if OfficerLogin.objects.filter(student_id=student_id).exists():
            messages.error(request, 'An officer with this student ID already exists.')
            return render(request, 'studentorg/ADMIN/registerofficer.html')

        officer_login = OfficerLogin(
            student_id=officer,
            username=username,
            password=password,
            organization=organization,
        )
        officer_login.save()
        messages.success(request, 'You have successfully created an officer account.')
        return redirect('studentLife_system:officer_login')

    return render(request, 'studentorg/ADMIN/registerofficer.html')


def officer_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
           
            try:
                officer = OfficerLogin.objects.get(username=username, password=password)
                
                # Store officer details in session
                request.session['officer_student_id'] = officer.student_id.student_id  # Correct reference to student_id
                request.session['organization'] = officer.organization
                
                # Success message
                messages.success(request, 'You have successfully logged in.')
                
                # Redirect based on organization
                if officer.organization == 'FSTLP':
                    return redirect('studentLife_system:FSTLP_profile')
                elif officer.organization == 'SI++':
                    return redirect('studentLife_system:SI_profile')
                elif officer.organization == 'THE EQUATIONERS':
                    return redirect('studentLife_system:THEEQUATIONERS_profile')
                elif officer.organization == 'SSG':
                    return redirect('studentLife_system:SSG_profile')
                elif officer.organization == 'TECHNOCRATS':
                    return redirect('studentLife_system:TECHNOCRATS_profile')
                else:
                    messages.error(request, 'Invalid organization.')
                    return redirect('studentLife_system:officer_login')  # Fallback redirect to login if organization is invalid
            except OfficerLogin.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'studentorg/ADMIN/officer_login.html', {'form': form})
# admin
def admin_manageofficer(request):
    officers = Officer.objects.all()
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        officer = get_object_or_404(Officer, student_id=student_id)
        if action == 'approve':
            officer.status = 'approved'
        elif action == 'decline':
            officer.status = 'declined'
        elif action == 'terminate':
            officer.status = 'terminated'
        officer.save()
        return redirect('studentLife_system:admin_manageofficer')
    return render(request, 'studentorg/ADMIN/admin_manageofficer.html', {'officers': reversed(officers)})


def admin_manageadviser(request):
    advisers = Adviser.objects.all()
    if request.method == 'POST':
        adviser_id = request.POST.get('adviser_id')
        action = request.POST.get('action')
        adviser = get_object_or_404(Adviser, id=adviser_id)
        if action == 'approve':
            adviser.status = 'approved'
        elif action == 'decline':
            adviser.status = 'declined'
        elif action == 'terminate':
            adviser.status = 'terminated'
        adviser.save()
        return redirect('studentLife_system:admin_manageadviser')
    return render(request, 'studentorg/ADMIN/admin_manageadviser.html', {'advisers': reversed(advisers)})



def admin_manageproject(request):
    projects = Project.objects.all()
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        action = request.POST.get('action')
        project = get_object_or_404(Project, project_id=project_id)
        if action == 'approve':
            project.status = 'approved'
        elif action == 'decline':
            project.status = 'declined'
        project.save()
        return redirect('studentLife_system:admin_manageproject')
    return render(request, 'studentorg/ADMIN/admin_manageproject.html', {'projects': reversed(projects)})

def admin_managefinancial(request):
    statements = FinancialStatement.objects.all()
    if request.method == 'POST':
        financial_id = request.POST.get('financial_id')  
        action = request.POST.get('action')
        statement = get_object_or_404(FinancialStatement, financial_id=financial_id)  # Corrected variable name
        if action == 'approve':
            statement.status = 'approved'
        elif action == 'decline':
            statement.status = 'declined'
        statement.save()
        return redirect('studentLife_system:admin_managefinancial')
    return render(request, 'studentorg/ADMIN/admin_managefinancial.html', {'statements': reversed(statements)})

def admin_manage_accreditations(request):
    accreditations = Accreditation.objects.all() 
    if request.method == 'POST':
        accreditation_id = request.POST.get('accreditation_id')
        action = request.POST.get('action')
        accreditation = get_object_or_404(Accreditation, accreditation_id=accreditation_id)
        
        if action == 'approve':
            accreditation.status = 'approved'
            accreditation.save()
            
         
            organization = accreditation.organization
            if organization == 'FSTLP':
                return redirect('studentLife_system:FSTLP_certification')
            elif organization == 'SI':
                return redirect('studentLife_system:SI_certification')
            elif organization == 'THEEQUATIONERS':
                return redirect('studentLife_system:THEEQUATIONERS_certification')
            elif organization == 'SSG':
                return redirect('studentLife_system:SSG_certification')
            elif organization == 'TECHNOCRATS':
                return redirect('studentLife_system:TECHNOCRATS_certification')
            else:
             
                return redirect('studentLife_system:admin_manage_accreditations')  # Default redirect if no match
        elif action == 'decline':
            accreditation.status = 'declined'
            accreditation.save()
            return redirect('studentLife_system:admin_manage_accreditations')
    
    return render(request, 'studentorg/ADMIN/manage_accreditation.html', {'accreditations': reversed(accreditations)})

def FSTLP_certification(request):
    return render(request, 'studentorg/FSTLP/FSTLP_certification.html')

def SI_certification(request):
    return render(request, 'studentorg/SI++/SI++_certification.html')

def SSG_certification(request):
    return render(request, 'studentorg/SSG/SSG_certification.html')

def THEEQUATIONERS_certification(request):
    return render(request, 'studentorg/THEEQUATIONER/THEEQUATIONER_certification.html')

def TECHNOCRATS_certification(request):
    return render(request, 'studentorg/TECHNOCRATS/TECHNOCRATS_certification.html')




def admin_view_accreditations(request):
    approved_accreditations= Accreditation.objects.all()
    return render(request, 'studentorg/ADMIN/view_accreditation.html', {'accreditations': approved_accreditations})

#FSLTP
def FSTLP_profile(request):
    return render (request, "studentorg/FSTLP/FSTLP_profile.html")
def FSTLP_CBL(request):
    return render (request, "studentorg/FSTLP/FSTLP_CBL.html")

def FSTLP_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect('studentLife_system:FSTLP_accreditation')
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {'form': form}

    if request.method == 'POST':
        context['uploaded_files'] = {
            'letter_of_intent': request.FILES.get('letter_of_intent'),
            'list_of_officers': request.FILES.get('list_of_officers'),
            'certificate_of_registration': request.FILES.get('certificate_of_registration'),
            'list_of_members': request.FILES.get('list_of_members'),
            'accomplishment_report': request.FILES.get('accomplishment_report'),
            'calendar_of_activities': request.FILES.get('calendar_of_activities'),
            'financial_statement': request.FILES.get('financial_statement'),
            'bank_passbook': request.FILES.get('bank_passbook'),
            'inventory_of_properties': request.FILES.get('inventory_of_properties'),
            'organization_bylaws': request.FILES.get('organization_bylaws'),
            'faculty_adviser_appointment': request.FILES.get('faculty_adviser_appointment'),
            'other_documents': request.FILES.get('other_documents'),
        }

    return render (request, "studentorg/FSTLP/FSTLP_accreditation.html", context)



#FSLTP ADD
def FSTLP_projects(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:FSTLP_projects')
    else:
        form = ProjectForm()
    return render(request, "studentorg/FSTLP/FSTLP_projects.html", {'form': form})


def FSTLP_financial(request):
    if request.method == 'POST':
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:FSTLP_financial')
    else:
        form = FinancialStatementForm()
    return render(request, "studentorg/FSTLP/FSTLP_financial_statement.html", {'form': form})

def FSTLP_officerdata(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:FSTLP_officerdata') 
    else:
        form = OfficerForm()
    return render(request, 'studentorg/FSTLP/FSTLP_officerdata.html', {'form': form})

def FSTLP_adviserdata(request):
    if request.method == 'POST':
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('studentLife_system:FSTLP_adviserdata')
    else:
        form = AdviserForm()
    return render(request,'studentorg/FSTLP/FSTLP_adviserdata.html',{'form': form})
# FSLTP VIEW
def FSTLP_viewproject(request):
    approved_projects = Project.objects.filter(org="FSTLP")
    return render(
        request,
        "studentorg/FSTLP/FSTLP_viewproject.html",
        {"projects": approved_projects},
    )


def FSTLP_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(org="FSTLP")
    return render(
        request,
        "studentorg/FSTLP/FSTLP_viewfinancial.html",
        {"statements": approved_projects},
    )


def FSTLP_viewofficer(request):
    approved_projects = Officer.objects.filter(organization="FSTLP")
    return render(
        request,
        "studentorg/FSTLP/FSTLP_viewofficer.html",
        {"statements": approved_projects},
    )


def FSTLP_viewadviser(request):
    approved_projects = Adviser.objects.filter(organization="FSTLP")
    return render(
        request,
        "studentorg/FSTLP/FSTLP_viewadviser.html",
        {"advisers": approved_projects},
    )


# SI++
def SI_profile(request):
    return render(request, "studentorg/SI++/SI++_profile.html")


def SI_accreditation(request):
    if request.method == "POST":
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect("studentLife_system:SI_accreditation")
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {"form": form}

    if request.method == "POST":
        context["uploaded_files"] = {
            "letter_of_intent": request.FILES.get("letter_of_intent"),
            "list_of_officers": request.FILES.get("list_of_officers"),
            "certificate_of_registration": request.FILES.get(
                "certificate_of_registration"
            ),
            "list_of_members": request.FILES.get("list_of_members"),
            "accomplishment_report": request.FILES.get("accomplishment_report"),
            "calendar_of_activities": request.FILES.get("calendar_of_activities"),
            "financial_statement": request.FILES.get("financial_statement"),
            "bank_passbook": request.FILES.get("bank_passbook"),
            "inventory_of_properties": request.FILES.get("inventory_of_properties"),
            "organization_bylaws": request.FILES.get("organization_bylaws"),
            "faculty_adviser_appointment": request.FILES.get(
                "faculty_adviser_appointment"
            ),
            "other_documents": request.FILES.get("other_documents"),
        }
    return render(request, "studentorg/SI++/SI++_accreditation.html", context)


def SI_CBL(request):
    return render(request, "studentorg/SI++/SI++_CBL.html")


# SI++ ADD


def SI_projects(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SI_projects")
    else:
        form = ProjectForm()
    return render(request, "studentorg/SI++/SI++_projects.html", {"form": form})


def SI_financial(request):
    if request.method == "POST":
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SI_financial")
    else:
        form = FinancialStatementForm()
    return render(
        request, "studentorg/SI++/SI++_financial_statement.html", {"form": form}
    )


def SI_officerdata(request):
    if request.method == "POST":
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SI_officerdata")
    else:
        form = OfficerForm()
    return render(request, "studentorg/SI++/SI++_officerdata.html", {"form": form})


def SI_adviserdata(request):
    if request.method == "POST":
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SI_adviserdata")
    else:
        form = AdviserForm()
    return render(request, "studentorg/SI++/SI++_adviserdata.html", {"form": form})


# SI++ VIEW
def SI_viewproject(request):
    approved_projects = Project.objects.filter(org="SI++")
    return render(
        request,
        "studentorg/SI++/SI++_viewproject.html",
        {"projects": approved_projects},
    )


def SI_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(org="SI++")
    return render(
        request,
        "studentorg/SI++/SI++_viewfinancial.html",
        {"statements": approved_projects},
    )


def SI_viewofficer(request):
    approved_projects = Officer.objects.filter(organization="SI++")
    return render(
        request,
        "studentorg/SI++/SI++_viewofficer.html",
        {"statements": approved_projects},
    )


def SI_viewadviser(request):
    approved_projects = Adviser.objects.filter(organization="SI++")
    return render(
        request,
        "studentorg/SI++/SI++_viewadviser.html",
        {"advisers": approved_projects},
    )


# THE EQUATIONERS
def THEEQUATIONERS_profile(request):
    return render(request, "studentorg/THEEQUATIONER/THEEQUATIONER_profile.html")


def THEEQUATIONERS_accreditation(request):
    if request.method == "POST":
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect("studentLife_system:THEEQUATIONERS_accreditation")
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {"form": form}

    if request.method == "POST":
        context["uploaded_files"] = {
            "letter_of_intent": request.FILES.get("letter_of_intent"),
            "list_of_officers": request.FILES.get("list_of_officers"),
            "certificate_of_registration": request.FILES.get(
                "certificate_of_registration"
            ),
            "list_of_members": request.FILES.get("list_of_members"),
            "accomplishment_report": request.FILES.get("accomplishment_report"),
            "calendar_of_activities": request.FILES.get("calendar_of_activities"),
            "financial_statement": request.FILES.get("financial_statement"),
            "bank_passbook": request.FILES.get("bank_passbook"),
            "inventory_of_properties": request.FILES.get("inventory_of_properties"),
            "organization_bylaws": request.FILES.get("organization_bylaws"),
            "faculty_adviser_appointment": request.FILES.get(
                "faculty_adviser_appointment"
            ),
            "other_documents": request.FILES.get("other_documents"),
        }
    return render(
        request, "studentorg/THEEQUATIONER/THEEQUATIONER_accreditation.html", context
    )


def THEEQUATIONERS_CBL(request):
    return render(request, "studentorg/THEEQUATIONER/THEEQUATIONER_CBL.html")


# THE EQUATIONERS ADD
def THEEQUATIONERS_projects(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:THEEQUATIONERS_projects")
    else:
        form = ProjectForm()
    return render(
        request, "studentorg/THEEQUATIONER/THEEQUATIONER_projects.html", {"form": form}
    )


def THEEQUATIONERS_financial(request):
    if request.method == "POST":
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:THEEQUATIONERS_financial")
    else:
        form = FinancialStatementForm()
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_financial_statement.html",
        {"form": form},
    )


def THEEQUATIONERS_officerdata(request):
    if request.method == "POST":
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:THEEQUATIONERS_officerdata")
    else:
        form = OfficerForm()
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_officerdata.html",
        {"form": form},
    )


def THEEQUATIONERS_adviserdata(request):
    if request.method == "POST":
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:THEEQUATIONERS_adviserdata")
    else:
        form = AdviserForm()
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_adviserdata.html",
        {"form": form},
    )


# THE EQUATIONERS VIEW
def THEEQUATIONERS_viewproject(request):
    approved_projects = Project.objects.filter(org="THE EQUATIONERS")
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_viewproject.html",
        {"projects": approved_projects},
    )


def THEEQUATIONERS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(org="THE EQUATIONERS")
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_viewfinancial.html",
        {"statements": approved_projects},
    )


def THEEQUATIONERS_viewofficer(request):
    approved_projects = Officer.objects.filter(organization="THE EQUATIONERS")
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_viewofficer.html",
        {"statements": approved_projects},
    )


def THEEQUATIONERS_viewadviser(request):
    approved_projects = Adviser.objects.filter(organization="THE EQUATIONERS")
    return render(
        request,
        "studentorg/THEEQUATIONER/THEEQUATIONER_viewadviser.html",
        {"advisers": approved_projects},
    )


# SUPREME STUDENT GOV (SSG)
def SSG_profile(request):
    return render(request, "studentorg/SSG/SSG_profile.html")


def SSG_accreditation(request):
    if request.method == "POST":
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect("studentLife_system:SSG_accreditation")
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {"form": form}

    if request.method == "POST":
        context["uploaded_files"] = {
            "letter_of_intent": request.FILES.get("letter_of_intent"),
            "list_of_officers": request.FILES.get("list_of_officers"),
            "certificate_of_registration": request.FILES.get(
                "certificate_of_registration"
            ),
            "list_of_members": request.FILES.get("list_of_members"),
            "accomplishment_report": request.FILES.get("accomplishment_report"),
            "calendar_of_activities": request.FILES.get("calendar_of_activities"),
            "financial_statement": request.FILES.get("financial_statement"),
            "bank_passbook": request.FILES.get("bank_passbook"),
            "inventory_of_properties": request.FILES.get("inventory_of_properties"),
            "organization_bylaws": request.FILES.get("organization_bylaws"),
            "faculty_adviser_appointment": request.FILES.get(
                "faculty_adviser_appointment"
            ),
            "other_documents": request.FILES.get("other_documents"),
        }
    return render(request, "studentorg/SSG/SSG_accreditation.html", context)


def SSG_CBL(request):
    return render(request, "studentorg/SSG/SSG_CBL.html")


# SSG ADD
def SSG_projects(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SSG_projects")
    else:
        form = ProjectForm()
    return render(request, "studentorg/SSG/SSG_projects.html", {"form": form})


def SSG_financial(request):
    if request.method == "POST":
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SSG_financial")
    else:
        form = FinancialStatementForm()
    return render(
        request, "studentorg/SSG/SSG_financial_statement.html", {"form": form}
    )


def SSG_officerdata(request):
    if request.method == "POST":
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SSG_officerdata")
    else:
        form = OfficerForm()
    return render(request, "studentorg/SSG/SSG_officerdata.html", {"form": form})


def SSG_adviserdata(request):
    if request.method == "POST":
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:SSG_adviserdata")
    else:
        form = AdviserForm()
    return render(request, "studentorg/SSG/SSG_adviserdata.html", {"form": form})


# SSG VIEW
def SSG_viewproject(request):
    approved_projects = Project.objects.filter(org="SSG")
    return render(
        request, "studentorg/SSG/SSG_viewproject.html", {"projects": approved_projects}
    )


def SSG_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(org="SSG")
    return render(
        request,
        "studentorg/SSG/SSG_viewfinancial.html",
        {"statements": approved_projects},
    )


def SSG_viewofficer(request):
    approved_projects = Officer.objects.filter(organization="SSG")
    return render(
        request,
        "studentorg/SSG/SSG_viewofficer.html",
        {"statements": approved_projects},
    )


def SSG_viewadviser(request):
    approved_projects = Adviser.objects.filter(organization="SSG")
    return render(
        request, "studentorg/SSG/SSG_viewadviser.html", {"advisers": approved_projects}
    )


# TECHNOCRATS
def TECHNOCRATS_profile(request):
    return render(request, "studentorg/TECHNOCRATS/TECHNOCRATS_profile.html")


def TECHNOCRATS_accreditation(request):
    if request.method == "POST":
        form = AccreditationForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation = form.save()
            return redirect("studentLife_system:TECHNOCRATS_accreditation")
        else:
            print(form.errors)
    else:
        form = AccreditationForm()

    context = {"form": form}

    if request.method == "POST":
        context["uploaded_files"] = {
            "letter_of_intent": request.FILES.get("letter_of_intent"),
            "list_of_officers": request.FILES.get("list_of_officers"),
            "certificate_of_registration": request.FILES.get(
                "certificate_of_registration"
            ),
            "list_of_members": request.FILES.get("list_of_members"),
            "accomplishment_report": request.FILES.get("accomplishment_report"),
            "calendar_of_activities": request.FILES.get("calendar_of_activities"),
            "financial_statement": request.FILES.get("financial_statement"),
            "bank_passbook": request.FILES.get("bank_passbook"),
            "inventory_of_properties": request.FILES.get("inventory_of_properties"),
            "organization_bylaws": request.FILES.get("organization_bylaws"),
            "faculty_adviser_appointment": request.FILES.get(
                "faculty_adviser_appointment"
            ),
            "other_documents": request.FILES.get("other_documents"),
        }
    return render(
        request, "studentorg/TECHNOCRATS/TECHNOCRATS_accreditation.html", context
    )


def TECHNOCRATS_CBL(request):
    return render(request, "studentorg/TECHNOCRATS/TECHNOCRATS_CBL.html")


# TECNOCRATS ADD
def TECHNOCRATS_projects(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:TECHNOCRATS_projects")
    else:
        form = ProjectForm()
    return render(
        request, "studentorg/TECHNOCRATS/TECHNOCRATS_projects.html", {"form": form}
    )


def TECHNOCRATS_financial(request):
    if request.method == "POST":
        form = FinancialStatementForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = FinancialStatementForm()
    return render(
        request,
        "studentorg/TECHNOCRATS/TECHNOCRATS_financial_statement.html",
        {"form": form},
    )


def TECHNOCRATS_officerdata(request):
    if request.method == "POST":
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:TECHNOCRATS_officerdata")
    else:
        form = OfficerForm()
    return render(
        request, "studentorg/TECHNOCRATS/TECHNOCRATS_officerdata.html", {"form": form}
    )


def TECHNOCRATS_adviserdata(request):
    if request.method == "POST":
        form = AdviserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("studentLife_system:TECHNOCRATS_adviserdata")
    else:
        form = AdviserForm()
    return render(
        request, "studentorg/TECHNOCRATS/TECHNOCRATS_adviserdata.html", {"form": form}
    )


# TECNOCRATS VIEW
def TECHNOCRATS_viewproject(request):
    approved_projects = Project.objects.filter(org="TECHNOCRATS")
    return render(
        request,
        "studentorg/TECHNOCRATS/TECHNOCRATS_viewproject.html",
        {"projects": approved_projects},
    )


def TECHNOCRATS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(org="TECHNOCRATS")
    return render(
        request,
        "studentorg/TECHNOCRATS/TECHNOCRATS_viewfinancial.html",
        {"statements": approved_projects},
    )


def TECHNOCRATS_viewofficer(request):
    approved_projects = Officer.objects.filter(organization="TECHNOCRATS")
    return render(
        request,
        "studentorg/TECHNOCRATS/TECHNOCRATS_viewofficer.html",
        {"statements": approved_projects},
    )


def TECHNOCRATS_viewadviser(request):
    approved_projects = Adviser.objects.filter(organization="TECHNOCRATS")
    return render(
        request,
        "studentorg/TECHNOCRATS/TECHNOCRATS_viewadviser.html",
        {"advisers": approved_projects},
    )


# General View


def Gen_Home(request):
    return render(request, "studentorg/VIEW/OrgMain.html")


def Gen_FSTLP_profile(request):
    return render(request, "studentorg/VIEW/FSTLP_profile.html")


def Gen_SI_profile(request):
    return render(request, "studentorg/VIEW/SI++_profile.html")


def Gen_SSG_profile(request):
    return render(request, "studentorg/VIEW/SSG_profile.html")


def Gen_TECHNOCRATS_profile(request):
    return render(request, "studentorg/VIEW/TECHNOCRATS_profile.html")


def Gen_THEEQUATIONERS_profile(request):
    return render(request, "studentorg/VIEW/THEEQUATIONER_profile.html")


def Gen_FSTLP_viewproject(request):
    approved_projects = Project.objects.filter(status="approved", org="FSTLP")
    return render(
        request,
        "studentorg/VIEW/FSTLP_viewproject.html",
        {"projects": approved_projects},
    )


def Gen_FSTLP_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(
        status="approved", org="FSTLP"
    )
    return render(
        request,
        "studentorg/VIEW/FSTLP_viewfinancial.html",
        {"statements": approved_projects},
    )


def Gen_FSTLP_viewofficer(request):
    approved_projects = Officer.objects.filter(status="approved", organization="FSTLP")
    return render(
        request,
        "studentorg/VIEW/FSTLP_viewofficer.html",
        {"statements": approved_projects},
    )


def Gen_FSTLP_viewadviser(request):
    approved_projects = Adviser.objects.filter(status="approved", organization="FSTLP")
    return render(
        request,
        "studentorg/VIEW/FSTLP_viewadviser.html",
        {"advisers": approved_projects},
    )


def Gen_SI_viewproject(request):
    approved_projects = Project.objects.filter(status="approved", org="SI++")
    return render(
        request,
        "studentorg/VIEW/SI++_viewproject.html",
        {"projects": approved_projects},
    )


def Gen_SI_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status="approved", org="SI++")
    return render(
        request,
        "studentorg/VIEW/SI++_viewfinancial.html",
        {"statements": approved_projects},
    )


def Gen_SI_viewofficer(request):
    approved_projects = Officer.objects.filter(status="approved", organization="SI++")
    return render(
        request,
        "studentorg/VIEW/SI++_viewofficer.html",
        {"statements": approved_projects},
    )


def Gen_SI_viewadviser(request):
    approved_projects = Adviser.objects.filter(status="approved", organization="SI++")
    return render(
        request,
        "studentorg/VIEW/SI++_viewadviser.html",
        {"advisers": approved_projects},
    )


def Gen_THEEQUATIONERS_viewproject(request):
    approved_projects = Project.objects.filter(status="approved", org="THE EQUATIONERS")
    return render(
        request,
        "studentorg/VIEW/THEEQUATIONER_viewproject.html",
        {"projects": approved_projects},
    )


def Gen_THEEQUATIONERS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(
        status="approved", org="THE EQUATIONERS"
    )
    return render(
        request,
        "studentorg/VIEW/THEEQUATIONER_viewfinancial.html",
        {"statements": approved_projects},
    )


def Gen_THEEQUATIONERS_viewofficer(request):
    approved_projects = Officer.objects.filter(
        status="approved", organization="THE EQUATIONERS"
    )
    return render(
        request,
        "studentorg/VIEW/THEEQUATIONER_viewofficer.html",
        {"statements": approved_projects},
    )


def Gen_THEEQUATIONERS_viewadviser(request):
    approved_projects = Adviser.objects.filter(
        status="approved", organization="THE EQUATIONERS"
    )
    return render(
        request,
        "studentorg/VIEW/THEEQUATIONER_viewadviser.html",
        {"advisers": approved_projects},
    )


def Gen_SSG_viewproject(request):
    approved_projects = Project.objects.filter(status="approved", org="SSG")
    return render(
        request, "studentorg/VIEW/SSG_viewproject.html", {"projects": approved_projects}
    )


def Gen_SSG_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(status="approved", org="SSG")
    return render(
        request,
        "studentorg/VIEW/SSG_viewfinancial.html",
        {"statements": approved_projects},
    )


def Gen_SSG_viewofficer(request):
    approved_projects = Officer.objects.filter(status="approved", organization="SSG")
    return render(
        request,
        "studentorg/VIEW/SSG_viewofficer.html",
        {"statements": approved_projects},
    )


def Gen_SSG_viewadviser(request):
    approved_projects = Adviser.objects.filter(status="approved", organization="SSG")
    return render(
        request, "studentorg/VIEW/SSG_viewadviser.html", {"advisers": approved_projects}
    )


def Gen_TECHNOCRATS_viewproject(request):
    approved_projects = Project.objects.filter(status="approved", org="TECHNOCRATS")
    return render(
        request,
        "studentorg/VIEW/TECHNOCRATS_viewproject.html",
        {"projects": approved_projects},
    )


def Gen_TECHNOCRATS_viewfinancial(request):
    approved_projects = FinancialStatement.objects.filter(
        status="approved", org="TECHNOCRATS"
    )
    return render(
        request,
        "studentorg/VIEW/TECHNOCRATS_viewfinancial.html",
        {"statements": approved_projects},
    )


def Gen_TECHNOCRATS_viewofficer(request):
    approved_projects = Officer.objects.filter(
        status="approved", organization="TECHNOCRATS"
    )
    return render(
        request,
        "studentorg/VIEW/TECHNOCRATS_viewofficer.html",
        {"statements": approved_projects},
    )


def Gen_TECHNOCRATS_viewadviser(request):
    approved_projects = Adviser.objects.filter(
        status="approved", organization="TECHNOCRATS"
    )
    return render(
        request,
        "studentorg/VIEW/TECHNOCRATS_viewadviser.html",
        {"advisers": approved_projects},
    )


def calculate_age(birth_date):
    today = datetime.today()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    return age


@login_required
def individualProfile(request):
    user = request.user
    if user.user_type == "sao admin":
        return render(
            request,
            "guidance/admin/access_violation.html",
            {"info": "For student use only."},
        )
    if request.method == "POST":
        form = IndividualProfileForm(request.POST, request.FILES)
        if form.is_valid():
            siblings_name = request.POST.getlist("name[]")
            siblings_age = request.POST.getlist("age[]")
            siblings_placework = request.POST.getlist("placework[]")

            name_of_organization = request.POST.getlist("name_of_organization[]")

            inout_school = []
            intout_school1 = request.POST.get("inoutSchool_0[]")
            intout_school2 = request.POST.get("inoutSchool_1[]")
            inout_school.append(intout_school1)
            inout_school.append(intout_school2)

            position = request.POST.getlist("position[]")
            inclusive_years = request.POST.getlist("inclusiveyears[]")

            current_datetime = timezone.now()

            # Daghan kaau kuhaon na fields kay yawa ka daghan na checkbox
            describeYouBest_values = [
                "Friendly",
                "Self-Confident",
                "Calm",
                "Quick-Tempered",
                "Feels Inferior",
                "Unhappy",
                "Easily Bored",
                "Talented",
                "Withdrawn",
                "Conscientious",
                "Talkative",
                "Cheerful",
                "Moody",
                "Easily Exhausted",
                "Lazy",
                "Sensitive",
                "Poor health",
                "Reserved",
                "Quiet",
                "Independent",
                "Depressed",
                "Suspicious",
                "Irritable",
                "Stubborn",
                "Thoughtful",
                "Lovable",
                "Jealous",
                "Shy",
                "Sarcastic",
                "Tactful",
                "Pessimistic",
                "Submissive",
                "Optimistic",
                "Happy-go-lucky",
                "Goal-oriented",
            ]
            # This shit so slow but it works

            describeYouBest_checked = request.POST.getlist("describeYouBest[]")

            student_id = request.POST.get("student_id_val")

            date_of_birth_str = form.cleaned_data["dateOfBirth"]
            date_of_birth = datetime.strptime(str(date_of_birth_str), "%Y-%m-%d")
            age = calculate_age(date_of_birth)

            # Get the studentInfo instance corresponding to the provided student ID
            student = get_object_or_404(studentInfo, studID=student_id)

            # Create a dictionary to store the state (checked or not) of each value
            describeYouBest_state = {
                value: value in describeYouBest_checked
                for value in describeYouBest_values
            }

            new_form = form.save(commit=False)
            new_form.age = age
            new_form.studentId = student
            new_form.dateFilled = current_datetime
            new_form.siblingsName = siblings_name
            new_form.siblingsAge = siblings_age
            new_form.siblingsSchoolWork = siblings_placework

            # Assuming the other fields are also JSONFields
            new_form.nameOfOrganization = name_of_organization
            new_form.inOutSchool = inout_school
            new_form.positionTitle = position
            new_form.inclusiveYears = inclusive_years
            new_form.describeYouBest = describeYouBest_state

            # Handle the studentPhoto field
            if "studentPhoto" in request.FILES:
                new_form.studentPhoto = request.FILES["studentPhoto"]
            transaction = GuidanceTransaction(
                transactionType=f"{student.lastname} {student.firstname} fillup Individual Profile.",
                transactionOrigin="individualprofile",
                transactionDate=timezone.now(),
            )
            transaction.save()
            new_form.save()
            messages.success(request, "Your information has been submitted.")
            return redirect("studentLife_system:Individual Profile")
    else:
        form = IndividualProfileForm()

    user = request.user

    student_info = None
    # Check if the user has a related studentInfo object
    if user.student_id:
        student_info = user.student_id
    context = {"form": form, "student_id": student_info.studID}
    return render(request, "guidance/user/individual_profile.html", context)


def intake_interview_view(request):
    user = request.user
    if not user.user_type == "sao admin":
        return render(
            request,
            "guidance/user/access_violation.html",
            {"info": "For admin user only!"},
        )
    # Mas daghan panig bug kaysa wuthering waves

    if request.method == "POST":
        individualId = request.POST.get("individualId")

        individualActivity = request.POST.getlist("individualActivity[]")
        individualDateAccomplished = request.POST.getlist("individualAccomplished[]")
        individualRemarks = request.POST.getlist("individualRemarks[]")

        apprailsalTest = request.POST.getlist("appraisalTest[]")
        apprailsalDateTaken = request.POST.getlist("appraisalDateTaken[]")
        apprailsalDateInterpreted = request.POST.getlist("appraisalDateInterpreted[]")
        apprailsalRemarks = request.POST.getlist("appraisalRemarks[]")

        counseling_types = request.POST.getlist("couseling_type[]")
        selected_types = []

        for x in range(1, 10):
            counseling_types = request.POST.get(f"couseling_type{x}[]")
            selected_types.append(counseling_types)

        counselingDate = request.POST.getlist("counselingDate[]")
        counselingConcern = request.POST.getlist("counselingConcern[]")
        counselingRemarks = request.POST.getlist("counselingRemarks[]")

        followActivity = request.POST.getlist("followActivity[]")
        followDate = request.POST.getlist("followDate[]")
        followRemarks = request.POST.getlist("followRemarks[]")

        informationActivity = request.POST.getlist("informationActivity[]")
        informationDate = request.POST.getlist("informationDate[]")
        informationRemarks = request.POST.getlist("informationRemarks[]")

        counsultationActivity = request.POST.getlist("counseltationActivity[]")
        counsultationDate = request.POST.getlist("counseltationDate[]")
        counsultationRemarks = request.POST.getlist("counseltationRemarks[]")

        individual = get_object_or_404(
            IndividualProfileBasicInfo, individualProfileID=individualId
        )

        # Issue: Di mag sunod2 sa database

        # 'If ignoring this issue is a sin then I am a sinner - Bryan Antier 2024'

        obj = IntakeInverView(
            individualProfileId=individual,
            individualActivity=individualActivity,
            individualDateAccomplished=individualDateAccomplished,
            individualRemarks=individualRemarks,
            appraisalTest=apprailsalTest,
            appraisalDateTaken=apprailsalDateTaken,
            appraisalDateInterpreted=apprailsalDateInterpreted,
            appraisalRemarks=apprailsalRemarks,
            counselingType=selected_types,
            counselingDate=counselingDate,
            counselingConcern=counselingConcern,
            counselingRemarks=counselingRemarks,
            followActivity=followActivity,
            followDate=followDate,
            followRemarks=followRemarks,
            informationActivity=informationActivity,
            informationDate=informationDate,
            informationRemarks=informationRemarks,
            counsultationActivity=counsultationActivity,
            counsultationDate=counsultationDate,
            counsultationRemarks=counsultationRemarks,
        )
        obj.save()

        transaction = GuidanceTransaction(
            transactionType=f"Counselor fill out the intake interview for {individual.studentId.studID}",
            transactionOrigin="intake",
            transactionDate=timezone.now(),
        )
        transaction.save()

        new_intake_id = obj.intakeId

        return redirect("studentLife_system:individual_profile_sheet", id=new_intake_id)

    return render(request, "guidance/admin/intake_interview.html", {})


def individual_profile_sheet(request, id):
    intake = IntakeInverView.objects.get(intakeId=id)
    return render(
        request, "guidance/admin/individual_profile_sheet.html", {"form": intake}
    )


def search_student_info_for_intake(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number", "")
        try:
            student = studentInfo.objects.get(studID=id_number)
            individual = IndividualProfileBasicInfo.objects.filter(
                studentId=student
            ).order_by("-dateFilled")
            items = []
            for val in individual:
                response = {
                    "profile_number": val.individualProfileID,
                    "studentid": val.studentId.studID,
                    "name": f"{val.studentId.lastname}, {val.studentId.middlename}, {val.studentId.firstname}",
                    "datefilled": val.dateFilled.strftime("%B %d, %Y"),
                }
                items.append(response)

            return JsonResponse({"response": items})
        except studentInfo.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)


@register.filter
def extract_initials(text):
    words = text.split()
    result = ""
    for word in words:
        if word[0].isupper():
            result += word[0]
    return result


@register.filter
def toTitle(text):
    return f"{text}".title()


@login_required
def counseling_app(request):
    user = request.user
    if user.user_type == "sao admin":
        return redirect("studentLife_system:Counseling App With Scheduler Admin View")
    if request.method == "POST":
        form = CounselingSchedulerForm(request.POST)
        if form.is_valid():
            current_datetime = timezone.now()
            student_id = request.POST.get("student_id_val")

            # Get the studentInfo instance corresponding to the provided student ID
            student = get_object_or_404(studentInfo, studID=student_id)

            # Check for ongoing schedules
            ongoing_schedule = counseling_schedule.objects.filter(
                studentID=student, scheduled_date__gte=current_datetime.date()
            ).first()

            if (
                ongoing_schedule
                and not ongoing_schedule.status == "Declined"
                and not ongoing_schedule.status == "Expired"
            ):
                time = {
                    "8-9": "8:00 AM - 9:00 AM",
                    "9-10": "9:00 AM - 10:00 AM",
                    "10-11": "10:00 AM-11:00 AM",
                    "11-12": "11:00 AM -12:00 PM",
                    "1-2": "1:00 PM - 2:00 PM",
                    "2-3": "2:00 PM - 3:00 PM",
                    "3-4": "3:00 PM - 4:00 PM",
                    "4-5": "4:00 PM - 5:00 PM",
                }

                scheduled_date = ongoing_schedule.scheduled_date.strftime("%B %d, %Y")
                scheduled_time = time[f"{ongoing_schedule.scheduled_time}"]
                messages.error(
                    request,
                    f"You still have an ongoing schedule on {scheduled_date} on {scheduled_time}.",
                )
                return redirect("studentLife_system:Counseling App With Scheduler")

            formatted_date = current_datetime.strftime("%Y-%m-%d")
            counseling = form.save(commit=False)
            counseling.orno = 0
            counseling.dateRecieved = formatted_date
            counseling.studentID = student  # Assign the studentInfo instance
            counseling.counselingOrigin = "student"
            counseling.save()
            transaction = GuidanceTransaction(
                transactionType=f"{student.lastname} {student.firstname} requested a counseling schedule",
                transactionOrigin="counseling",
                transactionDate=timezone.now(),
            )
            transaction.save()

            messages.success(
                request,
                "Your request has been successfully added. An email will be sent if it is accepted.",
            )
            return redirect("studentLife_system:Counseling App With Scheduler")
    else:
        form = CounselingSchedulerForm()

    student_info = None
    # Check if the user has a related studentInfo object
    if user.student_id:
        student_info = user.student_id
    context = {"form": form, "student_id": student_info.studID}
    return render(request, "guidance/user/counseling_app.html", context)


@login_required
def counseling_app_admin_view(request):
    user = request.user
    if not user.user_type == "sao admin":
        return render(
            request,
            "guidance/user/access_violation.html",
            {"info": "For admin user only!"},
        )
    now = timezone.now()
    meeting_requests = (
        counseling_schedule.objects.filter(scheduled_date=now)
        .select_related("studentID")
        .order_by("-dateRecieved")
    )

    time = {
        "8-9": "8:00 AM - 9:00 AM",
        "9-10": "9:00 AM - 10:00 AM",
        "10-11": "10:00 AM-11:00 AM",
        "11-12": "11:00 AM -12:00 PM",
        "1-2": "1:00 PM - 2:00 PM",
        "2-3": "2:00 PM - 3:00 PM",
        "3-4": "3:00 PM - 4:00 PM",
        "4-5": "4:00 PM - 5:00 PM",
    }

    context = {
        "meeting_requests": meeting_requests,
        "time": time,
    }
    return render(request, "guidance/admin/counseling_app_admin_view.html", context)


@login_required
def counseling_schedule_admin(request):
    user = request.user
    if not user.user_type == "sao admin":
        return render(
            request,
            "guidance/user/access_violation.html",
            {"info": "For admin user only!"},
        )
    if request.method == "POST":
        form = CounselingSchedulerForm(request.POST)
        if form.is_valid():
            current_datetime = timezone.now()
            student_id = request.POST.get("student_id_val")

            # Get the studentInfo instance corresponding to the provided student ID
            student = get_object_or_404(studentInfo, studID=student_id)

            # Check for ongoing schedules
            ongoing_schedule = counseling_schedule.objects.filter(
                studentID=student, scheduled_date__gte=current_datetime.date()
            ).first()

            if (
                ongoing_schedule
                and not ongoing_schedule.status == "Declined"
                and not ongoing_schedule.status == "Expired"
            ):
                time = {
                    "8-9": "8:00 AM - 9:00 AM",
                    "9-10": "9:00 AM - 10:00 AM",
                    "10-11": "10:00 AM-11:00 AM",
                    "11-12": "11:00 AM -12:00 PM",
                    "1-2": "1:00 PM - 2:00 PM",
                    "2-3": "2:00 PM - 3:00 PM",
                    "3-4": "3:00 PM - 4:00 PM",
                    "4-5": "4:00 PM - 5:00 PM",
                }

                scheduled_date = ongoing_schedule.scheduled_date.strftime("%B %d, %Y")
                scheduled_time = time[f"{ongoing_schedule.scheduled_time}"]
                messages.error(
                    request,
                    f"You still have an ongoing schedule on {scheduled_date} on {scheduled_time}.",
                )
                return redirect("studentLife_system:Counseling App With Scheduler")

            formatted_date = current_datetime.strftime("%Y-%m-%d")
            counseling = form.save(commit=False)
            counseling.orno = 0
            counseling.dateRecieved = formatted_date
            counseling.studentID = student  # Assign the studentInfo instance
            counseling.save()
            transaction = GuidanceTransaction(
                transactionType=f"Counselor created a counseling schedule",
                transactionOrigin="counseling",
                transactionDate=timezone.now(),
            )
            transaction.save()
            return redirect("studentLife_system:Counseling App With Scheduler")
    else:
        form = CounselingSchedulerForm()

    context = {"form": form}
    return render(request, "guidance/admin/add_counseling.html", context)


def counselor_scheduler(request):
    if request.method == "POST":
        studendtID = request.POST.get("studentId", "")
        date_scheduled = request.POST.get("date_scheduled", "")
        date_scheduled = request.POST.get("date_scheduled", "")
        time = request.POST.get("time", "")
        reason = request.POST.get("reason", "")
        now = timezone.now()
        student = get_object_or_404(studentInfo, studID=studendtID)
        ongoing_schedule = counseling_schedule.objects.filter(
            studentID=student, scheduled_date__gte=now
        ).first()

        if (
            ongoing_schedule
            and not ongoing_schedule.status == "Declined"
            and not ongoing_schedule.status == "Expired"
        ):
            time = {
                "8-9": "8:00 AM - 9:00 AM",
                "9-10": "9:00 AM - 10:00 AM",
                "10-11": "10:00 AM-11:00 AM",
                "11-12": "11:00 AM -12:00 PM",
                "1-2": "1:00 PM - 2:00 PM",
                "2-3": "2:00 PM - 3:00 PM",
                "3-4": "3:00 PM - 4:00 PM",
                "4-5": "4:00 PM - 5:00 PM",
            }
            return HttpResponse("Student have already have an schedule on going.")
        status = "Accepted"
        counseling = counseling_schedule(
            counselingOrigin="counselor",
            dateRecieved=now,
            studentID=student,
            reason=reason,
            scheduled_date=date_scheduled,
            status=status,
            scheduled_time=time,
            email="",
        )
        counseling.save()
        transaction = GuidanceTransaction(
            transactionType=f"Counselor create a shedule.",
            transactionOrigin="counseling",
            transactionDate=timezone.now(),
        )
        transaction.save()
        return HttpResponse("Counseling scheduled successfully!")


@login_required
def exit_interview(request):
    user = request.user
    if request.method == "POST":
        form = ExitInterviewForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            fields = [
                "academically_too_challenging",
                "not_academically_challenging_enough",
                "does_not_offer_my_academic_major",
                "what_is_your_intended_major",
                "size_of_the_school",
                "location_of_the_school",
                "negative_social_campus_climate",
                "residence_hall_environment_not_positive",
                "social_environment_not_diverse_enough",
                "not_enough_campus_activities",
                "needed_more_academic_support",
                "financial",
                "medical_injury",
                "medical_pyscho",
                "family-obligations",
                "major_event",
            ]
            values = []
            for field in fields:
                value = request.POST.get(field, "")
                if value == "":
                    values.append("")
                else:
                    values.append(value)
            student_id = request.POST.get("studentID")

            # Get the studentInfo instance corresponding to the provided student ID
            student = get_object_or_404(studentInfo, studID=student_id)

            ongoing_request = exit_interview_db.objects.filter(
                studentID=student, status="Pending"
            ).first()

            if ongoing_request:
                messages.error(request, f"You still have an pending request.")
                return redirect("studentLife_system:Exit Interview")

            current_date = timezone.localtime(timezone.now())
            date_number = current_date.strftime("%m%d%y")  # Format date as MMDDYY

            # Sum the digits of the student ID
            digit_sum = sum(int(digit) for digit in str(student_id))

            # Combine date number and digit sum into a preliminary final number
            preliminary_final_number = f"{date_number}{digit_sum}"

            # Calculate the number of zeros needed to make the length 10 digits
            total_length = 10
            number_of_zeros_needed = total_length - len(preliminary_final_number)

            # Insert zeros between date number and digit sum
            final_number = f"{date_number}{'0' * number_of_zeros_needed}{digit_sum}"

            new_form.date = timezone.now()
            new_form.contributedToDecision = values
            new_form.studentID = student
            new_form.dateRecieved = timezone.now()
            new_form.save()
            transaction = GuidanceTransaction(
                transactionType=f"{student.lastname} {student.firstname} requested a exit interview schedule",
                transactionOrigin="exit",
                transactionDate=timezone.now(),
            )
            transaction.save()
            messages.success(
                request,
                "Your request has been successfully added. An email will be sent if it is accepted.",
            )
            return redirect("studentLife_system:Exit Interview")
    else:
        form = ExitInterviewForm()
    if user.student_id:
        student_info = user.student_id
    return render(
        request,
        "guidance/user/exit_interview.html",
        {"form": form, "student_id": student_info.studID},
    )


@login_required
def exit_interview_admin_view(request):
    user = request.user
    if not user.user_type == "sao admin":
        return render(
            request,
            "guidance/user/access_violation.html",
            {"info": "For admin user only!"},
        )
    now = timezone.now()
    exit_interview_request = (
        exit_interview_db.objects.filter(scheduled_date=now)
        .select_related("studentID")
        .order_by("-dateRecieved")
    )
    context = {
        "exit_interview_request": exit_interview_request,
    }
    return render(request, "guidance/admin/exit_interview_admin.html", context)


@login_required
def ojt_assessment(request):
    user = request.user
    if request.method == "POST":
        form = OjtAssessmentForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            student_id = request.POST.get("student_id_val")
            student = get_object_or_404(studentInfo, studID=student_id)
            currentdate = timezone.now()
            ongoing_request = OjtAssessment.objects.filter(
                studentID=student, status="Pending"
            ).first()

            if ongoing_request:
                messages.error(request, f"You still have an pending request.")
                return redirect("studentLife_system:OJT Assessment")

            new_form.studentID = student
            new_form.dateRecieved = currentdate
            new_form.dateAccepted = currentdate
            new_form.save()
            transaction = GuidanceTransaction(
                transactionType=f"{student.lastname} {student.firstname} requested a ojt assessment",
                transactionOrigin="ojt",
                transactionDate=timezone.now(),
            )
            transaction.save()
            messages.success(
                request,
                "Your request has been successfully added. An email will be sent if it is accepted.",
            )
            return redirect("studentLife_system:OJT Assessment")
    else:
        form = OjtAssessmentForm()
    if user.student_id:
        student_info = user.student_id
    return render(
        request,
        "guidance/user/ojt_assessment.html",
        {"form": form, "student_id": student_info.studID},
    )


@login_required
def ojt_assessment_admin_view(request):
    user = request.user
    if not user.user_type == "sao admin":
        return render(
            request,
            "guidance/user/access_violation.html",
            {"info": "For admin user only!"},
        )
    ojt_assessment_request = OjtAssessment.objects.select_related("studentID").order_by(
        "-dateRecieved"
    )
    context = {
        "ojt_assessment_request": ojt_assessment_request,
    }
    return render(request, "guidance/admin/ojt_assessment_admin.html", context)


def guidance_transaction(request):
    user = request.user
    if not user.user_type == "sao admin":
        return render(
            request,
            "guidance/user/access_violation.html",
            {"info": "For admin user only!"},
        )
    now = timezone.now()
    transactions = GuidanceTransaction.objects.filter(transactionDate=now).order_by(
        "-transactionId"
    )
    return render(request, "guidance/admin/transaction.html", {"form": transactions})


# Checker/Getter


def check_date_time_validity(request):
    if request.method == "POST":
        selected_date = request.POST.get("selected_date")
        try:
            # Convert the selected date string to a Python datetime object
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            # Query the counseling_schedule model for entries with the same scheduled_date
            counseling_schedules = counseling_schedule.objects.filter(
                scheduled_date=selected_date
            )
            # You can now do something with the counseling_schedules queryset, like serialize it to JSON
            serialized_data = [
                {"scheduled_time": schedule.scheduled_time, "status": schedule.status}
                for schedule in counseling_schedules
            ]
            return JsonResponse({"counseling_schedules": serialized_data})
        except ValueError:
            # Handle invalid date format
            return JsonResponse({"error": "Invalid date format"}, status=400)


def check_date_time_validity_for_exit(request):
    if request.method == "POST":
        selected_date = request.POST.get("selected_date")
        try:
            # Convert the selected date string to a Python datetime object
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            # Query the counseling_schedule model for entries with the same scheduled_date
            counseling_schedules = exit_interview_db.objects.filter(
                scheduled_date=selected_date
            )
            # You can now do something with the counseling_schedules queryset, like serialize it to JSON
            serialized_data = [
                {"scheduled_time": schedule.scheduled_time, "status": schedule.status}
                for schedule in counseling_schedules
            ]
            return JsonResponse({"counseling_schedules": serialized_data})
        except ValueError:
            # Handle invalid date format
            return JsonResponse({"error": "Invalid date format"}, status=400)


def search_student_info_for_individual(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number", "")
        try:
            student = studentInfo.objects.get(studID=id_number)
            response = {
                "student_id": student.studID,
                "name": f"{(student.lastname).title()}, {(student.middlename).title()}, {(student.firstname.title())}",
                "program": student.degree,
                "sex": student.sex,
            }
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)


def search_student_info(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number", "")
        try:
            student = studentInfo.objects.get(studID=id_number)
            response = {
                "student_id": student.studID,
                "name": f"{student.lastname}, {student.firstname}",
                "program": student.degree,
                "year": student.yearlvl,
                "contact_number": student.contact,
                "email": student.emailadd,
            }
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)


def search_exit_interview_request(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number", "")
        students = exit_interview_db.objects.filter(studentID__studID=id_number)
        if students.exists():
            response = []
            for student in students:
                response.append(
                    {
                        "exit_interview_id": student.exitinterviewId,
                        "date_received": student.dateRecieved.strftime("%B %d, %Y"),
                        "student_id": student.studentID.studID,
                        "name": f"{student.studentID.lastname}, {student.studentID.firstname}",
                        "status": student.status,
                    }
                )
            return JsonResponse(
                response, safe=False
            )  # safe=False to allow serialization of non-dict objects
        else:
            return JsonResponse({"error": "Student not found"}, status=404)


def search_ojt_assessment_request(request):
    if request.method == "POST":
        id_number = request.POST.get("id_number", "")
        students = OjtAssessment.objects.filter(studentID__studID=id_number)
        if students.exists():
            response = []
            for student in students:
                response.append(
                    {
                        "ojt_assessment_id": student.OjtRequestID,
                        "date_received": student.dateRecieved.strftime("%B %d, %Y"),
                        "student_id": student.studentID.studID,
                        "name": f"{student.studentID.lastname}, {student.studentID.firstname}",
                        "schoolyear": student.schoolYear,
                        "status": student.status,
                    }
                )
            return JsonResponse(
                response, safe=False
            )  # safe=False to allow serialization of non-dict objects
        else:
            return JsonResponse({"error": "Student not found"}, status=404)


def get_exit_interview_request(request):
    if request.method == "POST":
        recordID = request.POST.get("requestID", "")
        try:
            student = exit_interview_db.objects.get(exitinterviewId=recordID)
            if student.studentID.middlename == "NONE":
                middleInit = ""  # Set to empty string if text is 'NONE'
            else:
                middleInit = student.studentID.middlename[0]

            response = {
                "name": f"{student.studentID.firstname.title()} {middleInit} {student.studentID.lastname.title()}",
                "date": (student.date).strftime("%B %d, %Y"),
                "dateenrolled": (student.dateEnrolled).strftime("%B %d, %Y"),
                "contact": student.studentID.contact,
                "reasonforleaving": student.reasonForLeaving,
                "satisfiedWithAcadamic": student.satisfiedWithAcadamic,
                "feedbackWithAcademic": student.feedbackWithAcademic,
                "satisfiedWithSocial": student.satisfiedWithSocial,
                "feedbackWithSocial": student.feedbackWithSocial,
                "satisfiedWithServices": student.satisfiedWithServices,
                "feedbackWithServices": student.feedbackWithServices,
                "contributedToDecision": student.contributedToDecision,
                "intendedMajor": student.intendedMajor,
                "firstConsider": student.firstConsider,
                "whatCondition": student.whatCondition,
                "recommend": student.recommend,
                "howSatisfied": (student.howSatisfied).title(),
                "planTOReturn": student.planTOReturn,
                "accademicExperienceSatisfied": student.accademicExperienceSatisfied,
                "knowAboutYourTime": student.knowAboutYourTime,
                "currentlyEmployed": student.currentlyEmployed,
                "explainationEmployed": student.explainationEmployed,
            }
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)


def get_ojt_assessment_data(request):
    if request.method == "POST":
        recordID = request.POST.get("OjtRequestID", "")
        try:
            student = OjtAssessment.objects.get(OjtRequestID=recordID)
            if student.studentID.middlename == "NONE":
                middleInit = ""  # Set to empty string if text is 'NONE'
            else:
                middleInit = student.studentID.middlename[0]
            dateAccepted = student.dateAccepted
            formatted_dateAccepeted = dateAccepted.strftime("%B %d, %Y")
            response = {
                "name": f"{student.studentID.firstname.title()} {middleInit} {student.studentID.lastname.title()}",
                "schoolyear": student.schoolYear,
                "program": student.studentID.degree,
                "date_accepted": formatted_dateAccepeted,
            }
            return JsonResponse(response)
        except studentInfo.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)


def daily_montly_guidance_transaction(request):
    if request.method == "POST":
        sorttype = request.POST.get("sorttype", "")
        transactionFrom = request.POST.get("transactionFrom", "")
        if transactionFrom == "all":
            if sorttype == "all":
                transactions = GuidanceTransaction.objects.all().order_by(
                    "-transactionId"
                )
                return render(
                    request, "guidance/admin/transaction.html", {"form": transactions}
                )
            elif sorttype == "monthly":
                now = timezone.now()
                current_month = now.month
                transactions = GuidanceTransaction.objects.filter(
                    transactionDate__month=current_month
                ).order_by("-transactionId")
                return render(
                    request, "guidance/admin/transaction.html", {"form": transactions}
                )
            elif sorttype == "daily":
                now = timezone.now()
                transactions = GuidanceTransaction.objects.filter(
                    transactionDate=now
                ).order_by("-transactionId")
                return render(
                    request, "guidance/admin/transaction.html", {"form": transactions}
                )
        else:
            if sorttype == "all":
                transactions = GuidanceTransaction.objects.filter(
                    transactionOrigin=transactionFrom
                ).order_by("-transactionId")
                return render(
                    request, "guidance/admin/transaction.html", {"form": transactions}
                )
            elif sorttype == "monthly":
                now = timezone.now()
                current_month = now.month
                transactions = GuidanceTransaction.objects.filter(
                    transactionOrigin=transactionFrom,
                    transactionDate__month=current_month,
                ).order_by("-transactionId")
                return render(
                    request, "guidance/admin/transaction.html", {"form": transactions}
                )
            elif sorttype == "daily":
                now = timezone.now()
                transactions = GuidanceTransaction.objects.filter(
                    transactionOrigin=transactionFrom, transactionDate=now
                ).order_by("-transactionId")
                return render(
                    request, "guidance/admin/transaction.html", {"form": transactions}
                )


def show_transaction_specific_date(request):
    if request.method == "POST":
        selectedDate = request.POST.get("selectedDate", "")
        transactions = GuidanceTransaction.objects.filter(
            transactionDate=selectedDate
        ).order_by("-transactionId")
        return render(
            request, "guidance/admin/transaction.html", {"form": transactions}
        )


def sort_counseling_app_admin_view(request):
    sortBy = request.POST.get("sortBy", "")
    sortStatus = request.POST.get("sortStatus", "")
    if sortBy == "all" and sortStatus == "All":
        meeting_requests = (
            counseling_schedule.objects.all()
            .select_related("studentID")
            .order_by("-dateRecieved")
        )

        time = {
            "8-9": "8:00 AM - 9:00 AM",
            "9-10": "9:00 AM - 10:00 AM",
            "10-11": "10:00 AM-11:00 AM",
            "11-12": "11:00 AM -12:00 PM",
            "1-2": "1:00 PM - 2:00 PM",
            "2-3": "2:00 PM - 3:00 PM",
            "3-4": "3:00 PM - 4:00 PM",
            "4-5": "4:00 PM - 5:00 PM",
        }

        context = {
            "meeting_requests": meeting_requests,
            "time": time,
        }
        return render(request, "guidance/admin/counseling_app_admin_view.html", context)
    else:
        if sortBy == "all":
            meeting_requests = (
                counseling_schedule.objects.filter(status=sortStatus)
                .select_related("studentID")
                .order_by("-dateRecieved")
            )
            time = {
                "8-9": "8:00 AM - 9:00 AM",
                "9-10": "9:00 AM - 10:00 AM",
                "10-11": "10:00 AM-11:00 AM",
                "11-12": "11:00 AM -12:00 PM",
                "1-2": "1:00 PM - 2:00 PM",
                "2-3": "2:00 PM - 3:00 PM",
                "3-4": "3:00 PM - 4:00 PM",
                "4-5": "4:00 PM - 5:00 PM",
            }
            context = {
                "meeting_requests": meeting_requests,
                "time": time,
            }
            return render(
                request, "guidance/admin/counseling_app_admin_view.html", context
            )
        elif sortBy == "scheduledToday":
            now = timezone.now()
            if sortStatus == "All":
                meeting_requests = (
                    counseling_schedule.objects.filter(scheduled_date=now)
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            else:
                meeting_requests = (
                    counseling_schedule.objects.filter(
                        scheduled_date=now, status=sortStatus
                    )
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            time = {
                "8-9": "8:00 AM - 9:00 AM",
                "9-10": "9:00 AM - 10:00 AM",
                "10-11": "10:00 AM-11:00 AM",
                "11-12": "11:00 AM -12:00 PM",
                "1-2": "1:00 PM - 2:00 PM",
                "2-3": "2:00 PM - 3:00 PM",
                "3-4": "3:00 PM - 4:00 PM",
                "4-5": "4:00 PM - 5:00 PM",
            }
            context = {
                "meeting_requests": meeting_requests,
                "time": time,
            }
            return render(
                request, "guidance/admin/counseling_app_admin_view.html", context
            )
        elif sortBy == "recievedToday":
            now = timezone.now()
            if sortStatus == "All":
                meeting_requests = (
                    counseling_schedule.objects.filter(dateRecieved=now)
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            else:
                meeting_requests = (
                    counseling_schedule.objects.filter(
                        dateRecieved=now, status=sortStatus
                    )
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            time = {
                "8-9": "8:00 AM - 9:00 AM",
                "9-10": "9:00 AM - 10:00 AM",
                "10-11": "10:00 AM-11:00 AM",
                "11-12": "11:00 AM -12:00 PM",
                "1-2": "1:00 PM - 2:00 PM",
                "2-3": "2:00 PM - 3:00 PM",
                "3-4": "3:00 PM - 4:00 PM",
                "4-5": "4:00 PM - 5:00 PM",
            }
            context = {
                "meeting_requests": meeting_requests,
                "time": time,
            }
            return render(
                request, "guidance/admin/counseling_app_admin_view.html", context
            )


def sort_exit_interview_admin_view(request):
    sortBy = request.POST.get("sortBy", "")
    sortStatus = request.POST.get("sortStatus", "")
    if sortBy == "all" and sortStatus == "All":
        now = timezone.now()
        exit_interview_request = (
            exit_interview_db.objects.all()
            .select_related("studentID")
            .order_by("-dateRecieved")
        )
        context = {
            "exit_interview_request": exit_interview_request,
        }
        return render(request, "guidance/admin/exit_interview_admin.html", context)
    else:
        if sortBy == "all":
            now = timezone.now()
            exit_interview_request = (
                exit_interview_db.objects.filter(status=sortStatus)
                .select_related("studentID")
                .order_by("-dateRecieved")
            )
            context = {
                "exit_interview_request": exit_interview_request,
            }
            return render(request, "guidance/admin/exit_interview_admin.html", context)
        elif sortBy == "scheduledToday":
            now = timezone.now()
            if sortStatus == "All":
                exit_interview_request = (
                    exit_interview_db.objects.filter(scheduled_date=now)
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            else:
                exit_interview_request = (
                    exit_interview_db.objects.filter(
                        scheduled_date=now, status=sortStatus
                    )
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            context = {
                "exit_interview_request": exit_interview_request,
            }
            return render(request, "guidance/admin/exit_interview_admin.html", context)
        elif sortBy == "recievedToday":
            now = timezone.now()
            if sortStatus == "All":
                exit_interview_request = (
                    exit_interview_db.objects.filter(dateRecieved=now)
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            else:
                exit_interview_request = (
                    exit_interview_db.objects.filter(
                        dateRecieved=now, status=sortStatus
                    )
                    .select_related("studentID")
                    .order_by("-dateRecieved")
                )
            context = {
                "exit_interview_request": exit_interview_request,
            }
            return render(request, "guidance/admin/exit_interview_admin.html", context)


# Update/Delete


def update_counseling_schedule(request):
    if request.method == "POST":
        requestID = request.POST.get("counselingID", "")
        update_type = request.POST.get("type", "")
        if update_type == "accept":
            obj = get_object_or_404(counseling_schedule, counselingID=requestID)
            obj.status = "Accepted"
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Counseling Schedule request has been approved."
            email = obj.email
            obj.save()

            # This shit takes longer to finish that my will to live
            transaction = GuidanceTransaction(
                transactionType=f"{obj.studentID.firstname.title()} {obj.studentID.lastname.title()} Counseling Schedule requested was approved",
                transactionOrigin="counseling",
                transactionDate=timezone.now(),
            )
            transaction.save()
            send_mail(
                "Counseling Schedule Request",
                message,
                "notifytest391@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()

            # Optionally, you can return a JSON response indicating success
            return JsonResponse({"message": "Value updated successfully"})
        elif update_type == "decline":
            obj = get_object_or_404(counseling_schedule, counselingID=requestID)
            obj.status = "Declined"
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Counseling Schedule request has been declined."
            email = obj.email
            obj.save()
            transaction = GuidanceTransaction(
                transactionType=f"{obj.studentID.firstname.title()} {obj.studentID.lastname.title()}  Counseling Schedule was declined.",
                transactionOrigin="counseling",
                transactionDate=timezone.now(),
            )
            transaction.save()
            send_mail(
                "Counseling Schedule Request",
                message,
                "notifytest391@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()

            # Optionally, you can return a JSON response indicating success
            return JsonResponse({"message": "Value updated successfully"})


def delete_counseling_schedule(request):
    if request.method == "POST":
        requestID = request.POST.get("counselingID", "")
        obj = get_object_or_404(counseling_schedule, counselingID=requestID)
        obj.delete()
        return JsonResponse({"message": "Value updated successfully"})


def update_exit_interview_status(request):
    if request.method == "POST":
        requestID = request.POST.get("exitinterviewId", "")
        update_type = request.POST.get("type", "")
        if update_type == "accept":
            obj = get_object_or_404(exit_interview_db, exitinterviewId=requestID)
            obj.status = "Accepted"
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Exit Interview request has been approved."
            email = obj.emailadd
            obj.save()
            transaction = GuidanceTransaction(
                transactionType=f"{obj.studentID.firstname.title()} {obj.studentID.lastname.title()}  Exit Interview was approved.",
                transactionOrigin="exit",
                transactionDate=timezone.now(),
            )
            transaction.save()
            send_mail(
                "Exit Interview Request",
                message,
                "notifytest391@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()

            # Optionally, you can return a JSON response indicating success
            return JsonResponse({"message": "Value updated successfully"})
        elif update_type == "decline":
            obj = get_object_or_404(exit_interview_db, exitinterviewId=requestID)
            obj.status = "Declined"
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your Exit Interview request has been declined."
            email = obj.emailadd
            obj.save()
            transaction = GuidanceTransaction(
                transactionType=f"{obj.studentID.firstname.title()} {obj.studentID.lastname.title()}  Exit Interview was declined.",
                transactionOrigin="exit",
                transactionDate=timezone.now(),
            )
            transaction.save()
            send_mail(
                "Exit Interview Request",
                message,
                "notifytest391@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )
            obj.save()

            # Optionally, you can return a JSON response indicating success
            return JsonResponse({"message": "Value updated successfully"})


def delete_exit_interview_status(request):
    if request.method == "POST":
        requestID = request.POST.get("exitinterviewId", "")
        obj = get_object_or_404(exit_interview_db, exitinterviewId=requestID)
        obj.delete()
        return JsonResponse({"message": "Value updated successfully"})


def update_ojt_assessment(request):
    if request.method == "POST":
        requestID = request.POST.get("OjtRequestID", "")
        orno = request.POST.get("orno", "")
        update_type = request.POST.get("type", "")
        if update_type == "accept":
            obj = get_object_or_404(OjtAssessment, OjtRequestID=requestID)
            obj.status = "Accepted"
            obj.orno = orno
            obj.dateAccepted = timezone.now()
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your OJT Assessments/Psychological Issuance request has been approved."
            transaction = GuidanceTransaction(
                transactionType=f"{obj.studentID.firstname.title()} {obj.studentID.lastname.title()}  OJT Assessments/Psychological Issuance was approved.",
                transactionOrigin="ojt",
                transactionDate=timezone.now(),
            )
            transaction.save()
            email = obj.emailadd
            obj.save()
            send_mail(
                "OJT Assessments/Psychological Issuance Request",
                message,
                "notifytest391@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )

            # Optionally, you can return a JSON response indicating success
            return JsonResponse({"message": "Value updated successfully"})
        elif update_type == "decline":
            obj = get_object_or_404(OjtAssessment, OjtRequestID=requestID)
            obj.status = "Declined"
            obj.save()

            transaction = GuidanceTransaction(
                transactionType=f"{obj.studentID.firstname.title()} {obj.studentID.lastname.title()}  OJT Assessments/Psychological Issuance was declined.",
                transactionOrigin="ojt",
                transactionDate=timezone.now(),
            )
            transaction.save()
            message = f"Hello {obj.studentID.firstname.title()} {obj.studentID.lastname.title()} your OJT Assessments/Psychological Issuance request has been declined."
            email = obj.emailadd
            send_mail(
                "OJT Assessments/Psychological Issuance Request",
                message,
                "notifytest391@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )
            # Optionally, you can return a JSON response indicating success
            return JsonResponse({"message": "Value updated successfully"})


def delete_ojt_assessment(request):
    if request.method == "POST":
        requestID = request.POST.get("exitinterviewId", "")
        obj = get_object_or_404(OjtAssessment, OjtRequestID=requestID)
        obj.delete()
        return JsonResponse({"message": "Value updated successfully"})


# Filter


@register.filter
def get_formatted_time(dictionary, key):
    return dictionary.get(key)


# COMMUNITY INVOLVEMENT


def programs(request):
    loadProgram = Program.objects.filter(archive=False).order_by("-date_time")
    user = request.user.is_staff

    return render(
        request,
        "community_involvement/programs.html",
        {
            "url": "programs",
            "title": "Programs",
            "loadPrograms": loadProgram,
            "user": user,
        },
    )


def projects(request):
    loadProjects = Projects.objects.filter(archive=False).order_by("-date_time")
    qrCodeID = QrDonation.objects.all()

    user = request.user.is_staff

    return render(
        request,
        "community_involvement/projects.html",
        {
            "url": "projects",
            "title": "Projects",
            "loadProjects": loadProjects,
            "user": user,
            "qrCodeID": qrCodeID,
        },
    )


@login_required(login_url="")
def program_form(request):
    user = request.user.is_staff
    return render(
        request,
        "community_involvement/admin/programs-forms.html",
        {
            "url": "studentLife_system:program-form",
            "user": user,
        },
    )


@login_required(login_url="")
def project_form(request):
    user = request.user.is_staff
    return render(
        request,
        "community_involvement/admin/projects-forms.html",
        {
            "url": "project-form",
            "user": user,
        },
    )


def add_program(request):
    if request.method == "POST":
        Program(request.POST)

        title = request.POST.get("title")
        caption = request.POST.get("caption")
        image_upload = request.FILES.getlist("images")

        for image in image_upload:
            program = Program(
                title=title,
                caption=caption,
                image_upload=image,
            )
            program.save()

    return redirect("studentLife_system:program-form")


def add_project(request):
    if request.method == "POST":
        Project(request.POST)

        title = request.POST.get("title")
        caption = request.POST.get("caption")
        image_upload = request.FILES.getlist("images")

        for image in image_upload:
            project = Projects(
                title=title,
                caption=caption,
                image_upload=image,
            )
            project.save()

    return redirect("studentLife_system:project-form")


def gcash_mode(request):
    if request.method == "POST":
        MOD(request.POST)

        donated = request.POST["title"]
        name = request.POST["name"]
        gcash_number = request.POST["gcash_number"]
        amount = request.POST["amount"]
        image_details = request.FILES.getlist("images")

        for image in image_details:

            donation = MOD(
                donation_type="GCash",
                donated=donated,
                name=name,
                gcash_number=gcash_number,
                amount=amount,
                image_details=image,
            )

            donation.save()

    return redirect("studentLife_system:projects")


def gcash_mode_admin(request, id):
    qr = request.FILES.getlist("images")

    for image in qr:
        if int(QrDonation.objects.count()) == 0:
            qrCode = QrDonation(gcash=image)

        else:
            qrCode = QrDonation.objects.get(qr_id=id)
            qrCode.gcash = image

        qrCode.save()

    return redirect("studentLife_system:projects")


def bank_mode(request):
    if request.method == "POST":
        MOD(request.POST)

        donated = request.POST["title"]
        name = request.POST["name"]
        bank_card = request.POST["banks"]
        bank_number = request.POST["bank_number"]
        amount = request.POST["amount"]
        image_details = request.FILES.getlist("images")

        for image in image_details:

            donation = MOD(
                donation_type="Bank",
                donated=donated,
                name=name,
                bank_number=bank_number,
                bank_card=bank_card,
                amount=amount,
                image_details=image,
            )

            donation.save()

    return redirect("studentLife_system:projects")


def bank_mode_admin(request, id):
    qr = request.FILES.getlist("images")
    banks = request.POST.get("banks")

    for image in qr:
        if int(QrDonation.objects.count()) == 0:
            if banks == "BPI":
                qrCode = QrDonation(bpi=image)

            if banks == "BDO":
                qrCode = QrDonation(bdo=image)

            if banks == "LANDBACK":
                qrCode = QrDonation(landbank=image)

            if banks == "PNB":
                qrCode = QrDonation(pnb=image)

            if banks == "METRO BANK":
                qrCode = QrDonation(metro=image)

            if banks == "UNION BANK":
                qrCode = QrDonation(union=image)

            if banks == "CHINA BANK":
                qrCode = QrDonation(china=image)

        else:
            qrCode = QrDonation.objects.get(qr_id=id)

            if banks == "BPI":
                qrCode.bpi = image

            if banks == "BDO":
                qrCode.bdo = image

            if banks == "LANDBACK":
                qrCode.landbank = image

            if banks == "PNB":
                qrCode.pnb = image

            if banks == "METRO BANK":
                qrCode.metro = image

            if banks == "UNION BANK":
                qrCode.union = image

            if banks == "CHINA BANK":
                qrCode.china = image

        qrCode.save()

    return redirect("studentLife_system:projects")


def volunteer_mode(request):
    if request.method == "POST":

        donated = request.POST["title"]
        name = request.POST["name"]
        contact_number = request.POST["contact_number"]
        confirmation_photo = request.FILES.getlist("images")
        what_kind = request.POST["what_kind"]

        for image in confirmation_photo:
            if what_kind == "RELIEF GOODS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )

            if what_kind == "BELONGINGS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )

            if what_kind == "EQUIPMENTS":
                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    what_kind=what_kind,
                    recepient_things=request.POST["recepient_things"],
                    image_details=image,
                )

            if what_kind == "MONEY":
                recepient_name = request.POST["recepient_name"]

                MOD.objects.create(
                    donation_type="Volunteer",
                    donated=donated,
                    name=name,
                    contact_number=contact_number,
                    amount=request.POST["volunteer_amount"],
                    what_kind=what_kind,
                    recepient=recepient_name,
                    image_details=image,
                )

        if what_kind == "SERVICE":
            MOD.objects.create(
                donation_type="Volunteer",
                donated=donated,
                name=name,
                contact_number=contact_number,
                what_kind=what_kind,
                date_sched=request.POST["date_sched"],
            )

        # date_sched = request.POST["date_sched"]
        # amount = request.POST["amount"]

    return redirect("studentLife_system:projects")


@login_required(login_url="")
def reports(request):
    user = request.user.is_staff

    # loadDonations = MOD.objects.all()

    # for i in loadDonations:
    #     print(i.date_time)

    return render(
        request,
        "community_involvement/reports.html",
        {"url": "report", "user": user},
    )


def reports_all(request):
    loadDonations = MOD.objects.all()
    return render(
        request,
        "community_involvement/reports.html",
        {
            "url": "report",
            "loadDonations": loadDonations,
        },
    )


def reports_find(request):

    if request.method == "POST":
        month = request.POST.get("month")
        year = request.POST.get("year")

        loadDonations = MOD.objects.filter(date__month=month, date__year=year)
    return render(
        request,
        "community_involvement/reports.html",
        {
            "url": "report",
            "loadDonations": loadDonations,
        },
    )


def archive_project(request, id):

    Project.objects.filter(id=id).update(archive=True)

    return redirect("studentLife_system:project")


def archive_program(request, id):
    Program.objects.filter(id=id).update(archive=True)

    return redirect("studentLife_system:program")



def dashboard(request):
    user = request.user.is_staff
    return render(
        request,
        "community_involvement/admin/dashboard.html",
        {"user": user},
    )



def donation_dashboard(request):

    return render(request, "community_involvement/admin/donation.html")



def gcash_dashboard(request):
    loadGcashDonations = MOD.objects.filter(donation_type="GCash", status="Accepted")

    return render(
        request,
        "community_involvement/admin/gcash-dashboard.html",
        {"loadGcashDonations": loadGcashDonations},
    )



def banks_dashboard(request):
    loadBanksDonations = MOD.objects.filter(donation_type="Bank", status="Accepted")

    return render(
        request,
        "community_involvement/admin/banks-dashboard.html",
        {"loadBanksDonations": loadBanksDonations},
    )



def volunteer_dashboard(request):
    loadVolunteerDonations = MOD.objects.filter(
        donation_type="Volunteer", status="Accepted"
    )

    return render(
        request,
        "community_involvement/admin/volunteer-dashboard.html",
        {"loadVolunteerDonations": loadVolunteerDonations},
    )


def donation_validate(request):
    loadDonations = MOD.objects.filter(status=None)

    context = {}

    if int(MOD.objects.count()) == 0:
        cotext = {"url": "report"}
    else:
        for status in loadDonations:
            if status == None:
                context = {
                    "url": "report",
                    "loadDonations": loadDonations,
                    "status": status,
                }
            else:
                context = {
                    "url": "report",
                    "loadDonations": loadDonations,
                }

    return render(
        request,
        "community_involvement/admin/donation-validate.html",
        context,
    )


def donation_accept(request, id):
    MOD.objects.filter(id=id).update(status="Accepted")

    return redirect("studentLife_system:donation-validate")


def donation_decline(request, id):
    MOD.objects.filter(id=id).update(status="Declined")

    return redirect("studentLife_system:donation-validate")


def donation_filter(request):
    if request.method == "POST":
        statusFilter = request.POST.get("filterStatus")

        # print(statusFilter)
        if statusFilter == "Accepted" or statusFilter == "Declined":
            status = "Yes"
        else:
            status = None

        filterStatus = MOD.objects.filter(status=statusFilter)

    return render(
        request,
        "community_involvement/admin/donation-validate.html",
        {"loadDonations": filterStatus, "status": status},
    )

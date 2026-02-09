from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import User, TimeOffRequest, Holiday
from .forms import TimeOffRequestForm, HolidayForm, UserRegistrationForm
from datetime import datetime

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home_view(request):
    pending_count = TimeOffRequest.objects.filter(
        user=request.user, 
        status='pending'
    ).count()
    
    return render(request, 'home.html', {
        'pending_count': pending_count
    })

@login_required
def new_request_view(request):
    if request.method == 'POST':
        form = TimeOffRequestForm(request.POST)
        if form.is_valid():
            time_off = form.save(commit=False)
            time_off.user = request.user
            time_off.save()
            messages.success(request, 'Time-off request submitted successfully!')
            return redirect('manage_requests')
    else:
        form = TimeOffRequestForm()
    return render(request, 'new_request.html', {'form': form})

@login_required
def manage_requests_view(request):
    if request.user.role in ['manager', 'admin']:
        # Managers and admins see all pending requests
        requests = TimeOffRequest.objects.filter(status='pending')
    else:
        # Employees see only their own requests
        requests = TimeOffRequest.objects.filter(user=request.user)
    
    return render(request, 'manage_requests.html', {'requests': requests})

@login_required
def history_view(request):
    if request.user.role in ['manager', 'admin']:
        requests = TimeOffRequest.objects.exclude(status='pending')
    else:
        requests = TimeOffRequest.objects.filter(
            user=request.user
        ).exclude(status='pending')
    
    return render(request, 'history.html', {'requests': requests})

@login_required
def approve_request(request, request_id):
    if request.user.role not in ['manager', 'admin']:
        messages.error(request, 'You do not have permission to approve requests')
        return redirect('manage_requests')
    
    time_off_request = get_object_or_404(TimeOffRequest, id=request_id)
    time_off_request.status = 'approved'
    time_off_request.reviewed_by = request.user
    time_off_request.save()
    messages.success(request, 'Request approved successfully!')
    return redirect('manage_requests')

@login_required
def reject_request(request, request_id):
    if request.user.role not in ['manager', 'admin']:
        messages.error(request, 'You do not have permission to reject requests')
        return redirect('manage_requests')
    
    time_off_request = get_object_or_404(TimeOffRequest, id=request_id)
    time_off_request.status = 'rejected'
    time_off_request.reviewed_by = request.user
    time_off_request.save()
    messages.success(request, 'Request rejected')
    return redirect('manage_requests')

@login_required
def holidays_view(request):
    country = request.GET.get('country', 'USA')
    location = request.GET.get('location', 'ALL')
    
    holidays = Holiday.objects.filter(country=country)
    if location != 'ALL':
        holidays = holidays.filter(Q(location=location) | Q(location='ALL'))
    
    countries = Holiday.objects.values_list('country', flat=True).distinct()
    locations = Holiday.objects.filter(country=country).values_list('location', flat=True).distinct()
    
    return render(request, 'holidays.html', {
        'holidays': holidays,
        'countries': countries,
        'locations': locations,
        'selected_country': country,
        'selected_location': location,
    })

@login_required
def add_holiday_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can add holidays')
        return redirect('holidays')
    
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Holiday added successfully!')
            return redirect('holidays')
    else:
        form = HolidayForm()
    
    return render(request, 'add_holiday.html', {'form': form})

@login_required
def review_view(request):
    if request.user.role not in ['manager', 'admin']:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('home')
    
    pending_requests = TimeOffRequest.objects.filter(status='pending')
    return render(request, 'review.html', {'requests': pending_requests})

@login_required
def data_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can access data')
        return redirect('home')
    
    from django.db.models import Sum, Count, Q
    from datetime import timedelta
    
    # Get all users and calculate their work data
    users = User.objects.all().order_by('first_name')
    work_data = []
    
    for user in users:
        # Calculate holiday days taken
        holiday_days = TimeOffRequest.objects.filter(
            user=user,
            type='vacation',
            status='approved'
        ).count() * 2  # Assuming average 2 days per request
        
        # Calculate Jiatiao days (sick leave or other approved leave)
        jiatiao_days = TimeOffRequest.objects.filter(
            user=user,
            type__in=['sick', 'personal'],
            status='approved'
        ).aggregate(
            total=Sum(
                Count('id')
            )
        )['total'] or 0
        jiatiao_days = jiatiao_days * 2  # Assuming average 2 days per request
        
        # Calculate work days (assuming 20 work days per month)
        # This is a simplified calculation
        total_approved_days = TimeOffRequest.objects.filter(
            user=user,
            status='approved'
        ).count() * 2  # Assuming average 2 days per request
        
        work_days = 20 - (holiday_days + jiatiao_days) if (20 - (holiday_days + jiatiao_days)) > 0 else 0
        
        # Calculate work hours (8 hours per work day)
        work_hours = work_days * 8
        
        work_data.append({
            'name': user.get_full_name() or user.username,
            'holiday_days': holiday_days,
            'jiatiao_days': jiatiao_days,
            'work_days': work_days,
            'work_hours': work_hours,
        })
    
    return render(request, 'data.html', {
        'work_data': work_data,
    })

@login_required
def download_pdf_report(request):
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can download reports')
        return redirect('home')
    
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    from datetime import datetime
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Add title
    title = Paragraph("Work Data Report", title_style)
    elements.append(title)
    
    # Add date
    date_text = Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y')}",
        styles['Normal']
    )
    elements.append(date_text)
    elements.append(Spacer(1, 20))
    
    # Get work data
    users = User.objects.all().order_by('first_name')
    data = [['Name', 'Holiday Days', 'Jiatiao Days', 'Work Days', 'Work Hours']]
    
    for user in users:
        holiday_days = TimeOffRequest.objects.filter(
            user=user,
            type='vacation',
            status='approved'
        ).count() * 2
        
        jiatiao_days = TimeOffRequest.objects.filter(
            user=user,
            type__in=['sick', 'personal'],
            status='approved'
        ).count() * 2
        
        work_days = 20 - (holiday_days + jiatiao_days) if (20 - (holiday_days + jiatiao_days)) > 0 else 0
        work_hours = work_days * 8
        
        data.append([
            user.get_full_name() or user.username,
            str(holiday_days),
            str(jiatiao_days),
            str(work_days),
            str(work_hours)
        ])
    
    # Create table
    table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    
    # Add style to table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="work_data_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response
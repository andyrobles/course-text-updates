from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import CreateAccountForm, SignInForm, AddCourseForm, RemoveCourseForm
from courses.vcccd import CourseSnapshot
from .models import Course

def require_sign_in(view_function):
	def wrapped_view_function(request):
		if not request.user.is_authenticated:
			return redirect('sign_in')
		return view_function(request)
	return wrapped_view_function

def landing(request):
	return render(request, 'courses/landing.html')

@require_sign_in
def index(request):
	return render(request, 'courses/index.html', {'course_list': Course.objects.filter(user=request.user)})

def create_account(request):
	if request.method == 'POST':
		# Get submitted create account form
		create_account_form = CreateAccountForm(request.POST)

		if create_account_form.is_valid() and is_valid_phone_number(create_account_form.cleaned_data['phone_number']):
			# Tell user to try again if confirm password does not match
			if create_account_form.cleaned_data['password'] != create_account_form.cleaned_data['confirm_password']:
				return render(request, 'courses/landing_modal.html', {
					'modal_title': 'Try Again',
					'icon': 'exclamation-triangle',
					'message': 'Password and Confirm password fields do not match'
				})

			# Create a user with the supplied email and password
			user = User.objects.create_user(
				username=create_account_form.cleaned_data['phone_number'],
				password=create_account_form.cleaned_data['password']
			)

			# Authenticate user that we just created  
			login(request, user)

			# Redirect to index page
			return redirect('index')
			
		
		# Return error message if invalid form
		return render(request, 'courses/landing_modal.html', {
			'modal_title': 'Try Again',
			'icon': 'exclamation-triangle',
			'message': 'Form contained one or more invalid fields'
		})

	# Render create account form if a get request		
	return render(request, 'courses/landing_modal.html', {
		'form': CreateAccountForm(),
		'icon': 'user-plus',
		'modal_title': 'Create Account'
	})

def sign_in(request):
	if request.method == 'POST':
		# Get form from post request
		sign_in_form = SignInForm(request.POST)

		if sign_in_form.is_valid() and is_valid_phone_number(sign_in_form.cleaned_data['phone_number']):
			# Authenticate user with form data
			user = authenticate(
				username=sign_in_form.cleaned_data['phone_number'],
				password=sign_in_form.cleaned_data['password']
			)

			if user is not None:
				# Login authenticated user
				login(request, user)

				# Redirect to index
				return redirect('index')

			# Return an invalid login error message
			return render(request, 'courses/landing_modal.html', {
				'icon': 'exclamation-triangle',
				'modal_title': 'Try Again',
				'message': 'Username or password were incorrect'
			})
		else:
			# Tell user to try again if form was invalid
			return render(request, 'courses/landing_modal.html', {
				'icon': 'exclamation-triangle',
				'modal_title': 'Try Again',
				'message': 'Form contained one or more invalid fields'
			})

	# Provide user a blank sign in form
	return render(request, 'courses/landing_modal.html', {
		'form': SignInForm(),
		'icon': 'sign-in-alt',
		'modal_title': 'Sign In'
	})

def is_valid_phone_number(string_value):
	return len(string_value) == 9 and string_value.isdigit()

@require_sign_in
def add_course(request):
	if request.method == 'POST':
		# Get submitted course form
		course_form = AddCourseForm(request.POST)

		if course_form.is_valid():
			# Get snapshot of course specified by user by CRN
			course_snapshot = CourseSnapshot(course_form.cleaned_data['course_reference_number'])

			# Create a course with attributes identical to snapshot

			identical_courses = Course.objects.filter(user=request.user, crn=course_snapshot.crn)

			if len(identical_courses) >= 1:
				return render(request, 'courses/index_modal.html', {
					'course_list': Course.objects.filter(user=request.user),
					'modal_title': 'Duplicate Course',
					'icon': 'exclamation-triangle',
					'message': 'Course with this CRN already exists on watch list'
				})

			course = Course(
				user=request.user,
				crn=course_snapshot.crn,
				title=course_snapshot.title,
				instructor=course_snapshot.instructor,
				meeting_time=course_snapshot.meeting_time,
				location=course_snapshot.location,
				status=course_snapshot.status,
				seating_availability=course_snapshot.seating_availability,
				waitlist_availability=course_snapshot.waitlist_availability
			)

			course.save()
			
			return redirect('index')
			
		else:
			# Return error message if invalid form
			return render(request, 'courses/index_modal.html', {
				'course_list': Course.objects.filter(user=request.user),
				'modal_title': 'Try Again',
				'icon': 'exclamation-triangle',
				'message': 'Form contained one or more invalid fields'
			})

	# Render create course form if a get request
	return render(request, 'courses/index_modal.html', {
		'course_list': Course.objects.filter(user=request.user),
		'form': AddCourseForm(),
		'icon': 'graduation-cap',
		'modal_title': 'Add Course'
	})

def remove_course(request):
	if request.method == 'POST':
		# Get submitted form form user when request method is post
		form = RemoveCourseForm(request.POST)
		form.fields['course'].queryset=Course.objects.filter(user=request.user)
			

		if form.is_valid():
			# Get selected course from user and delete it
			course = form.cleaned_data['course']
			course.delete()

			return redirect('index')

		# Return error form when form is invalid
		return render(request, 'courses/index_modal.html', {
			'course_list': Course.objects.filter(user=request.user),
			'icon': 'exclamation-triangle',
			'modal_title': 'Try Again',
			'message': 'Submitted form was invalid'
		})

	remove_course_form = RemoveCourseForm()
	remove_course_form.fields['course'].queryset=Course.objects.filter(user=request.user)
			
	# Return blank remove coures form when request method is get
	return render(request, 'courses/index_modal.html', {
		'course_list': Course.objects.filter(user=request.user),
		'form': remove_course_form,
		'icon': 'trash',
		'modal_title': 'Remove Course'
	})

def sign_out(request):
	# Sign out whichever user is currently signed in
	logout(request)

	# Redirect to landing page
	return redirect('landing')

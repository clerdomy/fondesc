from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse

from .models import Project, ProjectComment
from .forms import ProjectForm, ProjectCommentForm

def project_list(request):
    """Display list of published projects"""
    # Get all published projects
    projects = Project.objects.filter(status='published')
    
    # Filter by course if specified
    course_id = request.GET.get('course')
    if course_id:
        projects = projects.filter(course_id=course_id)
    
    # Filter by technology if specified
    tech = request.GET.get('tech')
    if tech:
        projects = projects.filter(technologies__icontains=tech)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(technologies__icontains=query)
        )
    
    # Filter by type (course project or personal)
    project_type = request.GET.get('type')
    if project_type == 'course':
        projects = projects.filter(is_course_project=True)
    elif project_type == 'personal':
        projects = projects.filter(is_course_project=False)
    
    # Pagination
    paginator = Paginator(projects, 12)  # 12 projects per page
    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)
    
    # Get all courses with projects for filtering
    from courses.models import Course
    courses_with_projects = Course.objects.filter(projects__isnull=False).distinct()
    
    # Get all technologies for filtering
    all_technologies = set()
    for project in Project.objects.filter(status='published'):
        all_technologies.update(project.get_technologies_list())
    
    context = {
        'projects': projects,
        'courses': courses_with_projects,
        'technologies': sorted(all_technologies),
        'selected_course': course_id,
        'selected_tech': tech,
        'query': query,
        'project_type': project_type,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, slug):
    """Display project details"""
    project = get_object_or_404(Project, slug=slug, status='published')
    comments = project.comments.all()
    
    # Handle new comments
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = ProjectCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.project = project
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Your comment has been added.')
            return redirect('project_detail', slug=slug)
    else:
        comment_form = ProjectCommentForm()
    
    # Get related projects (same course or technologies)
    related_projects = Project.objects.filter(status='published').exclude(id=project.id)
    if project.course:
        related_projects = related_projects.filter(course=project.course)
    else:
        # If no course, find projects with similar technologies
        tech_list = project.get_technologies_list()
        if tech_list:
            q_objects = Q()
            for tech in tech_list:
                q_objects |= Q(technologies__icontains=tech)
            related_projects = related_projects.filter(q_objects)
    
    related_projects = related_projects[:4]  # Limit to 4 related projects
    
    context = {
        'project': project,
        'comments': comments,
        'comment_form': comment_form,
        'related_projects': related_projects,
        'technologies': project.get_technologies_list(),
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def my_projects(request):
    """Display user's projects"""
    projects = Project.objects.filter(user=request.user)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status and status in dict(Project.STATUS_CHOICES):
        projects = projects.filter(status=status)
    
    context = {
        'projects': projects,
        'selected_status': status,
    }
    return render(request, 'projects/my_projects.html', context)


@login_required
def create_project(request):
    """Create a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.status = 'draft'  # Start as draft
            project.save()
            messages.success(request, 'Pwojè ou a kreye avèk siksè.')
            return redirect('my_projects')
    else:
        form = ProjectForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Project',
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def edit_project(request, slug):
    """Edit an existing project"""
    project = get_object_or_404(Project, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pwojè ou a mete ajou avèk siksè.')
            return redirect('my_projects')
    else:
        form = ProjectForm(instance=project, user=request.user)
    
    context = {
        'form': form,
        'project': project,
        'title': 'Edit Project',
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def delete_project(request, slug):
    """Delete a project"""
    project = get_object_or_404(Project, slug=slug, user=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Pwojè ou a efase.')
        return redirect('my_projects')
    
    context = {
        'project': project,
    }
    return render(request, 'projects/project_confirm_delete.html', context)


@login_required
def publish_project(request, slug):
    """Publish a draft project"""
    project = get_object_or_404(Project, slug=slug, user=request.user, status='draft')
    
    if request.method == 'POST':
        project.status = 'published'
        project.save()
        messages.success(request, 'Your project has been published.')
        return redirect('project_detail', slug=project.slug)
    
    return redirect('project_detail', slug=project.slug)


import os
import zipfile
import tempfile
import subprocess
import time
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.utils.encoding import smart_str
from django.views import generic
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .models import Settings, MesaJob

class SettingsView(generic.DetailView):
    model = Settings
    template_name = "settings.html"


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.label_suffix = ''


@login_required
def home(request):
    return render(request, "home.html")

@login_required
def dashboard_job_table(request):
    return render(request, "dashboard-job-table.html")
   

@login_required
def dashboard_all_checks_card(request):
    return render(request, "dashboard-all-checks-card.html")

#@login_required
#def dashboard_report_generator_card(request):
#    return render(request, "dashboard-report-generator-card.html")

@login_required
def settings(request):
    settings = Settings.get_settings()

    if request.method == "POST":
        settings.project_name = request.POST.get("project_name")

        if request.FILES.get("scope_file"):
            settings.scope = request.FILES.get("scope_file").read().decode("utf-8")
        else:
            settings.scope = request.POST.get("scope")

        if request.FILES.get("exclusions_file"):
            settings.exclusions = request.FILES.get("exclusions_file").read().decode("utf-8")
        else:
            settings.exclusions = request.POST.get("exclusions")

        # Temporary removal of credentialed settings
        # settings.domain_fqdn = request.POST.get("domain_fqdn")
        # settings.domain_controller = request.POST.get("domain_controller")
        # settings.domain_user = request.POST.get("domain_user")
        # settings.domain_password = request.POST.get("domain_password")
        # settings.neo4j_user = request.POST.get("neo4j_user")
        # settings.neo4j_password = request.POST.get("neo4j_password")
        settings.customer_name = request.POST.get("customer_name")
        settings.customer_initials = request.POST.get("customer_initials")
        settings.save()

    return render(request, 'settings.html')

@login_required
def job_run(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(MesaJob, pk=job_id)
        pid = job.run()
        print(job.get_pid())
        return JsonResponse({"status": "success", "pid": pid})
    else:
        # return a 404
        return JsonResponse({"status": "404"})

@login_required
def job_run_all(request):
    if request.method == "POST":
        jobs = MesaJob.objects.filter(name=MesaJob.MESA_JOB_ALL_CHECKS_NAME)
        pid = "N/A"
        if len(jobs) > 0:
            pid = jobs[0].run()
        return JsonResponse({"status": "success", "pid": pid})
    else:
        return JsonResponse({"status": "404"})

@login_required
def job_generate_report(request):
    if request.method == "GET":
        jobs = MesaJob.objects.filter()
        pid = "N/A"
        settings = Settings.get_settings()
        zip_file_path = f"/root/.mesa/projects/output/{settings.project_name}/customer_deliverable/{settings.customer_initials}-Customer-Report.zip"
        
        # Run the report generator function of MESA-Toolkit
        process = subprocess.Popen(f"MESA-Toolkit --project-name {settings.project_name} --customer-name '{settings.customer_name}' --customer-initials {settings.customer_initials} -o report_generator", shell=True, cwd=MesaJob.get_job_directory())
        process.wait() # Wait for the command to complete

        # Now proceed to download the file
        file = open(zip_file_path, 'rb')
        response = FileResponse(file, as_attachment=True, filename=smart_str(os.path.basename(zip_file_path)))
        # This is a temporary fix until the Download Report button has been updated
        os.system("rm -rf /root/.mesa/projects/output")
        return response
    else:
        return JsonResponse({"status": "404"})

@login_required
def job_stop(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(MesaJob, pk=job_id)
        pid = job.get_pid()
        print(f"Directing {job.id} to stop {job.get_pid()}")
        job.stop()
        return JsonResponse({"status": f"success - {pid}"})
    else:
        return JsonResponse({"status": "404"})

@login_required
def job_stop_all(request):
    if request.method == "POST":
        jobs = MesaJob.objects.filter(name=MesaJob.MESA_JOB_ALL_CHECKS_NAME)
        if len(jobs) > 0:
            jobs[0].stop()
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "404"})

@login_required
def job_download_data(request, job_id):
    if request.method == "GET":
        response = {}
        job = get_object_or_404(MesaJob, pk=job_id)
        if job.is_running():
            response = {"error": "Data cannot be downloaded while job is running"}
        else:
            folder_path = job._get_output_folder()

            settings = Settings.get_settings()
            zip_file_path = os.path.join(
                tempfile.gettempdir(),
                slugify(f'{settings.project_name}-{job.name}') + '.zip'
            )

            try:
                # Create a zip archive of the folder
                with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, folder_path)
                            zipf.write(file_path, arcname=arcname)

                # Serve the zip file as a response
                file = open(zip_file_path, 'rb')
                response = FileResponse(file, as_attachment=True, filename=smart_str(os.path.basename(zip_file_path)))
                return response
            finally:
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)
    else:
        result = {"status": "404"}

    return JsonResponse(result)

@login_required
def job_delete_data(request, job_id):
    if request.method == "POST":
        response = {}
        job = get_object_or_404(MesaJob, pk=job_id)
        if job.is_running():
            response = {"error": "Data cannot be deleted while job is running"}
        else:
            job.delete_data()
            result = {"status": f"success"}
    else:
        result = {"status": "404"}

    return JsonResponse(result)

@login_required
def demo(request):
    return render(request, "demo.html")

from .models import Settings, MesaJob

def sitewide_context(request):
    context = {
        'user': request.user
    }

    if request.user.is_authenticated:
        all_checks_job = None

        jobs = MesaJob.objects.filter(name=MesaJob.MESA_JOB_ALL_CHECKS_NAME)
        if len(jobs) > 0:
            all_checks_job = jobs[0]

        context['jobs'] = MesaJob.objects.filter(visible=True)
        context['all_checks_job'] = all_checks_job
        context['settings'] = Settings.get_settings()

    return context

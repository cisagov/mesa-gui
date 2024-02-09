import os
import shutil
import datetime
import subprocess
from pathlib import Path
from django.db import models
from django.template import Template, Context
from django.utils import timezone
import psutil
import traceback
import logging
import traceback
import threading

# Configure logging to print to the console
logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()

def _ensure_directory_exists(path:Path):
    path.mkdir(exist_ok = True)

class Settings(models.Model):
    project_name = models.CharField(max_length=50)
    scope= models.TextField(blank=False)
    exclusions = models.TextField(blank=True)
    domain_fqdn = models.CharField(max_length=255)
    domain_controller = models.CharField(max_length=255)
    domain_user = models.CharField(max_length=255)
    domain_password = models.CharField(max_length=255)
    neo4j_user = models.CharField(max_length=255)
    neo4j_password = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255,default="Acme Corporation")
    customer_initials = models.CharField(max_length=20,default="ACME")

    @staticmethod
    def get_settings():
        try:
            settings = Settings.objects.get()
        except Settings.DoesNotExist:
            settings = Settings.objects.create()
        return settings


class MesaJob(models.Model):
    MESA_JOB_DIRECTORY = "~/.mesa/projects/"
    MESA_JOB_FILE_COMPLETE = ".complete"
    MESA_JOB_FILE_RUNNING = ".running"
    MESA_JOB_FILE_STARTED = ".started"
    MESA_JOB_FILE_SCOPE = "scope.txt"
    MESA_JOB_FILE_EXCLUSIONS = "exclusions.txt"
    MESA_JOB_STATUS_NOT_STARTED = "Not Started"
    MESA_JOB_STATUS_QUEUED = "Queued"
    MESA_JOB_STATUS_RUNNING = "Running"
    MESA_JOB_STATUS_COMPLETE = "Complete"
    MESA_JOB_ALL_CHECKS_NAME = "ALL_CHECKS"


    name = models.CharField(max_length=50)
    command = models.CharField(max_length=512)
    status = models.CharField(max_length=50, default="Not Started")
    pid = models.CharField(max_length=10, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    relative_output_folder = models.CharField(max_length=255, blank=True, default="")
    visible = models.BooleanField(default=True)


    @staticmethod
    def get_job_directory() -> Path:
        return Path(os.path.expanduser(MesaJob.MESA_JOB_DIRECTORY))


    @staticmethod
    def get_project_directory() -> Path:
        settings = Settings.get_settings()
        project_directory = MesaJob.get_job_directory()
        project_directory /= Path(settings.project_name + "_Scans")
        return project_directory


    @staticmethod
    def prepare_scoping_files() -> None:
        settings = Settings.get_settings()
        output_folder = MesaJob.get_project_directory()
        # write settings.scope to output_folder/MesaJob.MESA_JOB_FILE_SCOPE
        scope_file = output_folder / Path(MesaJob.MESA_JOB_FILE_SCOPE)
        scope_file.write_text(settings.scope)
        # write settings.exclusions to output_folder/MesaJob.MESA_JOB_FILE_EXCLUSIONS
        exclusions_file = output_folder / Path(MesaJob.MESA_JOB_FILE_EXCLUSIONS)
        exclusions_file.write_text(settings.exclusions)


    @staticmethod
    def _get_command(command: str) -> str:
        command = Template(command)
        settings = Settings.get_settings()
        context = Context({
            "project_name": settings.project_name,
            "scope": os.path.join(MesaJob.get_project_directory(), MesaJob.MESA_JOB_FILE_SCOPE),
            "exclusions": os.path.join(MesaJob.get_project_directory(), MesaJob.MESA_JOB_FILE_EXCLUSIONS),
            "domain_fqdn": settings.domain_fqdn,
            "domain_controller": settings.domain_controller,
            "domain_user": settings.domain_user,
            "domain_password": settings.domain_password,
            "neo4j_user": settings.neo4j_user,
            "neo4j_password": settings.neo4j_password,
            "customer_name": settings.customer_name,
            "customer_initials": settings.customer_initials,
        })
        return command.render(context)


    @staticmethod
    def run_all() -> str:
        all_checks_job = MesaJob.objects.filter(name=MesaJob.MESA_JOB_ALL_CHECKS_NAME)
        if all_checks_job:
            all_checks_job[0].run()

    #def generate_report() -> str:
    #    generate_report_job = MesaJob.objects.filter(name=MesaJob.MESA_JOB_REPORT_GENERATOR_NAME)
    #    if generate_report_job:
    #        generate_report_job[0].run()


    def __str__(self) -> str:
        return self.name


    def _get_output_folder(self) -> Path:
        output_folder = MesaJob.get_project_directory()
        output_folder /= Path(self.relative_output_folder)
        return output_folder


    def _get_file_path(self, file):
        return Path(self._get_output_folder()/file)


    def get_command(self) -> str:
        return MesaJob._get_command(self.command)


    def _get_timestamp_from_file(self, file_name) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            file_name.stat().st_mtime,
            tz=timezone.get_current_timezone()
        )


    def _does_process_cmdline_match(self, process:psutil.Process):
        this_command = self.get_command().split(' ')
        this_operation = this_command[this_command.index("-o") + 1]
        try:
            cmdline = process.cmdline()

            operation_index = cmdline.index('-o')
            if operation_index:
                operation = cmdline[operation_index + 1]
                if (this_command[0] in ' '.join(cmdline)
                    and this_operation == operation):
                    return True
        except:
            pass
        return False


    def _is_pid_active(self) -> bool:
        pid = self.get_pid()
        if not pid:
            running_file = self._get_file_path(MesaJob.MESA_JOB_FILE_RUNNING)
            if running_file.exists():
                self.set_pid(running_file.read_text())
                self.save()

        if pid:
            pid = int(pid)
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)

                if process.status() in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                    self.set_pid(None)
                    self.save()
                    return False

                return True
            else:
                self.set_pid(None)
                self.save()

        return False


    def _is_all_checks_job(self) -> bool:
        if self.name == MesaJob.MESA_JOB_ALL_CHECKS_NAME:
            return True

        return False


    def set_pid(self, pid):
        self.pid = pid


    def get_pid(self):
        return self.pid


    def set_status(self, status):
        self.status = status
        self.save()


    def is_running(self):
        if self.update_status() == MesaJob.MESA_JOB_STATUS_RUNNING:
            return True
        else:
            return False


    def is_complete(self):
        if self.update_status() == MesaJob.MESA_JOB_STATUS_COMPLETE:
            return True
        else:
            return False


    def is_not_started(self):
        if self.update_status() == MesaJob.MESA_JOB_STATUS_NOT_STARTED:
            return True
        else:
            return False

    def is_queued(self):
        if self.update_status() == MesaJob.MESA_JOB_STATUS_QUEUED:
            return True
        else:
            return False


    def update_status(self, status=None) -> str:
        if not status:
            # status = MesaJob.MESA_JOB_STATUS_NOT_STARTED
            status = self.status
            all_checks_job = MesaJob.objects.filter(name=MesaJob.MESA_JOB_ALL_CHECKS_NAME)[0]
            output_folder = self._get_output_folder()
            started_file = Path(output_folder/MesaJob.MESA_JOB_FILE_STARTED)
            running_file = Path(output_folder/MesaJob.MESA_JOB_FILE_RUNNING)
            complete_file = Path(output_folder/MesaJob.MESA_JOB_FILE_COMPLETE)

            if started_file.exists():
                self.started_at = self._get_timestamp_from_file(started_file)

            if all_checks_job._is_pid_active():
                if self._is_all_checks_job():
                    status = MesaJob.MESA_JOB_STATUS_RUNNING
                elif running_file.exists():
                    status = MesaJob.MESA_JOB_STATUS_RUNNING
                elif complete_file.exists():
                    completed_time = self._get_timestamp_from_file(complete_file)
                    if completed_time < all_checks_job.started_at:
                        status = MesaJob.MESA_JOB_STATUS_QUEUED
                    else:
                        status = MesaJob.MESA_JOB_STATUS_COMPLETE
                        self.finished_at = completed_time
                elif self.status == MesaJob.MESA_JOB_STATUS_NOT_STARTED:
                    status = MesaJob.MESA_JOB_STATUS_QUEUED
            elif self._is_pid_active():
                status = MesaJob.MESA_JOB_STATUS_RUNNING
            elif running_file.exists():
                # The PID is dead, and the running file was left behind,
                #  indicating the job did not finish as intended
                running_file.unlink()
                status = MesaJob.MESA_JOB_STATUS_NOT_STARTED
                self.finished_at = None
            elif complete_file.exists():
                status = MesaJob.MESA_JOB_STATUS_COMPLETE
                self.finished_at = self._get_timestamp_from_file(complete_file)
            else:
                status = MesaJob.MESA_JOB_STATUS_NOT_STARTED
                if not running_file.exists() and not started_file.exists() and not running_file.exists():
                    self.started_at = None
                    self.finished_at = None

        self.set_status(status)
        self.save()

        return self.status


    def run(self):
        with lock:
            print("entering thread-safe zone")
            if not self.pid:
                _ensure_directory_exists(MesaJob.get_project_directory())
                MesaJob.prepare_scoping_files()
                logging.debug(f"MesaJob.run: Running {self.get_command()}")
                process = subprocess.Popen(self.get_command(), shell=True, cwd=MesaJob.get_job_directory())
                self.started_at = timezone.now()
                self.status = MesaJob.MESA_JOB_STATUS_RUNNING
                self.finished_at = None

                self.set_pid(str(process.pid))
                self.save()

                if self._is_all_checks_job():
                    for job in MesaJob.objects.filter(visible=True):
                        job.pid = self.pid
                        job.status = MesaJob.MESA_JOB_STATUS_QUEUED
                        job.save()

            print("leaving thread-safe zone")
        return self.get_pid()


    def stop(self):
        logging.debug(f"MesaJob.stop: Stopping {self.get_pid()}")
        if self._is_all_checks_job():
            for job in MesaJob.objects.filter(visible=True):
                if job.status == MesaJob.MESA_JOB_STATUS_QUEUED:
                    job.status == MesaJob.MESA_JOB_STATUS_NOT_STARTED
                job.stop()
        if self.pid:
            logging.debug(f"MesaJob.stop: Checking if {self.get_pid()} is running...")
            if psutil.pid_exists(int(self.pid)):
                process = psutil.Process(int(self.pid))
                if process:
                    for child in process.children(recursive=True):
                        try:
                            child.kill()
                        except Exception as e:
                            print(e)
                    try:
                        process.kill()
                    except:
                        pass


    def delete_data(self):
        if not self.is_running():
            output_folder = self._get_output_folder()

            if output_folder.exists():
                shutil.rmtree(output_folder)

            self.status = MesaJob.MESA_JOB_STATUS_NOT_STARTED
            self.finished_at = None
            self.started_at = None
            self.save()

            return True
        else:
            return False

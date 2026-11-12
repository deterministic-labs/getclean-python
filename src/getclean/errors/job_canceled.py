from ..types.job import Job


class JobCanceled(Exception):
    """The upload's job was canceled before a record was made. The job is on the error."""

    job: Job

    def __init__(self, job: Job) -> None:
        super().__init__(f"The job {job.id} was canceled before a record was made.")
        self.job = job

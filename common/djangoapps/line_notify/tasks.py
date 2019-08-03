from celery import task


@task(name='send_line_notify', bind=True, default_retry_delay=30, max_retries=2)
def send_line_notify(x):
    print(x)
    print("Hello Celery")
    return 'finish'
from django import template
from datetime import datetime
import pytz
from voting.models import PollingSchedule

register = template.Library()

@register.filter
def has_polling_ended(polling_schedule):
    now = datetime.now(pytz.timezone('Asia/Karachi')).time()
    return now > polling_schedule.end_datetime.time()

@register.filter
def is_time_within_range(current_time):
    polling_schedule = PollingSchedule.objects.latest('start_datetime')
    start_time = polling_schedule.start_datetime.time()
    end_time = polling_schedule.end_datetime.time()
    now = current_time
    return start_time <= now <= end_time
from datetime import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Sum
import pytz
from voting.models import PollingSchedule, Vote
from .models import CustomUser, Halka

def get_winner_for_halka(halka):
    candidates = CustomUser.objects.filter(groups__name='candidate', halka=halka)
    winner = None
    max_votes = 0
    for candidate in candidates:
        candidate_votes = Vote.objects.filter(candidate=candidate, halka=halka).aggregate(Sum('vote_count'))['vote_count__sum']
        if candidate_votes is None:
            candidate_votes = 0
        if candidate_votes > max_votes:
            max_votes = candidate_votes
            winner = {
                'candidate': candidate,
                'halka': halka,
                'votes': candidate_votes,
            }
    return winner

def get_winners_by_halka():
    winners_by_halka = {}
    halkas = Halka.objects.all()  # Update this based on your model
    for halka in halkas:
        winners_by_halka[halka] = get_winner_for_halka(halka)
    return winners_by_halka

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)
        )

account_activation_token = TokenGenerator()

def get_polling_schedule_context():
    context = {}
    try:
        polling_schedule = PollingSchedule.objects.latest('start_datetime')
        now = datetime.now(pytz.timezone('Asia/Karachi'))

        context['polling_schedule'] = polling_schedule
        context['current_time'] = now.time()

        if not polling_schedule.is_voting_open():
            context['winners_by_halka'] = get_winners_by_halka()
    except PollingSchedule.DoesNotExist:
        pass
    return context

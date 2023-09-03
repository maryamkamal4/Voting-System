from datetime import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Sum
import pytz
from voting.models import PollingSchedule, Vote
from .models import CustomUser, Halka
from django.core.paginator import Paginator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)
        )

account_activation_token = TokenGenerator()


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


def get_polling_schedule_context(request):
    context = {}
    
    try:
        polling_schedule = PollingSchedule.objects.latest('start_datetime')
        context['polling_schedule'] = polling_schedule
        now = datetime.now(pytz.timezone('Asia/Karachi'))
        
        if not polling_schedule.is_voting_open():
            context['winners_by_halka'] = get_winners_by_halka()
            context['current_time'] = now.time()
            handle_search(context, request)
            handle_pagination(context, request)

    except PollingSchedule.DoesNotExist:
        pass
    
    return context


def handle_search(context, request):
    search_query = request.GET.get('search')
    if search_query:
        winners_by_halka = context['winners_by_halka']
        winners_by_halka = {halka: winner_info for halka, winner_info in winners_by_halka.items() if search_query.lower() in halka.name.lower()}
        context['search_query'] = search_query
        context['winners_by_halka'] = winners_by_halka
        
        
def handle_pagination(context, request):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(list(context['winners_by_halka'].items()), per_page=10)
    page = paginator.get_page(page_number)
    context['winners_paginated'] = page

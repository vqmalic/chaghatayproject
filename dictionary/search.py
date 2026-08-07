import re
from django.db.models import F, Q, Case, When, Value, OuterRef, Subquery, IntegerField
from django.db.models.functions import Greatest, Coalesce, Length
from django.db.models.fields import FloatField
from django.contrib.postgres.search import TrigramSimilarity

from .models import Entry, AlternateSpelling, Definition
from .utils import strip_diacritics

ARABIC_SCRIPT_RE = re.compile(r'[\u0600-\u06FF]')

def looks_like_persoarabic(query: str) -> bool:
    return bool(ARABIC_SCRIPT_RE.search(query))


def search_entries_by_definition(query: str, limit: int = 10):
    """English-to-Chaghatay: match against Definition.definition_text via
    icontains, then rank parent Entry rows by their shortest matching
    definition (a cheap proxy for closeness, since icontains gives no
    similarity score to rank on)."""
    best_match_len = (
        Definition.objects
        .filter(entry=OuterRef('pk'), definition_text__icontains=query)
        .annotate(match_len=Length('definition_text'))
        .order_by('match_len')
        .values('match_len')[:1]
    )

    qs = Entry.objects.annotate(
        match_len=Subquery(best_match_len, output_field=IntegerField()),
    ).filter(match_len__isnull=False).order_by('match_len')

    return qs[:limit]


def search_entries(query: str, limit: int = 10, mode: str = 'chag_to_eng'):
    if mode == 'eng_to_chag':
        return search_entries_by_definition(query, limit)

    if looks_like_persoarabic(query):
        # correlated subquery: does this entry have ANY alt spelling
        # matching the query? (existence only — no ranking needed here,
        # since we're doing substring match, not similarity scoring)
        alt_match = AlternateSpelling.objects.filter(
            entry=OuterRef('pk'),
            persoarabic__icontains=query,
        )

        qs = Entry.objects.filter(
            Q(persoarabic__icontains=query) | Q(pk__in=Subquery(alt_match.values('entry_id')))
        ).annotate(
            own_exact_prefix=Case(
                When(persoarabic__istartswith=query, then=0),
                default=1,
            )
        ).order_by('own_exact_prefix', 'persoarabic')

        return qs[:limit]

    stripped_query = strip_diacritics(query.lower())

    alt_best = (
        AlternateSpelling.objects
        .filter(entry=OuterRef('pk'))
        .annotate(
            sim=Greatest(
                TrigramSimilarity('latin_strict_stripped', stripped_query),
                TrigramSimilarity('latin_strict', query),
            )
        )
        .order_by('-sim')
        .values('sim')[:1]
    )

    qs = Entry.objects.annotate(
        sim_strict=TrigramSimilarity('latin_strict_stripped', stripped_query),
        sim_phonetic=TrigramSimilarity('latin_phonetic_stripped', stripped_query),
        sim_strict_exact=TrigramSimilarity('latin_strict', query),
        sim_phonetic_exact=TrigramSimilarity('latin_phonetic', query),
        alt_sim=Coalesce(
            Subquery(alt_best, output_field=FloatField()),
            Value(0.0),
        ),
        best_sim=Greatest(
            F('sim_strict'), F('sim_phonetic'),
            F('sim_strict_exact'), F('sim_phonetic_exact'),
            F('alt_sim'),
        ),
    ).filter(best_sim__gt=0.2).order_by('-best_sim')

    return qs[:limit]
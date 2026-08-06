import re
from django.db.models import F, Q, Case, When, Value, OuterRef, Subquery
from django.db.models.functions import Greatest, Coalesce
from django.db.models.fields import FloatField
from django.contrib.postgres.search import TrigramSimilarity

from .models import Entry, AlternateSpelling
from .utils import strip_diacritics

ARABIC_SCRIPT_RE = re.compile(r'[\u0600-\u06FF]')

def looks_like_persoarabic(query: str) -> bool:
    return bool(ARABIC_SCRIPT_RE.search(query))



def search_entries(query: str, limit: int = 10):
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
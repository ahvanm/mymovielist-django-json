from rest_framework.filters import OrderingFilter

class StableOrderingFilter(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)
        if ordering:
            # Add secondary sort for tiebreakers
            return list(ordering) + ['date_watched', 'movie_title']
        return ordering
from rest_framework.pagination import PageNumberPagination

from utils.envelope import Envelope


class ListingPageNumberPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, serialized_data):
        return Envelope.success_response(
            data={
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": serialized_data,
            }
        )

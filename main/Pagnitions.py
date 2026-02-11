from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class DefaultPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)

        return Response({
            "pagination": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total": self.page.paginator.count,
                "page_size": self.page_size,
                "current_page_number": self.page.number,
                "total_pages": total_pages
            },
            "data": data
        })

class GroupPaginatsion(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)

        return Response({
            "pagination": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total": self.page.paginator.count,
                "page_size": self.page_size,
                "current_page_number": self.page.number,
                "total_pages": total_pages
            },
            "data": data
        })


class PublicationHome(DefaultPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)

        return Response({
            "pagination": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total": self.page.paginator.count,
                "page_size": self.page_size,
                "current_page_number": self.page.number,
                "total_pages": total_pages
            },
            "data": data
        })

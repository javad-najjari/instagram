from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



class HomePagination(PageNumberPagination):

    page_size = 3

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class GlobalPagination(PageNumberPagination):

    page_size = 15

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


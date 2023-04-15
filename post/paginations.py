from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



class PaginateBy5(PageNumberPagination):

    page_size = 5

    def get_paginated_response(self, data):
        domain = self.request.META['HTTP_HOST']
        next = self.get_next_link().split(domain)[1]

        return Response({
            'next': next,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class PaginateBy15(PageNumberPagination):

    page_size = 15

    def get_paginated_response(self, data):
        domain = self.request.META['HTTP_HOST']
        next = self.get_next_link().split(domain)[1]

        return Response({
            'next': next,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


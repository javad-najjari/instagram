from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from urllib.parse import urlparse



class PaginateBy5(PageNumberPagination):

    page_size = 5

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        if next_link:
            parsed_url = urlparse(next_link)
            next = parsed_url.path + '?' + parsed_url.query
        else:
            next = None
        
        return Response({
            'next': next,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })



class PaginateBy6(PageNumberPagination):

    page_size = 6

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        if next_link:
            parsed_url = urlparse(next_link)
            next = parsed_url.path + '?' + parsed_url.query
        else:
            next = None

        return Response({
            'next': next,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })



class PaginateBy10(PageNumberPagination):

    page_size = 10

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        if next_link:
            parsed_url = urlparse(next_link)
            next = parsed_url.path + '?' + parsed_url.query
        else:
            next = None

        return Response({
            'next': next,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })



class PaginateBy15(PageNumberPagination):

    page_size = 15

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        if next_link:
            parsed_url = urlparse(next_link)
            next = parsed_url.path + '?' + parsed_url.query
        else:
            next = None

        return Response({
            'next': next,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


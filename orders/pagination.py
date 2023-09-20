from rest_framework import pagination


class OrderCustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000000
    page_query_param = 'page'
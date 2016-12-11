from gru.config import settings


class Paginator(object):
    """
    Perform basic calculation of pagination and ranges.
    """
    def __init__(self, current_page, page_size=None):
        if page_size is None:
            self.page_size = settings.get('ui.items_per_page', 50)
        else:
            self.page_size = page_size
        self.current_page = current_page

    def serialize(self, total_results):
        return {
            'page_size': self.page_size,
            'current_page': self.current_page,
            'next_page': self.next(total_results),
            'previous_page': self.previous(total_results),
            'total_pages': self.total_pages(total_results)
        }

    def next(self, total_results):
        from_ind, to_ind = self.result_range()
        if to_ind < total_results:
            return self.current_page + 1
        return None

    def previous(self, total_results):
        from_ind, to_ind = self.result_range()
        if from_ind > 0:
            return self.current_page - 1
        return None

    def result_range(self):
        from_ind = (self.current_page - 1) * self.page_size
        to_ind = self.current_page * self.page_size
        return from_ind, to_ind

    def page_kwargs(self):
        from_ind, to_ind = self.result_range()
        return {'from_ind': from_ind, 'to_ind': to_ind}

    def total_pages(self, total_results):
        base = total_results / self.page_size
        if total_results % self.page_size > 0:
            base += 1
        return base

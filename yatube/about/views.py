from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_title'] = 'About author'
        context['author_links'] = 'GitHub - https://github.com/Ascurse'
        context['author_me'] = 'Maximilian, 24yo male'
        context['author_info'] = 'Currently learning Python!'
        return context


class Technologies(TemplateView):
    template_name = 'about/tech.html'

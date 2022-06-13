from django.forms.widgets import Widget

class PlusMinusNumberInput(Widget):
    template_name = 'widget/plusminusnumber.html'
    class Media:
        css = {'All':('css/plusminusnumber.css',)}
        js = ('js/plusminusnumber.js',)